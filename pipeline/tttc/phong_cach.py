"""Kiểm phong cách kịch bản theo kênh mẫu (docs/phong-cach-kich-ban.md). Chỉ trả cảnh báo, không chặn."""
import json
import re
import statistics
import sys
from pathlib import Path

from tttc import kiem as kiem_so, tts

HEAD, TAIL, MIN_TU, MAX_TU = 90, 60, 2000, 2600  # 10–13 phút ở ~200 từ/phút
# Bộ template theo loại tin (docs/template-kich-ban.md, mục 10 thẻ phong cách, user chốt 11/11/2026): khung từ theo
# thời lượng template ở ~200 từ/phút. cap-nhat: template không ghi thời lượng, 1:30–3:00 là giả định.
LOAI = {"ra-mat": (500, 800), "ro-ri": (300, 500), "gia": (250, 400), "bao-mat": (400, 700),
        "ai": (500, 800), "cap-nhat": (300, 600), "shorts": (100, 200)}
LOAI_DONG = re.compile(r"^\s*\**Loại:?\**:?\s*([a-z-]+)\s*$", re.I | re.M)


def loai_cua(script_md: str) -> str | None:
    """Khóa loại template ở dòng `Loại: <khóa>` đầu kịch bản (None nếu không có: video dài theo mục 3)."""
    m = LOAI_DONG.search(script_md)
    return m.group(1).lower() if m else None


def _split(script_md: str) -> tuple[list[str], list[str]]:
    """(các token kể cả thẻ [#id], các từ không tính thẻ) của phần lời đọc."""
    toks = " ".join(tts.spoken_paragraphs(script_md, keep_tags=True)).split()
    return toks, [t for t in toks if not tts.TAG.fullmatch(t)]


def kiem_hanh_chinh(text: str) -> list[str]:
    """Cảnh báo văn phong hành chính/công văn khô khan trong lời đọc."""
    pat = re.compile(r"\b(?:thông tư số|nghị định số|quyết định số|công văn số|văn bản số|cơ quan chủ trì|nhiệm vụ nghiên cứu|báo cáo đề tài)\b", re.I)
    matches = pat.findall(text)
    if matches:
        return [f"Cảnh báo văn phong hành chính khô khan: phát hiện cụm «{', '.join(set(matches))}» trong lời đọc. Khuyến nghị dịch sang ngôn ngữ nói (số văn bản đưa lên màn hình)."]
    return []


def kiem(script_md: str, check_cta: bool = False, check_dai_chung: bool = False) -> list[str]:
    toks, words = _split(script_md)
    if not words:  # kịch bản chưa có phần "Lời đọc": việc của bước TTS, không phải của kiểm phong cách
        return []
    loai = loai_cua(script_md)
    if loai is not None:
        if loai not in LOAI:
            return [f"Lỗi: loại «{loai}» không có trong bộ template ({', '.join(LOAI)})"]
        lo, hi = LOAI[loai]
        out = [] if lo <= len(words) <= hi else [f"Cảnh báo: lời đọc {len(words)} từ, loại {loai} khung {lo}–{hi} từ"]
        if check_cta and not any(k in " ".join(words).lower() for k in ["đăng ký", "theo dõi", "subscribe", "bấm chuông", "video liên kết", "link bên dưới"]):
            out.append("Cảnh báo: Kịch bản chưa có lời kêu gọi Đăng Ký kênh (CTA) hoặc link chuyển tiếp Shorts")
        if check_dai_chung:
            out += kiem_hanh_chinh(" ".join(words))
        return out + mui_may(script_md) + tu_cam(script_md) + nhip(script_md)  # hook, kết do template quy định
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
    if check_cta and not any(k in " ".join(words).lower() for k in ["đăng ký", "theo dõi", "subscribe", "bấm chuông"]):
        out.append("Cảnh báo: Kịch bản chưa có lời kêu gọi Đăng Ký kênh (CTA) - nguy cơ mất chuyển đổi subscriber")
    if check_dai_chung:
        out += kiem_hanh_chinh(" ".join(words))
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

