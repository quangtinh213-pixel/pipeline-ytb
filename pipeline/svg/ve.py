"""Vẽ thư viện SVG isometric theo brand. Chạy: uv run python svg/ve.py  (trong pipeline/).

Toạ độ 3D: x sang phải-trước, y sang trái-trước, z lên. Mặt thấy được: nóc (z cao), mặt x+ (phải), mặt y+ (trái).
"""
import math
from pathlib import Path

C, S = math.cos(math.radians(30)), math.sin(math.radians(30))
INK, WHITE, LIGHT, MID, DARK, Y = "#111111", "#FFFFFF", "#BDBDBD", "#6E6E6E", "#2A2A2A", "#FFC800"
OUT = Path(__file__).resolve().parent


def P(x, y, z):
    return ((x - y) * C, (x + y) * S - z)


def poly(pts, fill, sw=6):
    d = " ".join(f"{a:.1f},{b:.1f}" for a, b in (P(*p) for p in pts))
    return f'<polygon points="{d}" fill="{fill}" stroke="{INK}" stroke-width="{sw}" stroke-linejoin="round"/>'


def box(x, y, z, w, d, h, top=WHITE, left=LIGHT, right=MID):
    X, Yb, Z = x + w, y + d, z + h
    return [
        poly([(x, y, Z), (X, y, Z), (X, Yb, Z), (x, Yb, Z)], top),
        poly([(x, Yb, z), (X, Yb, z), (X, Yb, Z), (x, Yb, Z)], left),   # mặt y+ (trái-trước)
        poly([(X, y, z), (X, Yb, z), (X, Yb, Z), (X, y, Z)], right),    # mặt x+ (phải-trước)
    ]


def on_left(x, y, z, w, d, h, u0, v0, u1, v1, fill, sw=4):
    """Hình chữ nhật trên mặt y+ của hộp; u theo x (0..1), v theo z (0..1)."""
    Yb = y + d
    return poly([(x + u0 * w, Yb, z + v0 * h), (x + u1 * w, Yb, z + v0 * h),
                 (x + u1 * w, Yb, z + v1 * h), (x + u0 * w, Yb, z + v1 * h)], fill, sw)


def on_right(x, y, z, w, d, h, u0, v0, u1, v1, fill, sw=4):
    """Hình chữ nhật trên mặt x+ của hộp; u theo y (0..1), v theo z (0..1)."""
    X = x + w
    return poly([(X, y + u0 * d, z + v0 * h), (X, y + u1 * d, z + v0 * h),
                 (X, y + u1 * d, z + v1 * h), (X, y + u0 * d, z + v1 * h)], fill, sw)


def on_top(x, y, z, w, d, h, u0, v0, u1, v1, fill, sw=4):
    Z = z + h
    return poly([(x + u0 * w, y + v0 * d, Z), (x + u1 * w, y + v0 * d, Z),
                 (x + u1 * w, y + v1 * d, Z), (x + u0 * w, y + v1 * d, Z)], fill, sw)


def save(name, parts):
    body = "\n  ".join(parts)
    # khung nhìn tính từ toạ độ thật rồi đưa vào viewBox 0 0 400 400, chừa lề
    xs, ys = [], []
    import re
    for m in re.finditer(r'points="([^"]+)"', body):
        for pair in m.group(1).split():
            a, b = map(float, pair.split(","))
            xs.append(a), ys.append(b)
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    size = max(maxx - minx, maxy - miny) + 24
    cx, cy = (minx + maxx) / 2, (minx + maxx) and (miny + maxy) / 2
    vb = f"{cx - size / 2:.1f} {cy - size / 2:.1f} {size:.1f} {size:.1f}"
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="400" height="400">\n  {body}\n</svg>\n')
    (OUT / f"{name}.svg").write_text(svg, encoding="utf-8")


def toa_nha_quoc_hoi():
    p = box(0, 0, 0, 260, 120, 50)
    p += box(60, 20, 50, 140, 80, 60)
    for i in range(6):
        p += box(70 + i * 22, 100, 50, 10, 10, 60, WHITE, WHITE, LIGHT)
    p += box(105, 35, 110, 50, 50, 30, WHITE, LIGHT, MID)
    p += box(118, 48, 140, 24, 24, 40, Y, Y, "#C79C00")
    p += box(127, 57, 180, 6, 6, 24, INK, INK, INK)
    return p


def dien_thoai():
    p = box(0, 0, 0, 90, 16, 170, DARK, DARK, DARK)
    p.append(on_left(0, 0, 0, 90, 16, 170, 0.08, 0.06, 0.92, 0.94, Y))
    p.append(on_left(0, 0, 0, 90, 16, 170, 0.18, 0.62, 0.82, 0.78, WHITE, 3))
    p.append(on_left(0, 0, 0, 90, 16, 170, 0.18, 0.3, 0.6, 0.42, INK, 3))
    return p


