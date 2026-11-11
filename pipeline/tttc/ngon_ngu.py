"""Chữ hiện trên màn hình phải là tiếng Việt: nhận ra chữ có vẻ tiếng Anh và liệt kê các ô chữ của một cảnh.

shortcut: heuristic, không phải nhận dạng ngôn ngữ; tiếng Anh dưới 4 từ (tên riêng, viết tắt như GPU) được bỏ qua,
chữ Việt viết không dấu bị coi là tiếng Anh nếu từ 4 từ trở lên; nâng cấp khi có nhãn nào bị báo nhầm.
"""
import re

DAU_VIET = re.compile(r"[ăâđêôơưàáảãạằắẳẵặầấẩẫậèéẻẽẹềếểễệìíỉĩịòóỏõọồốổỗộờớởỡợùúủũụừứửữựỳýỷỹỵ]", re.I)
TU_TOI_THIEU = 4
O_CHU = ("nhan", "so", "chuong", "tieu_de", "ti_le", "chu_thich", "vai", "truoc", "sau", "don_vi", "tu_khoa", "cau", "nho", "moi", "nut", "nut_xong", "khung")


def la_tieng_anh(text: str, toi_thieu: int = TU_TOI_THIEU) -> bool:
    """Có từ `toi_thieu` từ chữ cái trở lên và không có một ký tự tiếng Việt có dấu nào. Nhãn: 4 từ; câu trích: 2 từ."""
    if DAU_VIET.search(text or ""):
        return False
    return len(re.findall(r"[A-Za-z]{2,}", text or "")) >= toi_thieu


def man_hinh(c: dict) -> list[tuple[str, str]]:
    """[(tên ô, chữ)] của một cảnh canh.json: những chuỗi mẫu cảnh hiện lên màn hình (không gồm nguyên văn trích để kiểm chứng)."""
    out: list[tuple[str, str]] = []

    def add(k, v):
        if isinstance(v, str) and v.strip():
            out.append((k, v))

    if c.get("mau") == "trich-bao":
        add("trich_vi", c.get("trich_vi"))
    for k in O_CHU:
        add(k, c.get(k))
    if isinstance(c.get("chia"), dict):
        add("chia.nhan", c["chia"].get("nhan"))
    for side in ("trai", "phai"):
        if isinstance(c.get(side), dict):
            add(f"{side}.nhan", c[side].get("nhan"))
            add(f"{side}.don_vi", c[side].get("don_vi"))
    for key in ("buoc", "hang", "diem", "noi"):
        for i, b in enumerate(c.get(key) or []):
            if isinstance(b, dict):
                add(f"{key}[{i}].nhan", b.get("nhan"))
    if isinstance(c.get("truc"), dict):
        add("truc.don_vi", c["truc"].get("don_vi"))
    if isinstance(c.get("bieu_do"), dict):
        for k in ("don_vi", "chu_thich"):
            add(f"bieu_do.{k}", c["bieu_do"].get(k))
        for i, x in enumerate(c["bieu_do"].get("nhan_x") or []):
            add(f"bieu_do.nhan_x[{i}]", x)
    return out
