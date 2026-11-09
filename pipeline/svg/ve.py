"""Vẽ thư viện SVG isometric theo brand. Chạy: uv run python svg/ve.py  (trong pipeline/).

Toạ độ 3D: x sang phải-trước, y sang trái-trước, z lên. Mặt thấy được: nóc (z cao), mặt x+ (phải), mặt y+ (trái).
"""
import math
from pathlib import Path

from tttc import theme

C, S = math.cos(math.radians(30)), math.sin(math.radians(30))
_VE = theme.TH["ve"]
INK, WHITE, LIGHT, MID, DARK = _VE["ink"], _VE["trang"], _VE["sang"], _VE["vua"], _VE["toi"]
Y, Y2, Y3 = theme.TH["nhan"]  # nhấn, bóng, bóng tối
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
    cx, cy = (minx + maxx) / 2, (miny + maxy) / 2
    vb = f"{cx - size / 2:.1f} {cy - size / 2:.1f} {size:.1f} {size:.1f}"
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="400" height="400">\n  {body}\n</svg>\n')
    (OUT / f"{name}.svg").write_text(svg, encoding="utf-8")


def toa_nha_quoc_hoi():
    p = box(0, 0, 0, 260, 120, 50)
    p += box(60, 20, 50, 140, 80, 60)
    for i in range(6):
        p += box(70 + i * 22, 100, 50, 10, 10, 60, WHITE, WHITE, LIGHT)
    p += box(105, 35, 110, 50, 50, 30, WHITE, LIGHT, MID)
    p += box(118, 48, 140, 24, 24, 40, Y, Y, Y3)
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
        p += box(0, 0, i * 18, 170, 90, 18, Y, Y2, Y3)
        p.append(on_top(0, 0, i * 18, 170, 90, 18, 0.35, 0.2, 0.65, 0.8, Y2, 3))
    for i in range(5):
        p += box(200, 40, i * 12, 50, 50, 12, Y, Y2, Y3)
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
    p += box(200, 20, 186, 26, 26, 14, Y, Y, Y3)
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
        top, left, right = (Y, Y2, Y3) if col == Y else (WHITE, LIGHT, MID)
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
    p += box(0, 0, 60, 70, 70, 70, WHITE, LIGHT, MID)
    p += box(12, 12, 130, 46, 46, 34, WHITE, LIGHT, MID)
    return p


def dong_xu():
    p = []
    for i in range(6):
        p += box(0, 0, i * 14, 80, 80, 14, Y, Y2, Y3)
        p.append(on_top(0, 0, i * 14, 80, 80, 14, 0.3, 0.3, 0.7, 0.7, Y2, 2))
    for i in range(3):
        p += box(110, 30, i * 14, 80, 80, 14, Y, Y2, Y3)
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
    return _mui_ten(True, Y, Y2, Y3)


def mui_ten_xuong():
    return _mui_ten(False, WHITE, LIGHT, MID)


def container():
    p = box(0, 0, 0, 240, 100, 100, Y, Y2, Y3)
    for k in range(9):
        u = 0.06 + k * 0.1
        p.append(on_left(0, 0, 0, 240, 100, 100, u, 0.1, u + 0.04, 0.9, Y3, 2))
    p += box(0, 0, 100, 240, 100, 100, WHITE, LIGHT, MID)
    for k in range(9):
        u = 0.06 + k * 0.1
        p.append(on_left(0, 0, 100, 240, 100, 100, u, 0.1, u + 0.04, 0.9, MID, 2))
    return p


def nguoi():
    p = box(10, 10, 0, 16, 16, 70, DARK, DARK, DARK)
    p += box(34, 10, 0, 16, 16, 70, DARK, DARK, DARK)
    p += box(0, 0, 70, 60, 36, 80, Y, Y2, Y3)
    p += box(14, 4, 150, 32, 28, 34, WHITE, LIGHT, MID)
    return p


# ---------- Đợt A: chip / bán dẫn ----------
def polyline(pts, sw=6):
    d = " ".join(f"{a:.1f},{b:.1f}" for a, b in (P(*p) for p in pts))
    return f'<polyline points="{d}" fill="none" stroke="{INK}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"/>'