SO_MOI_DOAN, SO_LE_MAX = 4, 2  # 4: mốc nền kịch bản máy cũ đã duyệt
SO_LE = re.compile(r"\bphẩy\b|\d,\d")


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
    # user 11/11/2026: tai không giữ nổi nhiều số; số lẻ chính xác để lên hình, lời đọc dùng số tròn
    for p in tts.spoken_paragraphs(script_md):
        so = kiem_so._claims(kiem_so.DATE_TIME.sub(" ", kiem_so.TAG.sub(" ", p)))
        if len(so) > SO_MOI_DOAN:
            out.append(f"Cảnh báo: đoạn có {len(so)} con số (tối đa {SO_MOI_DOAN}), tai không theo kịp; "
                       f"giữ số chính, số còn lại đưa lên hình: «{p[:50]}…»")
    le = len(SO_LE.findall(text))
    if le > SO_LE_MAX:
        out.append(f"Cảnh báo: {le} số lẻ đọc thành tiếng ('… phẩy …'), tối đa {SO_LE_MAX}; "
                   "đọc số tròn kèm 'gần', 'khoảng', số chính xác để lên hình")
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


# Luật 40 giây đầu (15/11/2026, docs/nghien-cuu/de-xuat-phat-trien-2026-11-15.md mục 1.3). Ba video có đường giữ chân
# mất ~1/3 người xem trước giây 49, rơi mạnh đúng ở câu nói về việc đọc tài liệu ("chi tiết lạ", "một dòng nhỏ") và khi
# mở nhiều câu hỏi cùng lúc; đối thủ kể thẳng: mốc giờ, sự kiện, số, một người Việt hoặc giá cụ thể, rồi một câu hỏi.
# Chỉ cảnh báo (không chặn duyệt 1); không gộp vào kiem() để mốc nền giọng văn cũ vẫn so được.
MO_DAU_GIAY, KHOP_GIAY = 40, 15
MOC_THOI_GIAN = re.compile(
    r"\b(?:ngày|tháng)\s+\w+|\bthứ (?:hai|ba|tư|năm|sáu|bảy)\b|\bchủ nhật\b|\b(?:sáng|trưa|chiều|tối|đêm|rạng sáng)\b"
    r"|\bhôm (?:qua|nay|kia)\b|\btuần (?:này|trước|qua)\b|\bnăm (?:ngoái|nay)\b|\b\d{1,2}/\d{1,2}\b|\bgiờ (?:việt nam|hà nội)\b",
    re.I)
NEO_VIET_NAM = re.compile(
    r"(?<!cộng )\bđồng\b|\bngười việt\b|\b(?:hà nội|tp hcm|thành phố hồ chí minh|sài gòn|đà nẵng|huế|cần thơ|hải phòng)\b"
    r"|\bmột (?:nhân viên|lập trình viên|tài xế|người bán|chủ tiệm|sinh viên|kỹ sư|giáo viên|công nhân)\b", re.I)
# Thực thể quá chung để coi là "đã nhắc chủ thể của tiêu đề"
THUC_THE_CHUNG = {r"\bai\b", r"\bchip\b", r"\bbán dẫn\b", r"\bthông tư\b", r"\bnghị định\b", r"\bram\b", r"\bssd\b",
                  r"\bcrypto\b"}


def _wpm(wpm: float | None) -> float:
    if wpm:
        return float(wpm)
    cfg = json.loads(CONFIG.read_text(encoding="utf-8")) if CONFIG.exists() else {}
    return float(cfg.get("vieneu", {}).get("wpm_du_kien") or 249)


def _dau(script_md: str, giay: float, wpm: float | None) -> str:
    """Lời đọc (giữ thẻ [#id]) trong `giay` giây đầu, ước theo số từ ở tốc độ wpm."""
    n, seen, out = int(_wpm(wpm) * giay / 60), 0, []
    for t in " ".join(tts.spoken_paragraphs(script_md, keep_tags=True)).split():
        if seen >= n:
            break
        out.append(t)
        seen += not tts.TAG.fullmatch(t)
    return " ".join(out)


