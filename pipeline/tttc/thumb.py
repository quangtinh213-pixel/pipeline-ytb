"""Thumbnail 1280×720 theo brand: chữ đậm, tùy chọn ảnh nền (TobyFlow) được làm tối."""
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

from tttc import theme



def _pal() -> dict:
    """Màu thumbnail lấy từ brand/theme.json mỗi lần gọi (đổi theme là đổi ngay)."""
    th = theme.TH
    return {"bg": theme.rgb(th["nen"]), "white": theme.rgb(th["muc"]), "yellow": theme.rgb(th["nhan"][0]),
            "ink": theme.rgb(th["chu_tren_nhan"])}


def _accent(p: dict, sac: str | None) -> tuple[int, int, int]:
    """Chọn màu nhấn theo sắc thái tin (do, xanh, lam, tim) hoặc màu nhấn mặc định của theme."""
    if sac and sac in theme.TH.get("sac", {}):
        return theme.rgb(theme.TH["sac"][sac][0])
    return p["yellow"]


# SF Pro trên Mac, Segoe UI Black trên Windows; cả hai có dấu tiếng Việt (giống brand/make_brand.py)
FONT = next((f for f in ("/System/Library/Fonts/SFNS.ttf", "C:/Windows/Fonts/seguibl.ttf") if Path(f).exists()),
           "/System/Library/Fonts/SFNS.ttf")
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


def make(lines: list[tuple[str, str]], out: Path, background: Path | None = None,
         sac: str | None = None) -> tuple[Path, Path]:
    out, p = Path(out), _pal()
    accent = _accent(p, sac)
    if background:
        img = ImageOps.fit(Image.open(background).convert("RGB"), (W, H))
        img = Image.blend(img, Image.new("RGB", (W, H), (0, 0, 0)), 0.55)  # tối 55% để chữ nổi
    else:
        img = Image.new("RGB", (W, H), p["bg"])
    d = ImageDraw.Draw(img)
    stroke = 4
    fonts = [fit_font(t, MAX_W - stroke * 2, 300) for t, _ in lines]
    boxes = [d.textbbox((0, 0), t, font=f, stroke_width=stroke) for (t, _), f in zip(lines, fonts)]
    total = sum(b[3] - b[1] for b in boxes) + GAP * (len(lines) - 1)
    if total > MAX_H:  # nhiều dòng: thu nhỏ đều cho vừa chiều cao
        gaps = GAP * (len(lines) - 1)  # khoảng cách dòng không co theo cỡ chữ, chỉ chia phần chữ
        k = (MAX_H - gaps) / (total - gaps)
        fonts = [font(max(20, int(f.size * k))) for f in fonts]
        boxes = [d.textbbox((0, 0), t, font=f, stroke_width=stroke) for (t, _), f in zip(lines, fonts)]
        total = sum(b[3] - b[1] for b in boxes) + GAP * (len(lines) - 1)
    y = (H - total) / 2
    for (text, color), f, b in zip(lines, fonts, boxes):
        fill = accent if color == "yellow" else p[color]
        d.text(((W - (b[2] - b[0])) / 2 - b[0], y - b[1]), text, font=f, fill=fill,
               stroke_width=stroke, stroke_fill=p["ink"])
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


def khung(anh_chinh: Path | None, anh_phu: Path, dong: list[str], out: Path, ghi_cong: str = "",
          sac: str | None = None) -> tuple[Path, Path]:
    """Thumbnail khung của kênh Nhịp Công Nghệ: chữ lớn bên trái, ô ảnh bo góc viền màu nhấn bên phải, thanh nhấn dọc mép trái,
    nhân vật Nhịp đứng ở góc ô ảnh. anh_phu = ảnh trong ô (bắt buộc); anh_chinh (tuỳ chọn) = ảnh nền phủ kín, được làm tối;
    dong = 1–2 dòng chữ (dòng cuối tô màu nhấn theo sac hoặc mặc định); ghi_cong = chữ ghi công ảnh ở góc dưới trái
    (tránh badge thời lượng góc dưới phải). Màu lấy từ theme."""
    if not 1 <= len(dong) <= 2:
        raise ValueError("Thumbnail khung cần 1–2 dòng chữ")
    out, p = Path(out), _pal()
    accent = _accent(p, sac)
    img = Image.new("RGB", (W, H), p["bg"])
    if anh_chinh is not None:
        bg = ImageOps.fit(Image.open(anh_chinh).convert("RGB"), (W, H))
        img = Image.blend(bg, img, 0.62)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 17, H], fill=accent)
    x0, y0, x1, y1 = BOX
    m = Image.new("L", (x1 - x0, y1 - y0), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, x1 - x0 - 1, y1 - y0 - 1], 40, fill=255)
    img.paste(ImageOps.fit(Image.open(anh_phu).convert("RGB"), (x1 - x0, y1 - y0)), (x0, y0), m)
    d.rounded_rectangle([x0, y0, x1, y1], 40, outline=accent, width=10)
    f0 = min((fit_font(t, 600, 130) for t in dong), key=lambda f: f.size)  # cùng cỡ cho mọi dòng, vừa dòng dài nhất
    cao = d.textbbox((0, 0), "Ậg", font=f0)[3] + 26
    y = (H - cao * len(dong)) // 2 - 10
    for k, text in enumerate(dong):
        d.text((60, y + k * cao), text, font=f0, fill=accent if k == len(dong) - 1 and len(dong) > 1 else p["white"],
               stroke_width=4, stroke_fill=p["ink"])
    if NHAN_VAT.exists():
        c = Image.open(NHAN_VAT).convert("RGBA")
        c = c.resize((200, int(200 * c.height / c.width)))
        img.paste(c, (x1 - 150, y1 - c.height + 30), c)
    if ghi_cong:
        f = ImageFont.truetype(FONT, 18)
        while d.textlength(ghi_cong, font=f) > 400 and len(ghi_cong) > 1:
            ghi_cong = ghi_cong[:-2].rstrip() + "…"
        d.text((61, H - 35), ghi_cong, font=f, fill=(0, 0, 0))
        d.text((60, H - 36), ghi_cong, font=f, fill=(255, 255, 255))
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    small = out.with_name(out.stem + "-168px" + out.suffix)
    img.resize((168, 94), Image.LANCZOS).save(small)
    return out, small


