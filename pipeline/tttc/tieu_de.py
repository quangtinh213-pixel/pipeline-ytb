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
    r"\bqualcomm\b", r"\bamd\b", r"\bsamsung\b", r"\bhollywood\b", r"\bnetflix\b", r"\bfmovies\b"
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