def cil(cx, cy, z, r, h, top=WHITE, left=LIGHT, right=MID, n=32):
    """Hình trụ đứng: mặt bên chỉ vẽ nửa nhìn thấy (góc −45°…135°), tô bằng chính màu mặt để không lộ đường nối."""
    ang = [2 * math.pi * k / n for k in range(n + 1)]
    p, vis = [], []
    for k in range(n):
        am = (ang[k] + ang[k + 1]) / 2
        am = (am + math.pi) % (2 * math.pi) - math.pi
        if -math.pi / 4 <= am <= 3 * math.pi / 4:
            col = left if am > math.pi / 4 else right
            q = [(cx + r * math.cos(ang[k]), cy + r * math.sin(ang[k]), z), (cx + r * math.cos(ang[k + 1]), cy + r * math.sin(ang[k + 1]), z),
                 (cx + r * math.cos(ang[k + 1]), cy + r * math.sin(ang[k + 1]), z + h), (cx + r * math.cos(ang[k]), cy + r * math.sin(ang[k]), z + h)]
            d = " ".join(f"{a:.1f},{b:.1f}" for a, b in (P(*t) for t in q))
            p.append(f'<polygon points="{d}" fill="{col}" stroke="{col}" stroke-width="2"/>')
            vis.append(k)
    k0, k1 = vis[0], vis[-1] + 1
    p.append(polyline([(cx + r * math.cos(ang[k]), cy + r * math.sin(ang[k]), z) for k in range(k0, k1 + 1)]))
    for k in (k0, k1):
        p.append(polyline([(cx + r * math.cos(ang[k]), cy + r * math.sin(ang[k]), z), (cx + r * math.cos(ang[k]), cy + r * math.sin(ang[k]), z + h)]))
    p.append(poly([(cx + r * math.cos(a), cy + r * math.sin(a), z + h) for a in ang[:-1]], top))
    return p


def wafer():
    p = cil(0, 0, 0, 130, 12, LIGHT, LIGHT, MID)
    for gx in range(-4, 5):
        for gy in range(-4, 5):
            x, y = gx * 24, gy * 24
            if (x * x + y * y) ** 0.5 < 112:
                p.append(poly([(x - 9, y - 9, 12), (x + 9, y - 9, 12), (x + 9, y + 9, 12), (x - 9, y + 9, 12)],
                              Y if (gx, gy) == (1, 0) else WHITE, 2))
    return p


def nha_may_duc():
    p = box(0, 0, 0, 260, 170, 80)
    for i in range(4):
        p += box(i * 65, 0, 80, 65, 170, 22, LIGHT, WHITE, MID)
    for i in range(5):
        p.append(on_left(0, 0, 0, 260, 170, 80, 0.07 + i * 0.18, 0.5, 0.2 + i * 0.18, 0.8, DARK, 3))
    p.append(on_left(0, 0, 0, 260, 170, 80, 0.4, 0.05, 0.6, 0.45, Y, 3))
    return p


def phong_sach():
    p = box(0, 0, 0, 220, 170, 100, WHITE, WHITE, LIGHT)
    p.append(on_left(0, 0, 0, 220, 170, 100, 0.06, 0.15, 0.94, 0.85, DARK, 3))
    p.append(on_left(0, 0, 0, 220, 170, 100, 0.12, 0.2, 0.3, 0.8, MID, 3))
    p.append(on_left(0, 0, 0, 220, 170, 100, 0.7, 0.05, 0.86, 0.8, Y, 3))
    return p + box(30, 190, 0, 70, 50, 60, LIGHT, LIGHT, MID) + box(130, 190, 0, 70, 50, 40, LIGHT, LIGHT, MID)


def may_quang_khac():
    p = box(0, 0, 0, 200, 140, 40, DARK, DARK, DARK)
    p += box(20, 20, 40, 160, 100, 110, LIGHT, WHITE, MID)
    p += box(70, 40, 150, 60, 60, 36, DARK, DARK, DARK)
    p += cil(100, 70, 186, 22, 40, Y, Y2, Y3)
    p.append(on_left(20, 20, 40, 160, 100, 110, 0.1, 0.2, 0.9, 0.8, MID, 3))
    return p


