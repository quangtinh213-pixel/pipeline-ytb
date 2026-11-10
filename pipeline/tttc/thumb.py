"""Thumbnail 1280×720 theo brand: chữ đậm, tùy chọn ảnh nền (TobyFlow) được làm tối."""
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from tttc import theme



def _pal() -> dict:
    """Màu thumbnail lấy từ brand/theme.json mỗi lần gọi (đổi theme là đổi ngay)."""
    th = theme.TH
    return {"bg": theme.rgb(th["nen"]), "white": theme.rgb(th["muc"]), "yellow": theme.rgb(th["nhan"][0]),
            "ink": theme.rgb(th["chu_tren_nhan"])}


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
    out, p = Path(out), _pal()
    if background:
        img = ImageOps.fit(Image.open(background).convert("RGB"), (W, H))
        img = Image.blend(img, Image.new("RGB", (W, H), (0, 0, 0)), 0.55)  # tối 55% để chữ nổi
    else:
        img = Image.new("RGB", (W, H), p["bg"])
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
        d.text(((W - (b[2] - b[0])) / 2 - b[0], y - b[1]), text, font=f, fill=p[color])
        y += (b[3] - b[1]) + GAP
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    small = out.with_name(out.stem + "-168px" + out.suffix)
    img.resize((168, 94), Image.LANCZOS).save(small)
    return out, small




def khung_tu_video(video, t: float, out, bo_day: float = 0.0) -> Path:
    """Lấy một khung hình PNG từ video (vd cảnh minh họa đẹp nhất của final.mp4) làm nửa phải thumbnail.
    bo_day: tỉ lệ chiều cao cắt bỏ ở đáy, 0,12 để bỏ dải phụ đề đã in sẵn trong video."""
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(video), "-frames:v", "1",
                    *(["-vf", f"crop=iw:ih*{1 - bo_day}:0:0"] if bo_day else []), str(out)], check=True)
    return out


NHAN_VAT = Path(__file__).resolve().parent.parent / "nhan-vat" / "ngac-nhien-nghieng-trai.png"  # nhân vật đứng ở góc ô ảnh
BOX = (700, 100, 1220, 620)  # ô ảnh bên phải (rộng 520, cao 520)


def khung(anh_chinh: Path | None, anh_phu: Path, dong: list[str], out: Path, ghi_cong: str = "") -> tuple[Path, Path]:
    """Thumbnail khung của kênh Nhịp Công Nghệ: chữ lớn bên trái, ô ảnh bo góc viền màu nhấn bên phải, thanh nhấn dọc mép trái,
    nhân vật Nhịp đứng ở góc ô ảnh. anh_phu = ảnh trong ô (bắt buộc); anh_chinh (tuỳ chọn) = ảnh nền phủ kín, được làm tối;
    dong = 1–2 dòng chữ (dòng cuối tô màu nhấn); ghi_cong = chữ ghi công ảnh, góc dưới phải, tự cắt cho vừa. Màu lấy từ theme."""
    if not 1 <= len(dong) <= 2:
        raise ValueError("Thumbnail khung cần 1–2 dòng chữ")
    out, p = Path(out), _pal()
    img = Image.new("RGB", (W, H), p["bg"])
    if anh_chinh is not None:
        bg = ImageOps.fit(Image.open(anh_chinh).convert("RGB"), (W, H))
        img = Image.blend(bg, img, 0.62)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 17, H], fill=p["yellow"])
    x0, y0, x1, y1 = BOX
    m = Image.new("L", (x1 - x0, y1 - y0), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, x1 - x0 - 1, y1 - y0 - 1], 40, fill=255)
    img.paste(ImageOps.fit(Image.open(anh_phu).convert("RGB"), (x1 - x0, y1 - y0)), (x0, y0), m)
    d.rounded_rectangle([x0, y0, x1, y1], 40, outline=p["yellow"], width=10)
    f0 = min((fit_font(t, 600, 130) for t in dong), key=lambda f: f.size)  # cùng cỡ cho mọi dòng, vừa dòng dài nhất
    cao = d.textbbox((0, 0), "Ậg", font=f0)[3] + 26
    y = (H - cao * len(dong)) // 2 - 10
    for k, text in enumerate(dong):
        d.text((60, y + k * cao), text, font=f0, fill=p["yellow"] if k == len(dong) - 1 and len(dong) > 1 else p["white"])
    if NHAN_VAT.exists():
        c = Image.open(NHAN_VAT).convert("RGBA")
        c = c.resize((200, int(200 * c.height / c.width)))
        img.paste(c, (x1 - 150, y1 - c.height + 30), c)
    if ghi_cong:
        f = ImageFont.truetype(FONT, 18)
        while d.textlength(ghi_cong, font=f) > 400 and len(ghi_cong) > 1:
            ghi_cong = ghi_cong[:-2].rstrip() + "…"
        x = x0 + 4
        d.text((x + 1, y1 + 21), ghi_cong, font=f, fill=(0, 0, 0))
        d.text((x, y1 + 20), ghi_cong, font=f, fill=(255, 255, 255))
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    small = out.with_name(out.stem + "-168px" + out.suffix)
    img.resize((168, 94), Image.LANCZOS).save(small)
    return out, small