def chip():
    p = []
    for i in range(6):
        p += box(25 + i * 25, -14, 0, 10, 14, 6, LIGHT, LIGHT, MID)
        p += box(-14, 25 + i * 25, 0, 14, 10, 6, LIGHT, LIGHT, MID)
    p += box(0, 0, 0, 180, 180, 22, DARK, DARK, DARK)
    for i in range(6):
        p += box(25 + i * 25, 180, 0, 10, 14, 6, LIGHT, LIGHT, MID)
        p += box(180, 25 + i * 25, 0, 14, 10, 6, LIGHT, LIGHT, MID)
    p.append(on_top(0, 0, 0, 180, 180, 22, 0.25, 0.25, 0.75, 0.75, Y))
    return p


def laptop():
    p = box(0, 0, 0, 200, 140, 10, LIGHT, LIGHT, MID)
    p.append(on_top(0, 0, 0, 200, 140, 10, 0.1, 0.45, 0.9, 0.85, MID, 3))
    p += box(0, -12, 10, 200, 12, 130, DARK, DARK, DARK)
    p.append(on_left(0, -12, 10, 200, 12, 130, 0.06, 0.08, 0.94, 0.92, Y))
    return p


def tien():
    p = []
    for i in range(4):
        p += box(0, 0, i * 18, 170, 90, 18, Y, "#E0B000", "#C79C00")
        p.append(on_top(0, 0, i * 18, 170, 90, 18, 0.35, 0.2, 0.65, 0.8, "#E0B000", 3))
    for i in range(5):
        p += box(200, 40, i * 12, 50, 50, 12, Y, "#E0B000", "#C79C00")
    return p


def tai_lieu():
    p = box(0, 0, 0, 150, 10, 200, WHITE, WHITE, LIGHT)
    for k, v in enumerate([0.82, 0.7, 0.6, 0.5, 0.4, 0.3]):
        p.append(on_left(0, 0, 0, 150, 10, 200, 0.12, v, 0.88 if k else 0.6, v + 0.04, MID if k else Y, 2))
    p.append(on_left(0, 0, 0, 150, 10, 200, 0.12, 0.1, 0.5, 0.18, Y, 3))
    return p


def nha_may():
    p = box(0, 0, 0, 240, 140, 70)
    for i in range(3):
        p += box(i * 80, 0, 70, 80, 140, 26, LIGHT, WHITE, MID)
    p += box(200, 20, 96, 26, 26, 110, MID, LIGHT, DARK)
    p += box(200, 20, 186, 26, 26, 14, Y, Y, "#C79C00")
    for i in range(4):
        p.append(on_left(0, 0, 0, 240, 140, 70, 0.06 + i * 0.23, 0.25, 0.2 + i * 0.23, 0.7, DARK, 3))
    return p


def may_chu():
    p = []
    for j in range(2):
        p += box(j * 120, 0, 0, 100, 100, 230, DARK, DARK, DARK)
        for i in range(7):
            v = 0.08 + i * 0.125
            p.append(on_left(j * 120, 0, 0, 100, 100, 230, 0.08, v, 0.92, v + 0.08, MID, 2))
            p.append(on_left(j * 120, 0, 0, 100, 100, 230, 0.78, v + 0.02, 0.86, v + 0.06,
                             Y if (i + j) % 3 == 0 else WHITE, 1))
    return p


def co_viet_nam():
    red = "#DA251D"  # cờ thật phải đúng màu, ngoại lệ duy nhất ngoài brand
    p = box(0, 0, 0, 40, 40, 10, LIGHT, LIGHT, MID)
    p += box(15, 15, 10, 10, 10, 250, WHITE, LIGHT, MID)
    p += box(25, 17, 140, 170, 6, 112, red, red, "#A51B15")
    # sao vàng 5 cánh trên mặt y+
    import math as m
    cx, cz, R, r = 25 + 85, 196, 34, 13
    pts = []
    for k in range(10):
        ang = m.pi / 2 + k * m.pi / 5
        rad = R if k % 2 == 0 else r
        pts.append((cx + rad * m.cos(ang), 23, cz + rad * m.sin(ang)))
    p.append(poly(pts, Y, 2))
    return p


def bieu_do_nen():
    p = box(0, 0, 0, 280, 120, 10, DARK, DARK, DARK)
    for i, (h, col) in enumerate([(60, LIGHT), (100, LIGHT), (150, LIGHT), (220, Y)]):
        top, left, right = (Y, "#E0B000", "#C79C00") if col == Y else (WHITE, LIGHT, MID)
        p += box(20 + i * 65, 35, 10, 45, 45, h, top, left, right)
    return p


def poly_raw(pts, fill, sw=6):
    """Đa giác từ toạ độ 3D, cho các mặt không phải hình hộp (chóp mũi tên, mái)."""
    return poly(pts, fill, sw)