def chip_bao_mat():
    p = chip()
    p += box(60, 60, 22, 60, 50, 36, Y, Y2, Y3)
    p += box(72, 72, 58, 10, 10, 30, DARK, DARK, DARK) + box(98, 72, 58, 10, 10, 30, DARK, DARK, DARK)
    p += box(72, 72, 88, 36, 10, 10, DARK, DARK, DARK)
    return p


def usb():
    p = box(0, 0, 0, 80, 170, 24, DARK, DARK, DARK)
    p.append(on_top(0, 0, 0, 80, 170, 24, 0.2, 0.1, 0.8, 0.5, Y, 3))
    p += box(14, 170, 2, 52, 60, 18, LIGHT, WHITE, MID)
    p += box(24, 230, 6, 10, 10, 8, DARK, DARK, DARK) + box(46, 230, 6, 10, 10, 8, DARK, DARK, DARK)
    return p


def o_khoa():
    p = box(0, 0, 0, 130, 70, 20, DARK, DARK, DARK)
    p += box(10, 5, 20, 110, 60, 90, Y, Y2, Y3)
    p += box(25, 20, 110, 16, 16, 60, LIGHT, WHITE, MID) + box(89, 20, 110, 16, 16, 60, LIGHT, WHITE, MID)
    p += box(25, 20, 170, 80, 16, 16, LIGHT, WHITE, MID)
    p.append(on_left(10, 5, 20, 110, 60, 90, 0.42, 0.3, 0.58, 0.7, INK, 3))
    return p


def chia_khoa():
    p = box(0, 0, 0, 220, 26, 12, LIGHT, WHITE, MID)
    p += box(150, 0, 12, 20, 26, 26, LIGHT, WHITE, MID) + box(190, 0, 12, 20, 26, 40, LIGHT, WHITE, MID)
    p += cil(-30, 13, 0, 56, 12, Y, Y2, Y3)
    p += cil(-30, 13, 12, 18, 1, DARK, DARK, DARK)
    return p


def khien():
    p = []
    for k, (w, h) in enumerate([(150, 40), (140, 30), (110, 30), (70, 30), (30, 24)]):
        p += box((150 - w) / 2, 0, sum(x[1] for x in [(150, 40), (140, 30), (110, 30), (70, 30)][:k]), w, 24, h,
                 Y if k == 0 else WHITE, Y2 if k == 0 else LIGHT, Y3 if k == 0 else MID)
    p.append(on_left(0, 0, 0, 150, 24, 40, 0.42, 0.2, 0.58, 0.9, INK, 3))
    return p


def transistor():
    p = [q for i in range(3) for q in box(14 + i * 28, 10, 0, 10, 10, 50, LIGHT, WHITE, MID)]
    p += box(0, 0, 50, 90, 50, 70, DARK, DARK, DARK)
    p.append(on_left(0, 0, 50, 90, 50, 70, 0.15, 0.15, 0.85, 0.5, Y, 3))
    return p


def soi_toc():
    p = box(0, 0, 0, 330, 6, 6, DARK, DARK, DARK)
    p += box(300, 30, 0, 36, 36, 8, Y, Y2, Y3)
    p += box(-10, 30, 0, 26, 26, 8, LIGHT, WHITE, MID)
    return p


def hat_gao():
    p = box(0, 0, 0, 160, 120, 10, DARK, DARK, DARK)
    p += box(55, 40, 10, 50, 22, 16, WHITE, WHITE, LIGHT)
    p.append(on_top(55, 40, 10, 50, 22, 16, 0.1, 0.4, 0.9, 0.6, LIGHT, 2))
    p += box(120, 90, 10, 12, 12, 12, Y, Y2, Y3)
    return p


