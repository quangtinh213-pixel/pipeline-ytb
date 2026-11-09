"""Tách nền phẳng của ảnh nhân vật (nền một màu do mô hình ảnh vẽ) và dựng bảng soi.

Dùng: uv run python -m tttc.tach_nen <ảnh vào> <png ra>      # một ảnh
      uv run python -m tttc.tach_nen soi <thư mục png> <bang.png>
shortcut: khoảng cách màu là hiệu lớn nhất giữa các kênh (không phải Euclid), nền phải phẳng và khác hẳn màu nhân vật; nền chuyển sắc hoặc nhân vật cùng màu nền thì cần công cụ khác.
"""
import statistics
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

NEN_LECH_MAX = 30  # bốn góc chênh nhau hơn mức này (theo kênh) thì nền không phẳng
LE = 8


def tach_nen(src: Path, out: Path, nguong: int = 28, mem: int = 24, cao: int = 560) -> Path:
    im = Image.open(src).convert("RGB")
    w, h = im.size
    goc = [im.getpixel(p) for p in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1))]
    if max(max(c[k] for c in goc) - min(c[k] for c in goc) for k in range(3)) > NEN_LECH_MAX:
        raise ValueError(f"{src}: bốn góc ảnh khác màu nhau, nền không phẳng (cần nền một màu để tách)")
    bg = tuple(round(statistics.median(c[k] for c in goc)) for k in range(3))
    r, g, b = ImageChops.difference(im, Image.new("RGB", im.size, bg)).split()
    d = ImageChops.lighter(ImageChops.lighter(r, g), b)
    alpha = d.point(lambda v: 0 if v <= nguong else min(255, round((v - nguong) / mem * 255)))
    box = alpha.point(lambda v: 255 if v > 8 else 0).getbbox()
    if box is None:
        raise ValueError(f"{src}: không còn điểm ảnh đối tượng sau khi bỏ nền")
    rgba = im.convert("RGBA")
    rgba.putalpha(alpha)
    x0, y0, x1, y1 = box
    rgba = rgba.crop((max(0, x0 - LE), max(0, y0 - LE), min(w, x1 + LE), min(h, y1 + LE)))
    rgba = rgba.resize((max(1, round(rgba.width * cao / rgba.height)), cao), Image.LANCZOS)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    rgba.save(out)
    return Path(out)


def bang_soi(thu_muc: Path, out: Path, cot: int = 6) -> Path:
    """Lưới các PNG trong thư mục, mỗi ô trên nền ca-rô kèm tên tệp (để soi viền, độ phủ nền)."""
    files = sorted(f for f in Path(thu_muc).glob("*.png") if f.resolve() != Path(out).resolve())
    ow, oh = 200, 280
    rows = max(1, -(-len(files) // cot))
    sheet = Image.new("RGB", (cot * ow, rows * (oh + 18)), (60, 60, 60))
    for i, f in enumerate(files):
        x, y = (i % cot) * ow, (i // cot) * (oh + 18)
        tile = Image.new("RGB", (ow, oh), (200, 200, 200))
        dr = ImageDraw.Draw(tile)
        for cy in range(0, oh, 20):
            for cx in range(0, ow, 20):
                if (cx // 20 + cy // 20) % 2:
                    dr.rectangle([cx, cy, cx + 19, cy + 19], fill=(150, 150, 150))
        im = Image.open(f).convert("RGBA")
        im.thumbnail((ow - 12, oh - 12))
        tile.paste(im, ((ow - im.width) // 2, (oh - im.height) // 2), im)
        sheet.paste(tile, (x, y))
        ImageDraw.Draw(sheet).text((x + 4, y + oh + 3), f.stem, fill=(255, 255, 255))
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    return Path(out)


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) == 3 and a[0] == "soi":
        print(bang_soi(Path(a[1]), Path(a[2])))
    elif len(a) == 2:
        print(tach_nen(Path(a[0]), Path(a[1])))
    else:
        sys.exit("dùng: python -m tttc.tach_nen <ảnh> <png ra>  |  python -m tttc.tach_nen soi <thư mục> <bang.png>")
