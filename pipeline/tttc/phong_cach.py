"""Kiểm phong cách kịch bản theo kênh mẫu (docs/phong-cach-kich-ban.md). Chỉ trả cảnh báo, không chặn."""
import json
import re
import statistics
import sys
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
    return out + mui_may(script_md) + tu_cam(script_md) + nhip(script_md)


CONFIG = Path(__file__).resolve().parent.parent / "config.json"
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
    n = len(RAO_DON.findall(text))
    if n > 3:
        out.append(f"Cảnh báo: {n} câu rào đón ('mình nghĩ', 'bạn tự xem'...), tối đa 3; hãy nêu phán xét kèm tiêu chí")
    if len(sents) >= 20:
        ngan = sum(len(x.split()) <= 5 for x in sents) / len(sents)
        if ngan < 0.10:
            out.append(f"Cảnh báo: chỉ {ngan:.0%} câu ngắn (≤ 5 từ), cần ≥ 10% để nhịp đọc không đều đều")
    if sum(bool(LIET_KE.match(x)) for x in sents[-6:]) >= 2:
        out.append("Cảnh báo: phần kết nhai lại bằng 'Một... Hai... Ba...'; kết bằng phán quyết, điều kiện đổi ý và câu mời đoán")
    return out


# Ngưỡng đặt dưới mốc nền của hai kịch bản đã duyệt (docs/superpowers/specs/2026-11-09-giong-van-kich-ban-design.md 3.4).
NHIP = {"cv_min": 0.5, "chuoi_max": 4, "dai_tu": 28, "dai_max": 8, "cam_than_max": 5, "dem_max": 15,
        "toi_thieu_cau": 20}
CAM_THAN = re.compile(r"\b(?:rất|vô cùng|cực kỳ|khổng lồ|đáng kinh ngạc|choáng)\b", re.I)
TU_DEM = re.compile(r"kiểu như|nói thật là|đoạn này mới cấn|tính ra thì", re.I)
TRAI_NGHIEM = re.compile(r"\b(?:mình từng|hồi mình|có lần mình|tôi từng)\b", re.I)


def nhip(script_md: str) -> list[str]:
    """Cảnh báo nhịp câu, từ đệm, tính từ cảm thán và trải nghiệm cá nhân bịa; không chặn."""
    text = " ".join(tts.spoken_paragraphs(script_md))
    if not text.strip():
        return []
    out = []
    sents = [x.strip() for x in re.split(r"(?<=[.!?…])\s+", text) if x.strip()]
    if len(sents) >= NHIP["toi_thieu_cau"]:  # thống kê chỉ có nghĩa khi đủ câu
        dai = [len(x.split()) for x in sents]
        cv = statistics.pstdev(dai) / statistics.mean(dai)
        if cv < NHIP["cv_min"]:
            out.append(f"Cảnh báo: độ lệch chuẩn/trung bình độ dài câu {cv:.2f}, cần ≥ {NHIP['cv_min']} (nhịp quá đều)")
        best = run = 1
        base = dai[0]
        for n in dai[1:]:  # chuỗi câu có độ dài trong ±20% so với câu đầu chuỗi
            run, base = (run + 1, base) if abs(n - base) <= 0.2 * base else (1, n)
            best = max(best, run)
        if best > NHIP["chuoi_max"]:
            out.append(f"Cảnh báo: {best} câu liền cùng độ dài (tối đa {NHIP['chuoi_max']})")
        so_dai = sum(n > NHIP["dai_tu"] for n in dai)
        if so_dai > NHIP["dai_max"]:
            out.append(f"Cảnh báo: {so_dai} câu dài hơn {NHIP['dai_tu']} từ, khó đọc to (tối đa {NHIP['dai_max']})")
    cam = len(CAM_THAN.findall(text))
    if cam > NHIP["cam_than_max"]:
        out.append(f"Cảnh báo: {cam} tính từ cảm thán (rất, vô cùng...), tối đa {NHIP['cam_than_max']}; dùng số liệu cụ thể")
    dem = len(TU_DEM.findall(text))
    if dem > NHIP["dem_max"]:
        out.append(f"Cảnh báo: {dem} từ đệm, tối đa {NHIP['dem_max']}")
    out += [f"Cảnh báo: cụm kể trải nghiệm cá nhân «{m.group(0)}», kênh tin tức không được bịa trải nghiệm"
            for m in TRAI_NGHIEM.finditer(text)]
    return out


def uoc_tinh_phut(script_md: str, wpm: float) -> float:
    """Số phút đọc ước tính = số từ lời đọc (không tính thẻ [#id]) / tốc độ đọc từ-phút."""
    return len(_split(script_md)[1]) / wpm


def main(video_dir: str) -> int:
    script = (Path(video_dir) / "kich-ban.md").read_text(encoding="utf-8")
    msgs = kiem(script)
    wpm = json.loads(CONFIG.read_text(encoding="utf-8")).get("vieneu", {}).get("wpm_du_kien") if CONFIG.exists() else None
    if wpm:
        print(f"ước tính {uoc_tinh_phut(script, wpm):.1f} phút ở {wpm:.0f} từ/phút (config vieneu.wpm_du_kien)")
    for m in msgs:
        print("-", m)
    loi = sum(m.startswith("Lỗi") for m in msgs)
    print(f"{loi} Lỗi, {len(msgs) - loi} cảnh báo")
    return 1 if loi else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