def san_bong():
    p = box(0, 0, 0, 320, 200, 10, DARK, DARK, DARK)
    p.append(on_top(0, 0, 0, 320, 200, 10, 0.05, 0.08, 0.95, 0.92, MID, 3))
    p.append(on_top(0, 0, 0, 320, 200, 10, 0.49, 0.08, 0.51, 0.92, WHITE, 2))
    p.append(on_top(0, 0, 0, 320, 200, 10, 0.4, 0.38, 0.6, 0.62, Y, 3))
    for u in (0.0, 0.93):
        p += box(u * 320, 70, 10, 22, 60, 6, WHITE, WHITE, LIGHT)
    return p


def thuoc_do():
    p = box(0, 0, 0, 320, 56, 10, WHITE, WHITE, LIGHT)
    for k in range(17):
        p.append(on_top(0, 0, 0, 320, 56, 10, 0.03 + k * 0.057, 0.0, 0.03 + k * 0.057 + 0.012, 0.5 if k % 4 == 0 else 0.3, INK, 2))
    p.append(on_top(0, 0, 0, 320, 56, 10, 0.03, 0.62, 0.34, 0.92, Y, 2))
    return p


def dong_ho():
    p = cil(0, 0, 0, 90, 22, WHITE, LIGHT, MID)
    p.append(poly([(-6, 0, 22), (6, 0, 22), (6, -60, 22), (-6, -60, 22)], INK, 2))
    p.append(poly([(0, -6, 22), (0, 6, 22), (46, 6, 22), (46, -6, 22)], INK, 2))
    p += cil(0, 0, 22, 12, 6, Y, Y2, Y3)
    return p


def lich():
    p = box(0, 0, 0, 170, 18, 190, WHITE, WHITE, LIGHT)
    p.append(on_left(0, 0, 0, 170, 18, 190, 0.0, 0.8, 1.0, 1.0, Y, 3))
    for r in range(4):
        for c in range(4):
            p.append(on_left(0, 0, 0, 170, 18, 190, 0.08 + c * 0.22, 0.08 + r * 0.17, 0.24 + c * 0.22, 0.2 + r * 0.17,
                             Y if (r, c) == (1, 2) else MID, 2))
    return p


# ---------- Đợt B: AI / dữ liệu / crypto ----------
def trung_tam_du_lieu():
    p = box(0, 0, 0, 340, 240, 12, DARK, DARK, DARK)
    for j in range(2):
        for i in range(3):
            x, y = 20 + i * 100, 20 + j * 110
            p += box(x, y, 12, 80, 70, 130, DARK, DARK, DARK)
            for k in range(5):
                v = 0.1 + k * 0.17
                p.append(on_left(x, y, 12, 80, 70, 130, 0.1, v, 0.9, v + 0.1, MID, 2))
                p.append(on_left(x, y, 12, 80, 70, 130, 0.76, v + 0.03, 0.84, v + 0.07, Y if (i + j + k) % 5 == 0 else WHITE, 1))
    return p


def bo_nao_ai():
    p = box(0, 0, 0, 200, 200, 14, DARK, DARK, DARK)
    p += box(25, 25, 14, 150, 150, 50, LIGHT, WHITE, MID)
    p += box(50, 50, 64, 100, 100, 50, WHITE, LIGHT, MID)
    p += box(75, 75, 114, 50, 50, 40, Y, Y2, Y3)
    for i in range(3):
        p.append(on_left(25, 25, 14, 150, 150, 50, 0.1 + i * 0.3, 0.3, 0.3 + i * 0.3, 0.7, MID, 3))
    return p


def robot():
    p = box(10, 10, 0, 30, 30, 50, DARK, DARK, DARK) + box(70, 10, 0, 30, 30, 50, DARK, DARK, DARK)
    p += box(0, 0, 50, 110, 60, 100, LIGHT, WHITE, MID)
    p.append(on_left(0, 0, 50, 110, 60, 100, 0.35, 0.3, 0.65, 0.6, Y, 3))
    p += box(20, 8, 150, 70, 44, 50, WHITE, WHITE, LIGHT)
    p.append(on_left(20, 8, 150, 70, 44, 50, 0.15, 0.4, 0.4, 0.7, INK, 3))
    p.append(on_left(20, 8, 150, 70, 44, 50, 0.6, 0.4, 0.85, 0.7, INK, 3))
    p += box(50, 26, 200, 10, 10, 30, DARK, DARK, DARK) + box(46, 22, 230, 18, 18, 14, Y, Y2, Y3)
    return p


