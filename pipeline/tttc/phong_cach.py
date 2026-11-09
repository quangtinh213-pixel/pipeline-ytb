"""Kiểm phong cách kịch bản theo kênh mẫu (docs/phong-cach-kich-ban.md). Chỉ trả cảnh báo, không chặn."""
import re

from tttc import tts

HEAD, TAIL, MIN_TU, MAX_TU = 90, 60, 2000, 2600  # 10–13 phút ở ~200 từ/phút


def _split(script_md: str) -> tuple[list[str], list[str]]:
    """(các token kể cả thẻ [#id], các từ không tính thẻ) của phần lời đọc."""
    toks = " ".join(tts.spoken_paragraphs(script_md, keep_tags=True)).split()
    return toks, [t for t in toks if not tts.TAG.fullmatch(t)]


def kiem(script_md: str) -> list[str]:
    toks, words = _split(script_md)
    if not words:  # kịch bản chưa có phần "Lời đọc": việc của bước TTS, không phải của kiểm phong cách
        return []
    out, seen, head = [], 0, []
    for t in toks:
        head.append(t)
        seen += not tts.TAG.fullmatch(t)
        if seen >= HEAD:
            break
    head_text = " ".join(head)
    if not tts.TAG.search(head_text):
        out.append(f"Cảnh báo: {HEAD} từ đầu chưa có con số có nguồn ([#id]); mở bằng sự kiện kèm con số gây tò mò")
    if "?" not in head_text:
        out.append(f"Cảnh báo: {HEAD} từ đầu chưa có câu hỏi hứa trả lời")
    if "?" not in " ".join(words[-TAIL:]):
        out.append(f"Cảnh báo: {TAIL} từ cuối chưa có câu hỏi mời người xem bình luận")
    if not MIN_TU <= len(words) <= MAX_TU:
        out.append(f"Cảnh báo: lời đọc {len(words)} từ, khung {MIN_TU}–{MAX_TU} từ (10–13 phút)")
    return out + mui_may(script_md)


# Cụm nghe như dịch thô từ tiếng Anh hoặc chuyển đoạn lười; danh sách tổng quát, không gắn riêng một kịch bản.
DICH_THO = ("hãy nhìn đúng", "như các bạn đã biết", "không thể phủ nhận", "trong thế giới ngày nay",
            "hãy cùng nhau", "tóm lại bằng", "điều quan trọng cần lưu ý", "chúng ta sẽ cùng")
RAO_DON = re.compile(r"mình nghĩ|mình cho rằng|tùy bạn|bạn tự (?:xem|thử|kiểm)", re.I)
BO_BA = re.compile(r"^(?:Ba|Thứ ba)\s*,")
LIET_KE = re.compile(r"^(?:Một|Hai|Ba|Thứ (?:nhất|hai|ba))\s*,")


def mui_may(script_md: str) -> list[str]:
    """Cảnh báo giọng văn nghe như máy viết (docs/phong-cach-kich-ban.md mục 'Chống mùi máy'); không chặn."""
    text = " ".join(tts.spoken_paragraphs(script_md))
    if not text.strip():
        return []
    sents = [x.strip() for x in re.split(r"(?<=[.!?…])\s+", text) if x.strip()]
    out = []
    ba = sum(bool(BO_BA.match(x)) for x in sents)
    if ba > 1:
        out.append(f"Cảnh báo: {ba} lần đếm kiểu bộ ba 'Một... Hai... Ba...' (tối đa 1 lần mỗi video); gom ý bằng mạch kể")
    low = text.lower()
    out += [f"Cảnh báo: cụm nghe như dịch thô từ tiếng Anh: «{p}»" for p in DICH_THO if p in low]
    n = len(RAO_DON.findall(text))
    if n > 3:
        out.append(f"Cảnh báo: {n} câu rào đón ('mình nghĩ', 'bạn tự xem'...), tối đa 3; hãy nêu phán xét kèm tiêu chí")
    if len(sents) >= 20:
        ngan = sum(len(x.split()) <= 5 for x in sents) / len(sents)
        if ngan < 0.10:
            out.append(f"Cảnh báo: chỉ {ngan:.0%} câu ngắn (≤ 5 từ), cần ≥ 10% để nhịp đọc không đều đều")
    if sum(bool(LIET_KE.match(x)) for x in sents[-6:]) >= 2:
        out.append("Cảnh báo: phần kết nhai lại bằng 'Một... Hai... Ba...'; kết bằng phán quyết, điều kiện đổi ý và câu mời đoán")
    if "đổi ý" not in low:
        out.append("Cảnh báo: chưa có điều kiện đổi ý ('mình sẽ đổi ý nếu...') đi kèm phán quyết")
    return out
