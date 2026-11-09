"""Kiểm phong cách kịch bản theo kênh mẫu (docs/phong-cach-kich-ban.md). Chỉ trả cảnh báo, không chặn."""
import json
import re
from pathlib import Path

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


TU_CAM = Path(__file__).resolve().parent.parent / "phong-cach" / "tu-cam.json"
QUOTED = re.compile(r'"[^"]*"|“[^”]*”')  # chữ trích nguyên văn từ nguồn được miễn khỏi danh sách cấm
RAO_DON = re.compile(r"mình nghĩ|mình cho rằng|tùy bạn|bạn tự (?:xem|thử|kiểm)", re.I)
BO_BA = re.compile(r"^(?:Ba|Thứ ba)\s*,")
LIET_KE = re.compile(r"^(?:Một|Hai|Ba|Thứ (?:nhất|hai|ba))\s*,")


def tu_cam(script_md: str, path: Path = TU_CAM) -> list[str]:
    """Lỗi cứng theo phong-cach/tu-cam.json: từ/cụm cấm, mở bài và kết bài sáo rỗng, cụm dịch thô."""
    text = QUOTED.sub(" ", " ".join(tts.spoken_paragraphs(script_md)))
    if not text.strip():
        return []
    low, cam, out = text.lower(), json.loads(Path(path).read_text(encoding="utf-8")), []
    ctx = lambda i: " ".join(text[max(0, i - 20):i + 50].split())
    for p in cam["tu"]:
        if p in low:
            out.append(f"Lỗi: từ cấm «{p}»: …{ctx(low.index(p))}…")
    for pat in cam["mau"]:
        if m := re.search(pat, low):
            out.append(f"Lỗi: từ cấm «{m.group(0)}»: …{ctx(m.start())}…")
    head, tail = " ".join(low.split()[:40]), " ".join(low.split()[-60:])
    out += [f"Lỗi: mở bài sáo rỗng «{p}»" for p in cam["mo_bai"] if p in head]
    out += [f"Lỗi: kết bài đúc kết đạo lý «{p}»" for p in cam["ket_bai"] if p in tail]
    out += [f"Lỗi: cụm nghe như dịch thô từ tiếng Anh: «{p}»" for p in cam["dich_tho"] if p in low]
    return out


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