def dam_may():
    p = box(0, 20, 0, 120, 100, 60, WHITE, WHITE, LIGHT)
    p += box(60, 0, 0, 130, 130, 90, WHITE, LIGHT, MID)
    p += box(150, 30, 0, 110, 90, 55, WHITE, WHITE, LIGHT)
    p += box(95, 35, 90, 60, 60, 10, Y, Y2, Y3)
    return p


def pin():
    p = box(0, 0, 0, 200, 90, 90, DARK, DARK, DARK)
    p += box(200, 25, 25, 18, 40, 40, LIGHT, WHITE, MID)
    for k in range(4):
        p.append(on_left(0, 0, 0, 200, 90, 90, 0.06 + k * 0.17, 0.2, 0.2 + k * 0.17, 0.8, Y if k < 3 else MID, 3))
    return p


def tia_set():
    pts = [(60, 0), (0, 90), (45, 90), (20, 190), (110, 70), (62, 70), (100, 0)]
    p = []
    for off, col in ((-16, Y3), (0, Y)):
        p.append(poly([(x, off, z) for x, z in pts], col))
    return p


def tram_phat_song():
    p = box(40, 40, 0, 120, 120, 14, DARK, DARK, DARK)
    p += box(90, 90, 14, 20, 20, 240, LIGHT, WHITE, MID)
    for k in range(3):
        p += box(70 - k * 0, 80, 120 + k * 50, 60, 6, 8, DARK, DARK, DARK) if False else box(75, 85, 130 + k * 45, 50, 8, 10, MID, LIGHT, DARK)
    p += box(86, 86, 254, 28, 28, 28, Y, Y2, Y3)
    return p


def bong_bong():
    """Quả cầu xếp từ 8 đĩa chồng nhau (kiểu khối như cả thư viện), một chấm vàng ở mặt trước."""
    p = []
    for k in range(8):
        zc = k * 25 + 12.5
        r = math.sqrt(max(100 ** 2 - (zc - 100) ** 2, 36))
        p += cil(0, 0, k * 25, r, 25, WHITE, LIGHT, MID, n=18)
    return p + box(52, 52, 78, 22, 22, 22, Y, Y2, Y3)


def do_thi_roi():
    p = box(0, 0, 0, 300, 120, 10, DARK, DARK, DARK)
    for i, h in enumerate([200, 150, 100, 50]):
        col = (Y, Y2, Y3) if i == 3 else (WHITE, LIGHT, MID)
        p += box(20 + i * 68, 35, 10, 46, 46, h, *col)
    return p


def ket_sat():
    p = box(0, 0, 0, 170, 130, 170, DARK, DARK, DARK)
    p.append(on_left(0, 0, 0, 170, 130, 170, 0.1, 0.1, 0.9, 0.9, MID, 3))
    p.append(on_left(0, 0, 0, 170, 130, 170, 0.18, 0.2, 0.82, 0.8, DARK, 3))
    p.append(on_left(0, 0, 0, 170, 130, 170, 0.55, 0.42, 0.78, 0.66, Y, 3))
    p.append(on_left(0, 0, 0, 170, 130, 170, 0.28, 0.46, 0.46, 0.5, WHITE, 2))
    return p


def the_ngan_hang():
    p = box(0, 0, 0, 200, 124, 10, WHITE, WHITE, LIGHT)
    p.append(on_top(0, 0, 0, 200, 124, 10, 0.0, 0.14, 1.0, 0.32, DARK, 2))
    p.append(on_top(0, 0, 0, 200, 124, 10, 0.08, 0.45, 0.28, 0.75, Y, 3))
    p.append(on_top(0, 0, 0, 200, 124, 10, 0.4, 0.55, 0.9, 0.62, MID, 2))
    p.append(on_top(0, 0, 0, 200, 124, 10, 0.4, 0.75, 0.7, 0.82, MID, 2))
    return p