def nen_dat():
    # nền sân khấu: tấm đất tối, đường xám có vạch vàng, vài ô cỏ
    G1, G2, G3, ROAD = "#262626", "#1A1A1A", "#141414", "#3A3A3A"
    p = box(0, 0, 0, 600, 420, 24, G1, G2, G3)
    p.append(on_top(0, 0, 0, 600, 420, 24, 0.0, 0.42, 1.0, 0.62, ROAD, 3))
    for k in range(6):
        u = 0.04 + k * 0.165
        p.append(on_top(0, 0, 0, 600, 420, 24, u, 0.505, u + 0.08, 0.535, Y, 2))
    p.append(on_top(0, 0, 0, 600, 420, 24, 0.05, 0.06, 0.32, 0.34, "#2F2F2F", 3))
    p.append(on_top(0, 0, 0, 600, 420, 24, 0.68, 0.70, 0.95, 0.94, "#2F2F2F", 3))
    return p


def cay():
    p = box(26, 26, 0, 18, 18, 60, "#8A6A3A", "#6E5430", "#5A4426")
    p += box(0, 0, 60, 70, 70, 70, "#FFFFFF", "#BDBDBD", "#6E6E6E")
    p += box(12, 12, 130, 46, 46, 34, "#FFFFFF", "#BDBDBD", "#6E6E6E")
    return p


def dong_xu():
    p = []
    for i in range(6):
        p += box(0, 0, i * 14, 80, 80, 14, Y, "#E0B000", "#C79C00")
        p.append(on_top(0, 0, i * 14, 80, 80, 14, 0.3, 0.3, 0.7, 0.7, "#E0B000", 2))
    for i in range(3):
        p += box(110, 30, i * 14, 80, 80, 14, Y, "#E0B000", "#C79C00")
    return p


def _mui_ten(up: bool, col_top, col_l, col_r):
    # thân hộp + chóp 4 mặt; up=False lật ngược chóp xuống dưới
    w, h, tip = 50, 150, 70
    if up:
        p = box(25, 25, 0, w, w, h, col_top, col_l, col_r)
        z0, z1 = h, h + tip
    else:
        p = box(25, 25, tip, w, w, h, col_top, col_l, col_r)
        z0, z1 = tip, 0
    a, b = (0, 0), (100, 100)
    apex = (50, 50, z1)
    base = [(a[0], a[1], z0), (b[0], a[1], z0), (b[0], b[1], z0), (a[0], b[1], z0)]
    if up:
        p.append(poly_raw([base[3], base[2], apex], col_l))
        p.append(poly_raw([base[1], base[2], apex], col_r))
    else:
        p.insert(0, poly_raw([base[3], base[2], apex], col_l))
        p.insert(0, poly_raw([base[1], base[2], apex], col_r))
        p.append(poly_raw(base, col_top))
    return p


def mui_ten_len():
    return _mui_ten(True, Y, "#E0B000", "#C79C00")


def mui_ten_xuong():
    return _mui_ten(False, WHITE, LIGHT, MID)


def container():
    p = box(0, 0, 0, 240, 100, 100, Y, "#E0B000", "#C79C00")
    for k in range(9):
        u = 0.06 + k * 0.1
        p.append(on_left(0, 0, 0, 240, 100, 100, u, 0.1, u + 0.04, 0.9, "#C79C00", 2))
    p += box(0, 0, 100, 240, 100, 100, WHITE, LIGHT, MID)
    for k in range(9):
        u = 0.06 + k * 0.1
        p.append(on_left(0, 0, 100, 240, 100, 100, u, 0.1, u + 0.04, 0.9, MID, 2))
    return p


def nguoi():
    p = box(10, 10, 0, 16, 16, 70, DARK, DARK, DARK)
    p += box(34, 10, 0, 16, 16, 70, DARK, DARK, DARK)
    p += box(0, 0, 70, 60, 36, 80, Y, "#E0B000", "#C79C00")
    p += box(14, 4, 150, 32, 28, 34, WHITE, LIGHT, MID)
    return p


ITEMS = {
    "toa-nha-quoc-hoi": toa_nha_quoc_hoi, "dien-thoai": dien_thoai, "chip": chip, "laptop": laptop,
    "tien": tien, "tai-lieu": tai_lieu, "nha-may": nha_may, "may-chu": may_chu,
    "co-viet-nam": co_viet_nam, "bieu-do-nen": bieu_do_nen,
    "nen-dat": nen_dat, "cay": cay, "dong-xu": dong_xu, "mui-ten-len": mui_ten_len,
    "mui-ten-xuong": mui_ten_xuong, "container": container, "nguoi": nguoi,
}

if __name__ == "__main__":
    for name, fn in ITEMS.items():
        save(name, fn())
    print(len(ITEMS), "svg")