# Khuôn thumbnail đã khóa cho mọi video dài (người dùng chốt 15/11/2026, docs/nghien-cuu/de-xuat-phat-trien-2026-11-15.md mục 5).
# Ba phương án chỉ khác chữ và ảnh, không khác khuôn. Cố ý khác khuôn kênh mẫu: nền giấy sáng, không viền cam/vàng,
# không tia chia đôi, không hộp vàng chữ đen.
KHUON = "ho-so"
NHAN_VAT_HO_SO = Path(__file__).resolve().parent.parent / "nhan-vat" / "nghi-nghieng-phai.png"
THE = (560, 470)  # ảnh dán (gồm viền trắng 20 px), xoay nhẹ
GOC_THE = (668, 108)


def ho_so(anh: Path, nhan: str, so: str, hoi: str, out: Path, ghi_cong: str = "",
          tam: tuple[float, float] = (0.5, 0.4)) -> tuple[Path, Path]:
    """Thumbnail khuôn «hồ sơ»: nền giấy kem kẻ dòng, bên trái ba tầng chữ mực (nhan = chủ thể/sự kiện ≤ 3 từ,
    so = con số làm chính có gạch đỏ dưới, hoi = một câu hỏi), bên phải ảnh dán viền trắng xoay nhẹ có băng keo,
    nhân vật Nhịp ở góc dưới trái ảnh. tam = điểm giữ khi cắt ảnh (0–1, ngang/dọc). Màu lấy từ theme (kem, sac.do)."""
    if not so.strip() or not hoi.strip():
        raise ValueError("Khuôn hồ sơ cần con số (so) và một câu hỏi (hoi)")
    out, kem = Path(out), theme.TH["kem"]
    nen, ke, muc = theme.rgb(kem["nen"]), theme.rgb(kem["nen_2"]), theme.rgb(kem["muc"])
    do, keo = theme.rgb(theme.TH["sac"]["do"][0]), theme.rgb(kem["duong"])
    img = Image.new("RGB", (W, H), nen)
    d = ImageDraw.Draw(img)
    for y in range(36, H, 36):
        d.line([(0, y), (W, y)], fill=ke, width=1)

    tw, th_ = THE
    the = Image.new("RGBA", THE, (255, 255, 255, 255))
    the.paste(ImageOps.fit(Image.open(anh).convert("RGB"), (tw - 40, th_ - 40), centering=tam), (20, 20))
    the = the.rotate(-4, expand=True, resample=Image.BICUBIC)
    bong = Image.new("RGBA", the.size, (0, 0, 0, 0))
    bong.paste((0, 0, 0, 90), mask=the.split()[3])
    bong = bong.filter(ImageFilter.GaussianBlur(14))
    gx, gy = GOC_THE
    img.paste(bong, (gx + 12, gy + 16), bong)
    img.paste(the, (gx, gy), the)
    d = ImageDraw.Draw(img)
    cx = gx + the.size[0] // 2
    d.polygon([(cx - 75, gy - 12), (cx + 75, gy), (cx + 70, gy + 40), (cx - 80, gy + 28)], fill=keo)

    x, rong = 60, 590
    tang = [(t, fit_font(t, rong, c), k) for t, c, k in ((nhan, 66, "nhan"), (so, 180, "so"), (hoi, 104, "hoi")) if t.strip()]
    hop = [d.textbbox((0, 0), t, font=f) for t, f, _ in tang]
    cach = {"so": 24, "hoi": 64}  # khoảng trên mỗi tầng; dưới con số chừa chỗ gạch đỏ
    tong = sum(b[3] - b[1] for b in hop) + sum(cach.get(k, 0) for _, _, k in tang[1:])
    y = (H - tong) // 2 - 10  # cả khối chữ căn giữa theo chiều dọc
    for i, ((t, f, k), b) in enumerate(zip(tang, hop)):
        y += cach.get(k, 0) if i else 0
        if k == "so":
            d.rectangle([x + b[0], y + b[3] - b[1] - 22, x + b[2], y + b[3] - b[1] + 6], fill=do)
        d.text((x - b[0], y - b[1]), t, font=f, fill=muc)
        y += b[3] - b[1]

    if NHAN_VAT_HO_SO.exists():
        c = Image.open(NHAN_VAT_HO_SO).convert("RGBA")
        c = c.resize((150, int(150 * c.height / c.width)))
        img.paste(c, (gx - 50, H - 25 - c.height), c)
    if ghi_cong:
        f = ImageFont.truetype(FONT, 18)
        while d.textlength(ghi_cong, font=f) > 300 and len(ghi_cong) > 1:
            ghi_cong = ghi_cong[:-2].rstrip() + "…"
        d.text((gx + 130, H - 36), ghi_cong, font=f, fill=muc)  # tránh badge thời lượng ở góc dưới phải
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    small = out.with_name(out.stem + "-168px" + out.suffix)
    img.resize((168, 94), Image.LANCZOS).save(small)
    return out, small
