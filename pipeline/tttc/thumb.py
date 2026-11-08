"""Thumbnail 1280×720 theo brand: chữ đậm, tùy chọn ảnh nền (TobyFlow) được làm tối."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

BG, COLORS = (17, 17, 17), {"white": (255, 255, 255), "yellow": (255, 200, 0)}
FONT = "/System/Library/Fonts/SFNS.ttf"  # SF Pro, có dấu tiếng Việt (giống brand/make_brand.py)
W, H, MAX_W, MAX_H, GAP = 1280, 720, 1200, 640, 28  # GAP rộng cho dấu tiếng Việt


def font(size: int) -> ImageFont.FreeTypeFont:
    f = ImageFont.truetype(FONT, size)
    try:
        f.set_variation_by_name("Heavy")
    except Exception:
        pass  # bản font không có biến thể thì dùng mặc định
    return f


def fit_font(text: str, max_w: int, start: int) -> ImageFont.FreeTypeFont:
    d, size = ImageDraw.Draw(Image.new("RGB", (1, 1))), start
    while size > 20 and d.textlength(text, font=font(size)) > max_w:
        size -= 6
    return font(size)


def make(lines: list[tuple[str, str]], out: Path, background: Path | None = None) -> tuple[Path, Path]:
    out = Path(out)
    if background:
        img = ImageOps.fit(Image.open(background).convert("RGB"), (W, H))
        img = Image.blend(img, Image.new("RGB", (W, H), (0, 0, 0)), 0.55)  # tối 55% để chữ nổi
    else:
        img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    fonts = [fit_font(t, MAX_W, 300) for t, _ in lines]
    boxes = [d.textbbox((0, 0), t, font=f) for (t, _), f in zip(lines, fonts)]
    total = sum(b[3] - b[1] for b in boxes) + GAP * (len(lines) - 1)
    if total > MAX_H:  # nhiều dòng: thu nhỏ đều cho vừa chiều cao
        k = MAX_H / total
        fonts = [font(max(20, int(f.size * k))) for f in fonts]
        boxes = [d.textbbox((0, 0), t, font=f) for (t, _), f in zip(lines, fonts)]
        total = sum(b[3] - b[1] for b in boxes) + GAP * (len(lines) - 1)
    y = (H - total) / 2
    for (text, color), f, b in zip(lines, fonts, boxes):
        d.text(((W - (b[2] - b[0])) / 2 - b[0], y - b[1]), text, font=f, fill=COLORS[color])
        y += (b[3] - b[1]) + GAP
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    small = out.with_name(out.stem + "-168px" + out.suffix)
    img.resize((168, 94), Image.LANCZOS).save(small)
    return out, small
