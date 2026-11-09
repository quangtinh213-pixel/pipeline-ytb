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


BORDER, TEETH, TOOTH_AMP, CREDIT_W = 10, 7, 24, 460


def khung_tu_video(video, t: float, out, bo_day: float = 0.0) -> Path:
    """Lấy một khung hình PNG từ video (vd cảnh minh họa đẹp nhất của final.mp4) làm nửa phải thumbnail.
    bo_day: tỉ lệ chiều cao cắt bỏ ở đáy, 0,12 để bỏ dải phụ đề đã in sẵn trong video."""
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(video), "-frames:v", "1",
                    *(["-vf", f"crop=iw:ih*{1 - bo_day}:0:0"] if bo_day else []), str(out)], check=True)
    return out


def _zigzag() -> list[tuple[int, int]]:
    return [(640 + (TOOTH_AMP if i % 2 == 0 else -TOOTH_AMP), round(i * H / (2 * TEETH))) for i in range(2 * TEETH + 1)]


def chia_doi(trai: Path | None, phai: Path, dong: list[str], out: Path, ghi_cong: str = "",
             vs: bool = True) -> tuple[Path, Path]:
    """Thumbnail chia đôi khung bằng đường răng cưa: trái (chân dung CC có ghi công) – phải (vật/minh họa).
    trai=None thì cắt đôi ảnh phải thành hai nửa. Chữ tối đa 2 hộp vàng; ghi công nhỏ góc trên phải."""
    if not 1 <= len(dong) <= 2:
        raise ValueError("Thumbnail chia đôi cần 1–2 dòng chữ")
    out, p = Path(out), _pal()
    yellow, ink, bg = p["yellow"], p["ink"], p["bg"]
    zig = _zigzag()
    if trai is None:
        img = ImageOps.fit(Image.open(phai).convert("RGB"), (W, H))
    else:
        img = Image.new("RGB", (W, H), bg)
        img.paste(ImageOps.fit(Image.open(phai).convert("RGB"), (700, H)), (580, 0))
        left = Image.new("RGB", (W, H), bg)
        left.paste(ImageOps.fit(Image.open(trai).convert("RGB"), (700, H)), (0, 0))
        mask = Image.new("L", (W, H), 0)
        ImageDraw.Draw(mask).polygon([(0, 0), *zig, (0, H)], fill=255)
        img.paste(left, (0, 0), mask)
    d = ImageDraw.Draw(img)
    d.line(zig, fill=yellow, width=8, joint="curve")
    d.rectangle([0, 0, W - 1, H - 1], outline=yellow, width=BORDER)
    if vs:
        d.ellipse([640 - 62, 360 - 62, 640 + 62, 360 + 62], fill=yellow, outline=ink, width=6)
        f = font(64)
        b = d.textbbox((0, 0), "VS", font=f)
        d.text((640 - (b[0] + b[2]) / 2, 360 - (b[1] + b[3]) / 2), "VS", font=f, fill=ink)
    pad_x, pad_y, gap, y = 28, 14, 14, H - 44
    for text in reversed(dong):  # hộp dưới cùng vẽ trước, hộp trên xếp chồng lên
        f = fit_font(text, 1100 - 2 * pad_x, 110)
        b = d.textbbox((0, 0), text, font=f)
        tw, th = b[2] - b[0], b[3] - b[1]
        y -= th + 2 * pad_y
        d.rectangle([48, y, 48 + tw + 2 * pad_x, y + th + 2 * pad_y], fill=yellow)
        d.text((48 + pad_x - b[0], y + pad_y - b[1]), text, font=f, fill=ink)
        y -= gap
    if ghi_cong:
        f = ImageFont.truetype(FONT, 18)
        while d.textlength(ghi_cong, font=f) > CREDIT_W and len(ghi_cong) > 1:
            ghi_cong = ghi_cong[:-2].rstrip() + "…"
        x = W - BORDER - 14 - d.textlength(ghi_cong, font=f)
        d.text((x + 1, 23), ghi_cong, font=f, fill=(0, 0, 0))
        d.text((x, 22), ghi_cong, font=f, fill=(255, 255, 255))
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    small = out.with_name(out.stem + "-168px" + out.suffix)
    img.resize((168, 94), Image.LANCZOS).save(small)
    return out, small