def vi_tien():
    p = box(0, 0, 0, 190, 110, 70, DARK, DARK, DARK)
    p += box(0, 0, 70, 190, 110, 14, LIGHT, WHITE, MID)
    p.append(on_left(0, 0, 0, 190, 110, 70, 0.78, 0.35, 0.96, 0.65, Y, 3))
    p += box(30, -30, 0, 70, 30, 10, Y, Y2, Y3)
    return p


# ---------- Đợt C: kinh tế / chính trị / đời sống ----------
def can_cung_cau():
    p = box(70, 40, 0, 100, 60, 14, DARK, DARK, DARK)
    p += box(110, 60, 14, 20, 20, 190, LIGHT, WHITE, MID)
    p += box(-30, 60, 204, 300, 20, 14, WHITE, WHITE, LIGHT)
    p += box(-30, 40, 120, 90, 60, 10, DARK, DARK, DARK) + box(180, 40, 120, 90, 60, 10, DARK, DARK, DARK)
    p += box(-10, 55, 130, 50, 30, 50, Y, Y2, Y3) + box(200, 55, 130, 50, 30, 24, WHITE, LIGHT, MID)
    return p


def bua_phan_quyet():
    p = box(0, 0, 0, 160, 110, 24, DARK, DARK, DARK)
    p += box(60, 40, 24, 30, 30, 90, LIGHT, WHITE, MID)
    p += box(10, 30, 114, 130, 50, 50, DARK, DARK, DARK)
    p += box(10, 30, 164, 130, 50, 12, Y, Y2, Y3)
    return p


def ta_hang():
    p = box(0, 0, 0, 320, 110, 40, DARK, DARK, DARK)
    for i in range(3):
        p += box(20 + i * 80, 10, 40, 74, 90, 50, Y if i == 1 else WHITE, Y2 if i == 1 else LIGHT, Y3 if i == 1 else MID)
    p += box(250, 10, 40, 60, 90, 80, WHITE, LIGHT, MID)
    p.append(on_left(250, 10, 40, 60, 90, 80, 0.15, 0.45, 0.85, 0.75, DARK, 3))
    return p


def cang_bien():
    p = box(0, 0, 0, 340, 140, 14, DARK, DARK, DARK)
    p += box(30, 20, 14, 14, 14, 200, LIGHT, WHITE, MID) + box(150, 20, 14, 14, 14, 200, LIGHT, WHITE, MID)
    p += box(20, 16, 214, 160, 22, 14, Y, Y2, Y3)
    for i in range(3):
        p += box(200 + i * 40, 30, 14, 36, 70, 30, WHITE if i != 1 else LIGHT, LIGHT, MID)
    return p


def oto():
    p = box(0, 0, 20, 220, 100, 40, WHITE, LIGHT, MID)
    p += box(50, 6, 60, 110, 88, 40, LIGHT, WHITE, MID)
    p.append(on_left(50, 6, 60, 110, 88, 40, 0.1, 0.2, 0.9, 0.85, DARK, 3))
    for x in (20, 150):
        p += box(x, -6, 0, 40, 20, 40, DARK, DARK, DARK)
        p += box(x, 90, 0, 40, 20, 40, DARK, DARK, DARK)
    p.append(on_left(0, 0, 20, 220, 100, 40, 0.02, 0.4, 0.98, 0.6, Y, 2))
    return p


def kinh_lup():
    p = box(150, 150, 0, 160, 18, 18, DARK, DARK, DARK) if False else box(110, 110, 0, 140, 16, 16, DARK, DARK, DARK)
    p += cil(40, 40, 8, 80, 14, DARK, DARK, DARK)
    p += cil(40, 40, 22, 62, 2, WHITE, LIGHT, MID)
    p.append(poly([(10, 50, 24), (40, 30, 24), (60, 40, 24), (50, 50, 24)], Y, 2))
    return p