def kiem_mo_dau(script_md: str, wpm: float | None = None) -> list[str]:
    """Cảnh báo cho 40 giây đầu của video dài: lời nói về việc kể chuyện, > 1 câu hỏi, thiếu mốc thời gian/neo Việt Nam."""
    if loai_cua(script_md) is not None:
        return []  # template ngắn có hook riêng
    dau = _dau(script_md, MO_DAU_GIAY, wpm)
    if not dau.strip():
        return []
    low, cam, out = dau.lower(), json.loads(TU_CAM.read_text(encoding="utf-8")), []
    meta = [p for p in cam.get("mo_dau", []) if p in low]
    if meta:
        out.append(f"Cảnh báo: {MO_DAU_GIAY} giây đầu nói về việc kể chuyện («{'», «'.join(meta)}») – kể thẳng sự kiện; "
                   "người xem rơi mạnh đúng ở những câu này")
    cau_hoi = [x.strip() for x in re.findall(r"[^.!?…]*\?", tts.TAG.sub("", dau))]
    if len(cau_hoi) > 1:
        out.append(f"Cảnh báo: {MO_DAU_GIAY} giây đầu có {len(cau_hoi)} câu hỏi ({' '.join(cau_hoi)}) – "
                   "chỉ treo một câu hỏi, kể chuyện để dẫn tới nó")
    if not MOC_THOI_GIAN.search(low):
        out.append(f"Cảnh báo: {MO_DAU_GIAY} giây đầu thiếu mốc thời gian (ngày, thứ, sáng/tối, giờ Việt Nam)")
    if not NEO_VIET_NAM.search(low):
        out.append(f"Cảnh báo: {MO_DAU_GIAY} giây đầu thiếu neo cụ thể cho người Việt (một người Việt, một nơi, một giá bằng đồng)")
    return out


def kiem_khop_tieu_de(script_md: str, tieu_de: str, wpm: float | None = None) -> list[str]:
    """Cảnh báo khi chủ thể hoặc con số của tiêu đề chưa xuất hiện trong 15 giây đầu (tiêu đề hứa một đằng, mở đầu nói một nẻo)."""
    from tttc import tieu_de as td
    dau = tts.TAG.sub("", _dau(script_md, KHOP_GIAY, wpm))
    if not dau.strip() or not tieu_de.strip():
        return []
    gon = lambda x: " ".join(x.lower().replace("-", " ").split())
    out, low = [], gon(dau)
    cfg = json.loads(CONFIG.read_text(encoding="utf-8")) if CONFIG.exists() else {}
    phat_am = {gon(k): gon(v) for k, v in cfg.get("vieneu", {}).get("phat_am", {}).items()}  # lời đọc hay viết theo phiên âm
    rieng = [m.group(0) for pat in td.THUC_THE if pat not in THUC_THE_CHUNG and (m := re.search(pat, tieu_de, re.I))]
    cach_viet = {f for e in rieng for f in (gon(e), phat_am.get(gon(e))) if f}
    if rieng and not any(re.search(rf"\b{re.escape(f)}\b", low) for f in cach_viet):
        out.append(f"Cảnh báo: tiêu đề nhắc «{', '.join(dict.fromkeys(rieng))}» nhưng {KHOP_GIAY} giây đầu chưa nói tới")
    co = {v for _, v, _ in kiem_so._claims(dau)}
    for raw, v, _ in kiem_so._claims(tieu_de):
        if v not in co:
            out.append(f"Cảnh báo: tiêu đề có số «{raw}» nhưng {KHOP_GIAY} giây đầu chưa nói tới")
    return out


def kiem_loai_bai_chinh(script_md: str) -> list[str]:
    """Cảnh báo nếu kịch bản video chính bị gắn thẻ 'Loại:' của template ngắn."""
    loai = loai_cua(script_md)
    if loai is None or loai == "shorts":
        return []
    return [f"Cảnh báo: Kịch bản video chính đang gắn 'Loại: {loai}' (chỉ dành cho clip phụ/template ngắn); "
            f"bài hằng ngày cần bỏ dòng Loại: và viết đủ {MIN_TU:,}–{MAX_TU:,} từ (~8–13 phút).".replace(",", ".")]


def kiem_thoi_luong_thuc(script_md: str, wpm: float = 249, min_phut: float = 7.5) -> list[str]:
    """Cảnh báo nếu video dài (không phải clip ngắn/Shorts theo template) có thời lượng thực tế dưới ngưỡng tối thiểu."""
    _, words = _split(script_md)
    if not words or loai_cua(script_md) is not None:
        return []
    phut = len(words) / wpm
    if phut < min_phut:
        return [f"Cảnh báo thời lượng: Video dài ước tính chỉ {phut:.1f} phút ở tốc độ {wpm:.0f} từ/phút "
                f"(dưới ngưỡng {min_phut:.1f} phút; cần mở rộng phân tích tới ~2.000–2.600 từ)."]
    return []


