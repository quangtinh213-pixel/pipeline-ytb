"""Bộ kiểm tra (Linter) và chấm điểm tiêu đề video YouTube theo chuẩn Pipeline 2.0.

Tiêu chí bắt buộc:
1. Từ cảm xúc/cảnh báo mạnh (Trigger words)
2. Thực thể lớn/thương hiệu công nghệ (Anchor entities)
3. Góc Việt Nam hoặc quyền lợi/túi tiền người xem (Relevance hook)
4. Độ dài <= 100 ký tự, phần gây tò mò nằm trong 50 ký tự đầu.
"""
import re
from typing import NamedTuple

# 1. Từ kích thích cảm xúc / giật gân / cảnh báo
TU_CAM_XUC = [
    r"\bsốc\b", r"\bcảnh báo\b", r"\bsự thật\b", r"\bnguy cơ\b", r"\bmất trắng\b",
    r"\bbất ngờ\b", r"\bcấm\b", r"\bhủy bỏ\b", r"\bhủy\b", r"\btẩy chay\b",
    r"\bđắt gấp\b", r"\bchiêu trò\b", r"\bcạn tiền\b", r"\bbốc hơi\b", r"\bsụp đổ\b",
    r"\bbẫy\b", r"\bchấn động\b", r"\btừ chức\b", r"\bôm nợ\b", r"\bhết cửa\b",
    r"\blật tẩy\b", r"\bvỡ mộng\b", r"\bthảm họa\b", r"\bkỷ lục\b", r"\bkhẩn cấp\b"
]

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
    r"\blãng phí\b", r"\blương\b", r"\bmất việc\b", r"\btúi ai\b"
]


class KetQuaKiemTra(NamedTuple):
    hop_le: bool
    diem: int
    loi: list[str]
    canh_bao: list[str]


def kiem(tieu_de: str) -> list[str]:
    """Kiểm tra tính hợp lệ của tiêu đề. Trả về danh sách lỗi (rỗng nếu đạt chuẩn)."""
    t = tieu_de.strip()
    loi = []
    
    # Giới hạn độ dài tuyệt đối của YouTube
    if not t:
        return ["Lỗi: Tiêu đề không được để trống"]
    if len(t) > 100:
        loi.append(f"Lỗi: Tiêu đề dài {len(t)} ký tự (tối đa 100 ký tự)")
    if "<" in t or ">" in t:
        loi.append("Lỗi: Tiêu đề có ký tự < hoặc > (YouTube từ chối lúc upload)")

    lower = t.lower()
    
    # 1. Kiểm tra từ cảm xúc
    co_cam_xuc = any(re.search(pat, lower) for pat in TU_CAM_XUC)
    if not co_cam_xuc:
        loi.append("Lỗi: Thiếu từ kích thích cảm xúc/cảnh báo (SỐC, CẢNH BÁO, BẤT NGỜ, NGUY CƠ, MẤT TRẮNG, CẤM...)")
        
    # 2. Kiểm tra thực thể lớn
    co_thuc_the = any(re.search(pat, lower) for pat in THUC_THE)
    if not co_thuc_the:
        loi.append("Lỗi: Thiếu tên thực thể/thương hiệu công nghệ lớn (Nvidia, Apple, Grab, VinFast, iPhone, AI...)")
        
    # 3. Kiểm tra góc Việt Nam / túi tiền
    co_goc_vn = any(re.search(pat, lower) for pat in GOC_VIET_NAM)
    if not co_goc_vn:
        loi.append("Lỗi: Thiếu góc liên quan Việt Nam hoặc túi tiền người xem (Việt Nam, túi tiền, người dùng, giá tăng, ôm nợ...)")
        
    return loi


def cham_diem(tieu_de: str) -> KetQuaKiemTra:
    """Chấm điểm tiêu đề trên thang điểm 10 và đưa ra khuyến nghị tối ưu."""
    t = tieu_de.strip()
    loi = kiem(t)
    canh_bao = []
    diem = 10
    
    if not t:
        return KetQuaKiemTra(hop_le=False, diem=0, loi=["Tiêu đề trống"], canh_bao=[])
        
    lower = t.lower()
    
    # Trừ điểm lỗi cơ bản
    for l in loi:
        diem -= 2.5
        
    # Cảnh báo vùng an toàn 50 ký tự đầu tiên
    dau_50 = lower[:50]
    co_yeu_to_dau = (any(re.search(pat, dau_50) for pat in TU_CAM_XUC) or 
                     any(re.search(pat, dau_50) for pat in THUC_THE))
    if not co_yeu_to_dau:
        canh_bao.append("Cảnh báo: 50 ký tự đầu chưa chứa từ gây sốc hoặc tên thương hiệu (dễ bị ẩn trên mobile)")
        diem -= 1.0
        
    # Khuyến khích có dấu câu kịch tính (! hoặc ?)
    if "?" not in t and "!" not in t:
        canh_bao.append("Cảnh báo: Nên có dấu '?' hoặc '!' để tăng tỷ lệ click (CTR)")
        diem -= 0.5
        
    # Khuyến khích có con số cụ thể
    if not re.search(r"\d+", t):
        canh_bao.append("Gợi ý: Thêm con số cụ thể (tỷ đô, %, triệu đồng) giúp tiêu đề đáng tin cậy hơn")
        
    diem = max(0, min(10, int(round(diem))))
    return KetQuaKiemTra(hop_le=(len(loi) == 0), diem=diem, loi=loi, canh_bao=canh_bao)


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