def ten_lua():
    p = cil(0, 0, 40, 40, 150, WHITE, LIGHT, MID)
    nose = [(40 * math.cos(a), 40 * math.sin(a), 190) for a in [2 * math.pi * k / 16 for k in range(16)]]
    p += [poly([nose[0], nose[4], (0, 0, 270)], Y2, 3), poly([nose[4], nose[8], (0, 0, 270)], Y, 3)]
    p += box(-70, -12, 40, 36, 24, 70, Y, Y2, Y3) + box(34, -12, 40, 36, 24, 70, Y, Y2, Y3)
    p += box(-20, -20, 0, 40, 40, 40, DARK, DARK, DARK)
    return p


def hop_thu():
    p = box(0, 0, 0, 230, 150, 14, WHITE, WHITE, LIGHT)
    p.append(poly([(0, 0, 14), (230, 0, 14), (115, 75, 14)], Y, 4))
    p.append(poly([(0, 150, 14), (115, 75, 14), (0, 0, 14)], LIGHT, 4))
    p.append(poly([(230, 150, 14), (115, 75, 14), (230, 0, 14)], MID, 4))
    return p


def thue_phan_tram():
    p = cil(0, 0, 0, 44, 14, WHITE, LIGHT, MID) + cil(110, 110, 0, 44, 14, WHITE, LIGHT, MID)
    p.append(poly([(-14, 84, 14), (0, 98, 14), (124, 6, 14), (110, -8, 14)], Y, 4))
    return p


def _ng(x0, y0, top=Y):
    side = (Y2, Y3) if top == Y else (LIGHT, MID)
    p = box(x0 + 10, y0 + 10, 0, 16, 16, 70, DARK, DARK, DARK) + box(x0 + 34, y0 + 10, 0, 16, 16, 70, DARK, DARK, DARK)
    p += box(x0, y0, 70, 60, 36, 80, top, *side) + box(x0 + 14, y0 + 4, 150, 32, 28, 34, WHITE, LIGHT, MID)
    return p


def nguoi_nhom():
    return _ng(0, 0, WHITE) + _ng(70, 60, Y) + _ng(150, 10, WHITE)


def tui_xach():
    p = box(0, 0, 0, 130, 70, 150, WHITE, WHITE, LIGHT)
    p.append(on_left(0, 0, 0, 130, 70, 150, 0.0, 0.55, 1.0, 0.75, Y, 3))
    p += box(30, 28, 150, 10, 10, 50, DARK, DARK, DARK) + box(90, 28, 150, 10, 10, 50, DARK, DARK, DARK)
    p += box(30, 28, 200, 70, 10, 10, DARK, DARK, DARK)
    return p


def cao_oc():
    p = box(0, 0, 0, 110, 90, 260, WHITE, LIGHT, MID)
    for r in range(9):
        for c in range(3):
            p.append(on_left(0, 0, 0, 110, 90, 260, 0.12 + c * 0.28, 0.07 + r * 0.1, 0.28 + c * 0.28, 0.12 + r * 0.1, DARK, 2))
    p += box(110, 10, 0, 80, 70, 150, LIGHT, WHITE, MID)
    p += box(25, 20, 260, 60, 50, 24, Y, Y2, Y3)
    return p


