"""Kiểm phong cách kịch bản theo kênh mẫu (docs/phong-cach-kich-ban.md). Chỉ trả cảnh báo, không chặn."""
from tttc import tts

HEAD, TAIL, MIN_TU, MAX_TU = 90, 60, 1500, 1900


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
    return out
