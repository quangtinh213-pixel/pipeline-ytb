"""Màu và font thương hiệu một nguồn: brand/theme.json.

CSS/HTML của mẫu cảnh viết {{theme:khóa}} (khóa lồng nhau nối bằng dấu chấm, chỉ số danh sách là số) và được phân giải
bằng cssify lúc dựng. Màu vật thể (cờ, gỗ, xám nền đất) không thuộc theme. Đổi nhận diện: sửa theme.json rồi
uv run python -m tttc.theme ap-dung.
"""
import json
import re
from pathlib import Path

THEME = Path(__file__).resolve().parents[2] / "brand" / "theme.json"


def load(path: Path = THEME) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


TH = load()
VANG = tuple(TH["nhan"])
SAC = {k: tuple(v) for k, v in TH["sac"].items()}


def brand_colors() -> set[str]:
    """Bảng màu thư viện SVG (hoa chữ hoa): màu `ve` và bộ ba nhấn."""
    return {c.upper() for c in [*TH["ve"].values(), *TH["nhan"]]}


def _get(th: dict, key: str):
    cur = th
    for part in key.split("."):
        cur = cur[int(part)] if isinstance(cur, list) else cur[part]
    return cur


def cssify(text: str, th: dict | None = None) -> str:
    th = TH if th is None else th
    return re.sub(r"\{\{theme:([\w.]+)\}\}", lambda m: str(_get(th, m.group(1))), text)


def _lum(hex_color: str) -> float:
    r, g, b = (int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def contrast(a: str, b: str) -> float:
    hi, lo = sorted((_lum(a), _lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def kiem(th: dict) -> list[str]:
    out = []
    for ten, a, b in (("mực/nền", th["muc"], th["nen"]), ("chữ-trên-nhấn/nhấn", th["chu_tren_nhan"], th["nhan"][0]),
                      ("muted/nền", th["muted"], th["nen"])):
        c = contrast(a, b)
        if c < 4.5:
            out.append(f"Lỗi: tương phản {ten} {c:.1f}:1, cần ≥ 4,5")
    out += [f"Lỗi: màu nhấn {th['nhan'][0]} trùng màu phụ «{k}»" for k, v in th["sac"].items()
            if v[0].upper() == th["nhan"][0].upper()]
    if th.get("ten") != "hien-tai" and th["nen"].upper() == "#111111" and th["nhan"][0].upper() == "#FFC800":
        out.append("Cảnh báo: cặp đen–vàng trùng nhận diện của kênh mẫu")
    return out