# ---------- Nhân vật dẫn chuyện "Túi" (chờ duyệt, Task 8) ----------
def tui(the: str = "chao", nham: bool = False):
    """Chiếc túi tiền vàng có mặt trên mặt y+ của thân. the: chao | ngac-nhien | nghi; nham: mắt nhắm (để chớp)."""
    body = (0, 0, 12, 130, 90, 100)
    mat = lambda u0, v0, u1, v1, fill, sw=3: on_left(*body, u0, v0, u1, v1, fill, sw)
    arm = lambda x, z, h: box(x, 30, z, 20, 16, h, DARK, DARK, DARK)
    p = []
    if the == "ngac-nhien":
        p += arm(-20, 60, 70)  # tay trái ở phía sau thân nên vẽ trước
    p += box(15, 10, 0, 100, 70, 12, DARK, DARK, DARK)
    p += box(*body[:3], *body[3:], Y, Y2, Y3)
    p += box(25, 15, 112, 80, 60, 22, Y, Y2, Y3) + box(35, 25, 134, 60, 40, 12, DARK, DARK, DARK)
    p += box(20, 10, 146, 90, 70, 26, Y, Y2, Y3)
    for u in (0.2, 0.62):
        if nham:
            p.append(mat(u, 0.6, u + 0.18, 0.64, INK, 2))
        else:
            p.append(mat(u, 0.5, u + 0.18, 0.74, WHITE))
            p.append(mat(u + (0.02 if the == "nghi" else 0.06), 0.54, u + (0.1 if the == "nghi" else 0.12), 0.68, INK, 2))
    mieng = {"chao": (0.36, 0.26, 0.64, 0.34), "ngac-nhien": (0.43, 0.14, 0.57, 0.36), "nghi": (0.5, 0.28, 0.7, 0.31)}[the]
    p.append(mat(*mieng, INK, 2))
    if the in ("chao", "ngac-nhien"):
        p += arm(130, 70, 80) + box(128, 26, 148, 24, 24, 20, WHITE, LIGHT, MID)
    else:
        p += arm(130, 30, 40) + box(60, 92, 40, 40, 24, 18, WHITE, LIGHT, MID)
        p += box(52, 28, 190, 26, 26, 26, Y, Y2, Y3)
    return p


ITEMS = {
    "toa-nha-quoc-hoi": toa_nha_quoc_hoi, "dien-thoai": dien_thoai, "chip": chip, "laptop": laptop,
    "tien": tien, "tai-lieu": tai_lieu, "nha-may": nha_may, "may-chu": may_chu,
    "co-viet-nam": co_viet_nam, "bieu-do-nen": bieu_do_nen,
    "nen-dat": nen_dat, "cay": cay, "dong-xu": dong_xu, "mui-ten-len": mui_ten_len,
    "mui-ten-xuong": mui_ten_xuong, "container": container, "nguoi": nguoi,
    "wafer": wafer,
    "nha-may-duc": nha_may_duc,
    "phong-sach": phong_sach,
    "may-quang-khac": may_quang_khac,
    "chip-bao-mat": chip_bao_mat,
    "usb": usb,
    "o-khoa": o_khoa,
    "chia-khoa": chia_khoa,
    "khien": khien,
    "transistor": transistor,
    "soi-toc": soi_toc,
    "hat-gao": hat_gao,
    "san-bong": san_bong,
    "thuoc-do": thuoc_do,
    "dong-ho": dong_ho,
    "lich": lich,
    "trung-tam-du-lieu": trung_tam_du_lieu,
    "bo-nao-ai": bo_nao_ai,
    "robot": robot,
    "dam-may": dam_may,
    "pin": pin,
    "tia-set": tia_set,
    "tram-phat-song": tram_phat_song,
    "bong-bong": bong_bong,
    "do-thi-roi": do_thi_roi,
    "ket-sat": ket_sat,
    "the-ngan-hang": the_ngan_hang,
    "vi-tien": vi_tien,
    "can-cung-cau": can_cung_cau,
    "bua-phan-quyet": bua_phan_quyet,
    "ta-hang": ta_hang,
    "cang-bien": cang_bien,
    "oto": oto,
    "kinh-lup": kinh_lup,
    "ten-lua": ten_lua,
    "hop-thu": hop_thu,
    "thue-phan-tram": thue_phan_tram,
    "nguoi-nhom": nguoi_nhom,
    "tui-xach": tui_xach,
    "cao-oc": cao_oc,
    "tui-chao": lambda: tui("chao", False),
    "tui-chao-nham": lambda: tui("chao", True),
    "tui-ngac-nhien": lambda: tui("ngac-nhien", False),
    "tui-ngac-nhien-nham": lambda: tui("ngac-nhien", True),
    "tui-nghi": lambda: tui("nghi", False),
    "tui-nghi-nham": lambda: tui("nghi", True),
}

if __name__ == "__main__":
    for name, fn in ITEMS.items():
        save(name, fn())
    print(len(ITEMS), "svg")
