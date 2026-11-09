"""Bộ nhân vật dẫn chuyện (pipeline/nhan-vat/kit.json + các PNG nền trong suốt): biểu cảm × hướng nhìn.

kit.json: {"the": [biểu cảm], "huong": [truoc|nghieng-trai|nghieng-phai|ngang...], "dang": [[the, huong], ...],
           "nham": [[the, huong], ...]}  ("nham" = cặp có thêm ảnh nhắm mắt để chớp). Tệp ảnh: tep(the, huong[, nham]).
Chưa có kit.json thì canh/compose dùng nhân vật SVG cũ (svg/tui-*.svg).
"""
import json
from pathlib import Path

PIPE = Path(__file__).resolve().parent.parent
KIT = PIPE / "nhan-vat" / "kit.json"


def doc_kit(path: Path | None = None) -> dict | None:
    p = KIT if path is None else Path(path)  # đọc KIT lúc gọi để test đổi được đường dẫn
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def hop_le(the: str, huong: str, kit: dict) -> bool:
    return [the, huong] in kit["dang"]


def huong_mac_dinh(goc: str) -> str:
    """Nhân vật đứng ở góc nào thì nghiêng về phía giữa màn hình."""
    return {"phai": "nghieng-trai", "trai": "nghieng-phai"}[goc]


def tep(the: str, huong: str, nham: bool = False) -> str:
    return f"{the}-{huong}{'-nham' if nham else ''}.png"
