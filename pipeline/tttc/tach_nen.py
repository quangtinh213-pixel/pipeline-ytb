"""Tách nền phẳng của ảnh nhân vật (nền một màu do mô hình ảnh vẽ) và dựng bảng soi.

Dùng: uv run python -m tttc.tach_nen <ảnh vào> <png ra>      # một ảnh
      uv run python -m tttc.tach_nen soi <thư mục png> <bang.png>
shortcut: khoảng cách màu là hiệu lớn nhất giữa các kênh (không phải Euclid), nền phải phẳng và khác hẳn màu nhân vật; nền chuyển sắc hoặc nhân vật cùng màu nền thì cần công cụ khác.
"""
import statistics
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

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
    mask = alpha.point(lambda v: 255 if v > 8 else 0)
    box = mask.getbbox()
    if box is None:
        raise ValueError(f"{src}: không còn điểm ảnh đối tượng sau khi bỏ nền")
    box = _vat_chinh(mask, box)
    rgba = im.convert("RGBA")
    r, g, b = rgba.convert("RGB").split()
    rgba = Image.merge("RGB", (r, ImageChops.darker(g, ImageChops.lighter(r, b)), b)).convert("RGBA")  # khử viền xanh lá do nền
    rgba.putalpha(alpha)
    x0, y0, x1, y1 = box
    rgba = rgba.crop((max(0, x0 - LE), max(0, y0 - LE), min(w, x1 + LE), min(h, y1 + LE)))
    rgba = rgba.resize((max(1, round(rgba.width * cao / rgba.height)), cao), Image.LANCZOS)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    rgba.save(out)
    return Path(out)


def _vat_chinh(mask: Image.Image, box: tuple) -> tuple:
    """Hộp bao của vật chính: bỏ các đốm nhỏ rời xa (nhiễu của mô hình ảnh). Giữ thành phần lớn nhất và thành phần ≥ 4% của nó."""
    w, h = mask.size
    f = max(1, max(w, h) // 200)
    small = mask.resize((max(1, w // f), max(1, h // f)), Image.BOX).point(lambda v: 255 if v > 0 else 0)
    sw, sh = small.size
    px, seen, comps = small.load(), set(), []
    for y0 in range(sh):
        for x0 in range(sw):
            if px[x0, y0] and (x0, y0) not in seen:
                st, cells = [(x0, y0)], []
                seen.add((x0, y0))
                while st:
                    x, y = st.pop()
                    cells.append((x, y))
                    for dx in (-2, -1, 0, 1, 2):  # nối các mảnh cách nhau tới 2 ô nhỏ (ăng-ten, hào quang)
                        for dy in (-2, -1, 0, 1, 2):
                            q = (x + dx, y + dy)
                            if 0 <= q[0] < sw and 0 <= q[1] < sh and q not in seen and px[q]:
                                seen.add(q)
                                st.append(q)
                comps.append(cells)
    big = max(len(c) for c in comps)
    keep = [c for c in comps if len(c) >= 0.04 * big]
    xs = [x for c in keep for x, _ in c]
    ys = [y for c in keep for _, y in c]
    x0, y0, x1, y1 = min(xs) * f, min(ys) * f, (max(xs) + 1) * f, (max(ys) + 1) * f
    return (max(box[0], x0 - f), max(box[1], y0 - f), min(box[2], x1 + f), min(box[3], y1 + f))


def tao_nham(src: Path, out: Path, ty_le_mat: float = 0.55) -> Path:
    """Ảnh chớp mắt sinh từ chính ảnh mở mắt: tắt các nét sáng ở nửa trên màn hình tối (mắt), giữ miệng, ăng-ten và hình dáng.
    shortcut: màn hình = vùng tối lớn nhất (sau khi bào mòn nét viền); mắt = mọi điểm sáng hơn nền màn hình (và ít đỏ) ở 55% phía trên màn hình."""
    im = Image.open(src).convert("RGBA")
    rgb = im.convert("RGB")
    dark = Image.eval(rgb.convert("L"), lambda v: 255 if v < 70 else 0)
    dark = ImageChops.multiply(dark, im.getchannel("A").point(lambda v: 255 if v > 200 else 0))
    box = dark.filter(ImageFilter.MinFilter(9)).getbbox()
    if box is None:
        raise ValueError(f"{src}: không tìm thấy màn hình tối")
    x0, y0, x1, y1 = box
    sample = [rgb.getpixel((x, y)) for x in range(x0, x1, 4) for y in range(y0, y1, 4) if dark.getpixel((x, y))]
    man = tuple(sorted(c[k] for c in sample)[len(sample) // 2] for k in range(3))
    r, g, b = rgb.split()
    ml = int(0.299 * man[0] + 0.587 * man[1] + 0.114 * man[2])
    sang = ImageChops.multiply(rgb.convert("L").point(lambda v: 255 if v > ml + 18 else 0), r.point(lambda v: 255 if v < 150 else 0))  # sáng hơn nền màn hình, không phải viền trắng
    zone = Image.new("L", im.size, 0)
    ImageDraw.Draw(zone).rectangle([x0, y0, x1, y0 + int((y1 - y0) * ty_le_mat)], fill=255)
    tat = ImageChops.multiply(sang, zone)  # mắt cùng quầng sáng mờ quanh nó
    nen = Image.new("RGBA", im.size, man + (255,))
    nen.putalpha(im.getchannel("A"))
    res = Image.composite(nen, im, tat)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    res.save(out)
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