# Short dọc gốc (docs/superpowers/specs/2026-11-15-shorts-doc-goc-design.md mục 4.2): Shorts cũ chỉ giữ 9,6–18,9% người
# lướt tới; bản cắt từ giữa video dài mở bằng "Thứ nhất,". Câu nói đầu tiên phải là câu hook có con số gắn nguồn.
SHORT_GIAY, CAU_DAU_MAX_TU = (30, 55), 22
TU_NOI_DAU = ("thứ nhất", "còn", "vậy", "và", "nhưng", "tiếp theo", "ngoài ra")
NOI_VE_KE = re.compile(r"mình đọc lại|chi tiết lạ|một dòng nhỏ|ít ai đọc|video trước|dưới mô tả|đường dẫn", re.I)


def kiem_short(script_md: str, wpm: float = 237) -> list[str]:
    """Lỗi và cảnh báo của kịch bản Short viết riêng: thời lượng 30–55 giây, câu đầu là hook có số gắn [#id]."""
    from tttc import tieu_de as td
    from tttc.giong_vieneu import cau
    cac_cau = []
    for c in (c for p in tts.spoken_paragraphs(script_md, keep_tags=True) for c in cau(p)):
        the = re.match(r"(?:\s*\[#[\w-]+\])+", c)  # "… mười. [#v1] Câu sau": thẻ thuộc câu đứng trước
        if the and cac_cau:
            cac_cau[-1] += the.group(0)
            c = c[the.end():].strip()
        if c:
            cac_cau.append(c)
    if not cac_cau:
        return ["Lỗi: kịch bản Short chưa có phần lời đọc"]
    out, dau = [], cac_cau[0]
    giay = uoc_tinh_phut(script_md, wpm) * 60
    if not SHORT_GIAY[0] <= giay <= SHORT_GIAY[1]:
        out.append(f"Lỗi: Short ước {giay:.0f} giây ở {wpm:.0f} từ/phút (cho phép {SHORT_GIAY[0]}–{SHORT_GIAY[1]} giây)")
    dau_sach = tts.TAG.sub("", dau).strip()
    noi = next((t for t in TU_NOI_DAU if re.match(rf"{t}(?!\w)", dau_sach.lower())), None)
    if noi:
        out.append(f"Lỗi: câu đầu mở bằng từ nối «{noi}» – câu nói đầu tiên của Short phải là câu hook tự đứng được")
    if not tts.TAG.search(dau):
        out.append("Lỗi: câu đầu chưa có con số gắn nguồn [#id]")
    if len(dau_sach.split()) > CAU_DAU_MAX_TU:
        out.append(f"Cảnh báo: câu đầu dài {len(dau_sach.split())} từ (nên ≤ {CAU_DAU_MAX_TU})")
    if " ".join(cac_cau[:2]).count("?") > 1:
        out.append("Cảnh báo: hai câu đầu có hơn một câu hỏi – chỉ treo một câu hỏi")
    text = tts.TAG.sub("", " ".join(cac_cau))
    out += [f"Cảnh báo: lời nói về việc kể chuyện hoặc trỏ đi chỗ khác «{m}»"
            for m in dict.fromkeys(x.group(0).lower() for x in NOI_VE_KE.finditer(text))]
    giat = [m.group(0) for pat in td.TU_GIAT_GAN for m in re.finditer(pat, text.lower())]
    if giat:
        out.append(f"Lỗi: từ giật gân ({', '.join(dict.fromkeys(giat))}) – nói thẳng sự kiện và con số")
    if "!" in text:
        out.append("Lỗi: có dấu chấm than trong lời đọc")
    return out


def main(video_dir: str) -> int:
    script = (Path(video_dir) / "kich-ban.md").read_text(encoding="utf-8")
    msgs = kiem(script, check_cta=True, check_dai_chung=True) + kiem_loai_bai_chinh(script)
    wpm = json.loads(CONFIG.read_text(encoding="utf-8")).get("vieneu", {}).get("wpm_du_kien") if CONFIG.exists() else None
    if wpm:
        print(f"ước tính {uoc_tinh_phut(script, wpm):.1f} phút ở {wpm:.0f} từ/phút (config vieneu.wpm_du_kien)")
        msgs += kiem_thoi_luong_thuc(script, wpm=wpm)
    msgs += kiem_mo_dau(script, wpm=wpm)
    for m in msgs:
        print("-", m)
    loi = sum(m.startswith("Lỗi") for m in msgs)
    print(f"{loi} Lỗi, {len(msgs) - loi} cảnh báo")
    return 1 if loi else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
