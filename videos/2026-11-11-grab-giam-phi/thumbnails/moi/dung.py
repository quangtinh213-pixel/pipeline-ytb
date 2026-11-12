"""Thumbnail mới cho video Grab: nền cảnh tài xế (cắt từ ảnh AI của user), tài xế ngạc nhiên bên phải, chữ bên trái."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps, ImageEnhance

SRC = Path("/Users/quangtinh/Downloads/youtube-thumbnail-landscape-169.jpg")
OUT = Path("/Users/quangtinh/Documents/Youtube/videos/2026-11-11-grab-giam-phi/thumbnails/moi")
W, H = 1280, 720
FONT = "/System/Library/Fonts/SFNS.ttf"
YEL, WHITE, RED, GREEN = (255, 214, 0), (255, 255, 255), (230, 30, 40), (0, 177, 79)


def font(size):
    f = ImageFont.truetype(FONT, size)
    f.set_variation_by_name("Heavy")
    return f


def fit(text, max_w, start):
    d, s = ImageDraw.Draw(Image.new("RGB", (1, 1))), start
    while d.textlength(text, font=font(s)) > max_w:
        s -= 4
    return font(s)


def xoa_chu(im):
    """Xoá chữ vàng/đỏ in sẵn trong ảnh gốc: tô lại bằng màu tối mờ."""
    from PIL import ImageChops
    r, g, b = im.split()
    th = lambda ch, f: ch.point(lambda v: 255 if f(v) else 0)
    vang = ImageChops.multiply(ImageChops.multiply(th(r, lambda v: v > 170), th(g, lambda v: v > 140)), th(b, lambda v: v < 110))
    do = ImageChops.multiply(ImageChops.multiply(th(r, lambda v: v > 150), th(g, lambda v: v < 90)), th(b, lambda v: v < 90))
    vung = Image.new("L", im.size, 0)  # chỉ xoá ở vùng có chữ, không đụng mặt tài xế
    vd = ImageDraw.Draw(vung)
    vd.rectangle([0, 0, im.width, 262], fill=255)
    vd.rectangle([0, 0, 928, 335], fill=255)
    vd.rectangle([0, 495, im.width, im.height], fill=255)
    m = ImageChops.multiply(ImageChops.lighter(vang, do), vung).filter(ImageFilter.MaxFilter(15))
    im = im.copy()
    im.paste(Image.new("RGB", im.size, (6, 30, 18)), (0, 0), m.filter(ImageFilter.GaussianBlur(6)))
    return im


def base():
    src = xoa_chu(Image.open(SRC).convert("RGB"))
    # nền: đoàn tài xế bên trái, làm mờ + tối
    bg = ImageOps.fit(src.crop((0, 300, 760, 520)), (W, H)).filter(ImageFilter.GaussianBlur(6))
    bg = ImageEnhance.Brightness(bg).enhance(0.35)
    # phủ gradient xanh đậm từ trái
    grad = Image.new("L", (W, 1))
    for x in range(W):
        grad.putpixel((x, 0), int(235 * max(0, 1 - x / 900)))
    bg.paste(Image.new("RGB", (W, H), (4, 28, 16)), (0, 0), grad.resize((W, H)))
    # tài xế ngạc nhiên bên phải, mép trái mờ dần
    p = src.crop((740, 180, 1168, 505))
    ph = 600
    p = p.resize((int(p.width * ph / p.height), ph), Image.LANCZOS)
    p = ImageEnhance.Contrast(p).enhance(1.12)
    m = Image.new("L", p.size, 255)
    md = ImageDraw.Draw(m)
    for x in range(160):
        md.line([(x, 0), (x, p.height)], fill=int(255 * x / 160))
    for y in range(80):
        md.line([(0, y), (p.width, y)], fill=None)
    m = m.filter(ImageFilter.GaussianBlur(4))
    bg.paste(p, (W - p.width + 30, H - ph), m)
    return bg


def text(d, xy, s, f, fill, stroke=8):
    d.text(xy, s, font=f, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))


def save(img, name):
    OUT.mkdir(parents=True, exist_ok=True)
    img.save(OUT / f"{name}.png")
    img.resize((168, 94), Image.LANCZOS).save(OUT / f"{name}-168px.png")
    img.resize((320, 180), Image.LANCZOS).save(OUT / f"{name}-320px.png")


def a():  # 3.000 TỶ gạch -> 227 TỶ
    img = base(); d = ImageDraw.Draw(img)
    f1 = font(118)
    text(d, (50, 70), "3.000 TỶ", f1, WHITE)
    b = d.textbbox((50, 70), "3.000 TỶ", font=f1)
    d.line([(b[0] - 10, (b[1] + b[3]) // 2 + 8), (b[2] + 10, (b[1] + b[3]) // 2 - 8)], fill=RED, width=16)
    f2 = font(80)
    text(d, (55, 240), "GIẢM PHÍ THẬT", f2, WHITE)
    f3 = font(190)
    text(d, (40, 360), "227 TỶ?", f3, YEL, 10)
    save(img, "A-227-ty")


def b():  # 60% là mã giảm giá
    img = base(); d = ImageDraw.Draw(img)
    f1 = font(270)
    text(d, (40, 40), "60%", f1, YEL, 12)
    f2 = font(96)
    text(d, (50, 380), "LÀ MÃ", f2, WHITE)
    text(d, (50, 500), "GIẢM GIÁ?", f2, WHITE)
    save(img, "B-60-ma-giam-gia")


def c():  # Từ 26/02 trả nhiều hơn
    img = base(); d = ImageDraw.Draw(img)
    # nhãn đỏ ngày
    f1 = font(84)
    t = "TỪ 26/02"
    bb = d.textbbox((0, 0), t, font=f1)
    d.rounded_rectangle([40, 70, 40 + bb[2] + 50, 70 + bb[3] + 40], 18, fill=RED)
    d.text((65, 80), t, font=f1, fill=WHITE)
    f2 = font(150)
    text(d, (45, 260), "TRẢ", f2, WHITE, 10)
    text(d, (45, 430), "NHIỀU HƠN?", fit("NHIỀU HƠN?", 760, 150), YEL, 10)
    save(img, "C-26-02-tra-nhieu-hon")


if __name__ == "__main__":
    for fn in sys.argv[1:] or "abc":
        globals()[fn]()
