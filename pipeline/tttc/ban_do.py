"""Dữ liệu hình quốc gia cho mẫu cảnh `ban-do`: rút gọn từ Natural Earth (phạm vi công cộng, naturalearthdata.com).

Tạo lại: uv run python -m tttc.ban_do <ne_50m_admin_0_countries.geojson>   → pipeline/du-lieu/nuoc.json
Chỉ chứa hình quốc gia (đường biên và bờ biển), mã ADM0_A3 và tên tiếng Việt nếu có; không có đảo nhỏ dưới ngưỡng.
"""
import json
import math
import sys
from pathlib import Path

PIPE = Path(__file__).resolve().parent.parent
DATA = PIPE / "du-lieu" / "nuoc.json"
NGUON = "Natural Earth (phạm vi công cộng), ne_50m_admin_0_countries, rút gọn"
DIEN_TICH_MIN = 0.4  # độ² : vòng nhỏ hơn bị bỏ, trừ vòng lớn nhất của mỗi nước


def _khoang_cach(p, a, b) -> float:
    dx, dy = b[0] - a[0], b[1] - a[1]
    if dx == dy == 0:
        return math.hypot(p[0] - a[0], p[1] - a[1])
    t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)))
    return math.hypot(p[0] - (a[0] + t * dx), p[1] - (a[1] + t * dy))


def don_gian(ring: list, tol: float) -> list:
    """Douglas–Peucker trên một vòng khép kín; giữ điểm đầu = điểm cuối."""
    if len(ring) <= 4:
        return ring
    pts = ring[:-1]
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        i, j = stack.pop()
        far, idx = 0.0, -1
        for k in range(i + 1, j):
            d = _khoang_cach(pts[k], pts[i], pts[j])
            if d > far:
                far, idx = d, k
        if idx >= 0 and far > tol:
            keep[idx] = True
            stack += [(i, idx), (idx, j)]
    out = [p for p, k in zip(pts, keep) if k]
    return out + [out[0]] if len(out) >= 3 else ring


def _dien_tich(ring) -> float:
    return abs(sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(ring, ring[1:]))) / 2


def tao(src, dst=DATA, tol: float = 0.12) -> Path:
    feats = json.loads(Path(src).read_text(encoding="utf-8"))["features"]
    out = {}
    for f in feats:
        p, g = f["properties"], f["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        rings = [r[0] for r in polys if r]  # chỉ vòng ngoài: bỏ hồ và lỗ
        if not rings:
            continue
        big = max(rings, key=_dien_tich)
        vong = [[[round(x, 2), round(y, 2)] for x, y in don_gian(r, tol)] for r in rings if r is big or _dien_tich(r) >= DIEN_TICH_MIN]
        out[p.get("ADM0_A3") or p.get("ISO_A3")] = {"ten": p.get("NAME_VI") or p.get("NAME") or "", "vong": vong}
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps({"nguon": NGUON, "nuoc": out}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return dst


def doc(path=None) -> dict | None:
    p = DATA if path is None else Path(path)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def chon(nuoc: dict, lo0: float, lo1: float, la0: float, la1: float) -> dict:
    """Các nước có hộp bao chạm khung nhìn [lo0, lo1] × [la0, la1]."""
    out = {}
    for ma, n in nuoc.items():
        xs = [x for r in n["vong"] for x, _ in r]
        ys = [y for r in n["vong"] for _, y in r]
        if xs and min(xs) <= lo1 and max(xs) >= lo0 and min(ys) <= la1 and max(ys) >= la0:
            out[ma] = n
    return out


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("dùng: python -m tttc.ban_do <ne_50m_admin_0_countries.geojson>")
    d = tao(sys.argv[1])
    print(d, d.stat().st_size, "byte")
