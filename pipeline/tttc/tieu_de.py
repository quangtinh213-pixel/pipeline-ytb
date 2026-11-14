"""Kiểm tra (linter) và chấm điểm tiêu đề video YouTube.

Luật 15/11/2026 (docs/nghien-cuu/de-xuat-phat-trien-2026-11-15.md mục 1.1), rút từ số của kênh và đối thủ:
tiêu đề "SỐC…!" được 27 view, "Sự thật vụ…!" 0–2 view; tiêu đề thắng của đối thủ có dạng
`[sự kiện cụ thể có số]: [một câu hỏi Việt Nam/túi tiền]?`, không chấm than.

Lỗi (chặn hợp lệ): rỗng, > 100 ký tự, có < >, từ giật gân, dấu "!", hai móc chồng nhau, chữ in hoa cả từ tiếng Việt.
Cảnh báo (trừ điểm): thiếu con số, thiếu góc Việt Nam/túi tiền, phần trước ":" thiếu thực thể, không theo dạng "…: …?".
"""

import re
from typing import NamedTuple

# 1. Từ giật gân: bị cấm ở mọi vị trí (thị trường đang ngập kênh tin tự động dùng đúng các từ này)
TU_GIAT_GAN = [
    r"\bsốc\b", r"\bchấn động\b", r"\bkhẩn cấp\b", r"\bbất ngờ\b", r"\bsự thật\b", r"\blật tẩy\b",
    r"\bthảm họa\b", r"\bgây bão\b", r"\brúng động\b", r"\bkhông thể tin\b",
]
# Nhãn mở đầu kiểu bản tin tự động ("CẢNH BÁO: …", "NÓNG: …"); "Microsoft cảnh báo …" thì vẫn được
NHAN_MO_DAU = re.compile(r"^\s*(?:cảnh báo|nóng|khẩn|tin nóng)\s*[:!\-–]", re.I)
# Nhãn in hoa bất kỳ trước dấu ":" đầu tiên ("NGUY CƠ:", "BẤT NGỜ:") cũng là nhãn bản tin tự động
NHAN_IN_HOA = re.compile(r"^\s*([^:]{2,20}?)\s*:(?=\s)")
HAI_CHAM = re.compile(r":(?=\s|$)")  # chỉ dấu ":" tách vế; "15:30", "D:1" không tính

# 2. Thực thể lớn, thương hiệu, nhân vật công nghệ
THUC_THE = [
    r"\bnvidia\b", r"\bapple\b", r"\bgrab\b", r"\bvinfast\b", r"\biphone\b",
    r"\bjensen huang\b", r"\belon musk\b", r"\bmusk\b", r"\bsam altman\b",
    r"\bviettel\b", r"\bfpt\b", r"\bgoogle\b", r"\bmicrosoft\b", r"\bopenai\b",
    r"\bdeepseek\b", r"\btsmc\b", r"\bintel\b", r"\bbyd\b", r"\bbinance\b",
    r"\bcrypto\b", r"\bai\b", r"\bmacbook\b", r"\bchatgpt\b", r"\bgemini\b",
    r"\bbán dẫn\b", r"\bchip\b", r"\btesla\b", r"\btiktok\b", r"\byoutube\b",
    r"\bqualcomm\b", r"\bamd\b", r"\bsamsung\b", r"\bhollywood\b", r"\bnetflix\b", r"\bfmovies\b",
    r"\boutlook\b", r"\bmicrosoft 365\b", r"\bcopilot\b", r"\bclaude\b", r"\banthropic\b",
    r"\b7-zip\b", r"\b7zip\b", r"\bthông tư\b", r"\bnghị định\b", r"\bvietcombank\b",
    r"\bmomo\b", r"\bzalo\b", r"\bshopee\b", r"\bram\b", r"\bssd\b", r"\bwindows\b"
]

# 3. Góc Việt Nam / túi tiền / đời sống người xem
GOC_VIET_NAM = [
    r"\bviệt nam\b", r"\bngười việt\b", r"\btiền túi\b", r"\btúi tiền\b",
    r"\bngười dùng\b", r"\bgiá tăng\b", r"\bđắt hơn\b", r"\bgiảm giá\b",
    r"\bôm nợ\b", r"\bmất tiền\b", r"\bhết cửa\b", r"\bchịu trận\b",
    r"\bhàng việt\b", r"\bcước\b", r"\bthuế\b", r"\blời hứa\b",
    r"\bmua máy\b", r"\bngười mua\b", r"\bdân buôn\b", r"\btiết kiệm\b",
    r"\blãng phí\b", r"\blương\b", r"\bmất việc\b", r"\btúi ai\b",
    r"\bgiá\b", r"\bphí\b", r"\btài xế\b", r"\bkhách\b"
]


def _cum_in_hoa(t: str) -> list[str]:
    """Các cụm từ viết hoa toàn bộ, gộp từ liền nhau ("NGUY CƠ", "CẢNH BÁO")."""
    out, cum = [], []
    for w in re.findall(r"[^\W\d_]+|\S", t):
        if len(w) >= 2 and w.isupper():
            cum.append(w)
            continue
        if cum:
            out.append(" ".join(cum))
        cum = []
    return out + ([" ".join(cum)] if cum else [])


def _co(pats: list[str], text: str) -> bool:
    return any(re.search(pat, text) for pat in pats)


