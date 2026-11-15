"""Sổ theo dõi video (theo-doi.csv): cột so sánh với đối thủ, di trú định dạng cũ, chênh giờ, tỉ số view.

Quy tắc đọc: chenh_gio âm nghĩa là video của mình đăng sớm hơn; view_ho_24h là view của video họ đúng 24 giờ sau khi họ đăng.
"""
import csv
import statistics
from datetime import datetime, timedelta, timezone
from pathlib import Path

# o_lai_short: tỉ lệ "ở lại xem" của Short, nhập tay từ Studio sau 48 giờ; khuon_short: cu / doc (dang ghi lúc upload)
EXTRA = ["trung_de_ho", "chenh_gio", "radar_hang", "view_ho_24h", "avd_pct", "con_50pct", "o_lai_short", "khuon_short"]
VN = timezone(timedelta(hours=7))
# Cửa sổ ghi số view: lỡ cửa sổ thì để trống, không ghi số của thời điểm khác vào cột.
CUA_SO = {"view_24h": (timedelta(hours=24), timedelta(hours=48)), "view_7d": (timedelta(days=7), timedelta(days=8))}


def dien_view(row: dict, views: str, now: datetime) -> bool:
    """Điền view_24h/view_7d còn trống khi tuổi video (tính từ gio_dang, giờ VN) nằm trong cửa sổ của cột. Trả True nếu có điền."""
    try:
        tuoi = now - datetime.strptime(row.get("gio_dang", ""), "%d/%m/%Y %H:%M").replace(tzinfo=VN)
    except ValueError:
        return False
    cot = [c for c, (a, b) in CUA_SO.items() if a <= tuoi < b and not row.get(c)]
    for c in cot:
        row[c] = views
    return bool(cot)


def migrate(path) -> None:
    """Thêm các cột EXTRA còn thiếu vào cuối header, giữ nguyên dữ liệu và thứ tự cột cũ. Không có tệp thì bỏ qua."""
    p = Path(path)
    if not p.exists():
        return
    with p.open(encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))
    if not rows:
        return
    thieu = [c for c in EXTRA if c not in rows[0]]
    if not thieu:
        return
    rows[0] += thieu
    rows[1:] = [r + [""] * len(thieu) for r in rows[1:]]
    with p.open("w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(rows)


def chenh_gio(gio_minh: datetime, gio_ho: datetime) -> float:
    return (gio_minh - gio_ho).total_seconds() / 3600


def _so(v) -> float | None:
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return x if x > 0 else None


def ty_so_trung_vi(rows: list[dict]) -> float | None:
    """Trung vị của view_24h / view_ho_24h trên tối đa 10 dòng cuối có cả hai giá trị dương."""
    ty = [a / b for r in rows if (a := _so(r.get("view_24h"))) and (b := _so(r.get("view_ho_24h")))]
    return statistics.median(ty[-10:]) if ty else None