def kiem(tieu_de: str) -> list[str]:
    """Lỗi của tiêu đề (rỗng nếu hợp lệ). Thiếu số/góc Việt Nam/thực thể chỉ là cảnh báo, xem cham_diem."""
    t = tieu_de.strip()
    if not t:
        return ["Lỗi: Tiêu đề không được để trống"]
    loi = []
    if len(t) > 100:
        loi.append(f"Lỗi: Tiêu đề dài {len(t)} ký tự (tối đa 100 ký tự)")
    if "<" in t or ">" in t:
        loi.append("Lỗi: Tiêu đề có ký tự < hoặc > (YouTube từ chối lúc upload)")
    lower = t.lower()
    giat = [m.group(0) for pat in TU_GIAT_GAN for m in re.finditer(pat, lower)]
    if NHAN_MO_DAU.search(lower):
        giat.insert(0, NHAN_MO_DAU.search(lower).group(0).rstrip(":!-– ").strip())
    elif (m := NHAN_IN_HOA.match(t)) and m.group(1).isupper() and not m.group(1).isascii():
        giat.insert(0, m.group(1).strip().lower())
    if giat:
        loi.append(f"Lỗi: Từ giật gân ({', '.join(dict.fromkeys(giat))}) – kiểu kênh tin tự động, đã thua trên số của kênh; "
                   "nói thẳng sự kiện và con số")
    if "!" in t:
        loi.append("Lỗi: Có dấu chấm than – bỏ đi, để con số và câu hỏi tạo tò mò")
    if t.count("?") + t.count("!") > 1 or len(HAI_CHAM.findall(t)) > 1:
        loi.append("Lỗi: Hai móc chồng nhau – chỉ giữ một câu hỏi, dạng «[sự kiện + số]: [một câu hỏi]?»")
    hoa = [c for c in _cum_in_hoa(t) if not c.isascii()]
    if hoa:
        loi.append(f"Lỗi: Chữ in hoa cả từ ({' '.join(dict.fromkeys(hoa))}) – chỉ viết tắt như AI, GPU, USD được in hoa")
    return loi


def canh_bao(tieu_de: str) -> list[str]:
    """Cảnh báo về nội dung tiêu đề theo công thức «[sự kiện + số]: [một câu hỏi Việt Nam/túi tiền]?»."""
    t = tieu_de.strip()
    if not t:
        return []
    lower, out = t.lower(), []
    if not re.search(r"\d", t):
        out.append("Cảnh báo: Thiếu con số (lấy từ nguon.json) – tiêu đề thắng của đối thủ luôn có số")
    if not _co(GOC_VIET_NAM, lower):
        out.append("Cảnh báo: Thiếu góc Việt Nam hoặc túi tiền người xem (Việt Nam, người dùng, giá tăng, túi ai…)")
    truoc = HAI_CHAM.split(lower, maxsplit=1)[0] if HAI_CHAM.search(lower) else lower[:50]
    if not _co(THUC_THE, truoc):
        out.append("Cảnh báo: Phần đầu (trước dấu «:») thiếu thực thể cụ thể (Nvidia, Grab, iPhone, Microsoft…)")
    if not HAI_CHAM.search(t) or not t.endswith("?"):
        out.append("Gợi ý: Dạng tiêu đề thắng là «[sự kiện + số]: [một câu hỏi]?»")
    return out


class KetQuaKiemTra(NamedTuple):
    hop_le: bool
    diem: int
    loi: list[str]
    canh_bao: list[str]


def cham_diem(tieu_de: str) -> KetQuaKiemTra:
    """Điểm 0–10: trừ 3 mỗi lỗi, 1 mỗi cảnh báo/gợi ý."""
    t = tieu_de.strip()
    if not t:
        return KetQuaKiemTra(hop_le=False, diem=0, loi=["Tiêu đề trống"], canh_bao=[])
    loi, cb = kiem(t), canh_bao(t)
    diem = max(0, min(10, 10 - 3 * len(loi) - len(cb)))
    return KetQuaKiemTra(hop_le=not loi, diem=diem, loi=loi, canh_bao=cb)


_KHAO_CUONG = {
    "cấm bán": ("ban sale", "prohibit sale", "cấm kinh doanh"),
    "mất trắng": ("wipe out", "lose everything", "trắng tay"),
    "từ chức": ("resign", "step down", "stepping down", "rời ghế"),
    "phá sản": ("bankrupt", "bankruptcy"),
    "khai tử": ("discontinue", "kill off", "shut down"),
    "sập hoàn toàn": ("complete outage", "total shutdown", "tê liệt hoàn toàn"),
}
_DANH_TU_CHUNG = re.compile(r"\b(?:ông chủ|gã khổng lồ|hãng công nghệ lớn|tập đoàn lớn)\b", re.I)


def kiem_khop_nguon(tieu_de: str, nguon: list[dict]) -> list[str]:
    """Kiểm tra tiêu đề không giật tít quá sự thật trong nguon.json và ưu tiên tên riêng có lượng tìm kiếm."""
    t = tieu_de.strip()
    if not t:
        return []
    lower = t.lower()
    out: list[str] = []
    hay = " ".join(f"{n.get('gia_tri', '')} {n.get('trich_dan', '')}" for n in nguon).lower().strip()
    if hay:
        for cum, dong_nghia in _KHAO_CUONG.items():
            if re.search(rf"\b{re.escape(cum)}\b", lower):
                if cum not in hay and not any(s in hay for s in dong_nghia):
                    out.append(f"Cảnh báo lệch nguồn: Tiêu đề dùng cụm «{cum}» chưa thấy trong trích dẫn nguồn gốc")
    if _DANH_TU_CHUNG.search(lower):
        out.append("Gợi ý tìm kiếm: Tiêu đề dùng danh từ chung (vd 'ông chủ', 'gã khổng lồ') — nên nêu tên riêng cụ thể (vd Jensen Huang, Microsoft 365) để đón tìm kiếm")
    return out
