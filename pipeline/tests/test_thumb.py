from PIL import Image, ImageStat

from tttc import theme, thumb


def test_make_sizes(tmp_path):
    big, small = thumb.make([("BẢN FREE", "white"), ("ĐỦ?", "yellow")], tmp_path / "t.png")
    assert Image.open(big).size == (1280, 720)
    assert Image.open(small).size == (168, 94)


def test_make_uses_brand_colors(tmp_path):
    big, _ = thumb.make([("ĐỦ?", "yellow")], tmp_path / "t.png")
    colors = {c for _, c in Image.open(big).convert("RGB").getcolors(1_000_000)}
    assert theme.rgb(theme.TH["nen"]) in colors and theme.rgb(theme.TH["nhan"][0]) in colors


def test_make_with_background_darkens(tmp_path):
    bg = tmp_path / "bg.png"
    Image.new("RGB", (1600, 1200), (240, 240, 240)).save(bg)
    big, _ = thumb.make([("X", "white")], tmp_path / "t.png", background=bg)
    corner = Image.open(big).convert("L").crop((0, 0, 120, 120))
    assert ImageStat.Stat(corner).mean[0] <= 0.45 * 240


def test_text_fits_width():
    f = thumb.fit_font("GIÁ CHATGPT PLUS Ở VIỆT NAM HÔM NAY", 1200, 300)
    from PIL import ImageDraw
    w = ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength("GIÁ CHATGPT PLUS Ở VIỆT NAM HÔM NAY", font=f)
    assert w <= 1200 and f.size < 300


def test_lines_fit_height(tmp_path):
    big, _ = thumb.make([("A", "white")] * 6, tmp_path / "t.png")
    img = Image.open(big).convert("L")
    assert ImageStat.Stat(img.crop((0, 0, 1280, 20))).mean[0] < 30  # mép trên không bị chữ tràn
    assert ImageStat.Stat(img.crop((0, 700, 1280, 720))).mean[0] < 30


def _solid(path, color, size=(1280, 720)):
    Image.new("RGB", size, color).save(path)
    return path


def _halves(path):
    img = Image.new("RGB", (1280, 720), (200, 0, 0))
    img.paste((0, 0, 200), (640, 0, 1280, 720))
    img.save(path)
    return path


DONG = ["VIETTEL ĐANG LÀM ĐIỀU", "MÀ NVIDIA CHƯA DÁM LÀM?"]








def test_khung_tu_video_returns_png(tmp_path):
    import subprocess
    mp4 = tmp_path / "v.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=blue:s=320x180:d=2",
                    "-pix_fmt", "yuv420p", str(mp4)], check=True)
    out = thumb.khung_tu_video(mp4, 1.0, tmp_path / "k.png")
    assert out == tmp_path / "k.png" and Image.open(out).size == (320, 180)


def test_khung_tu_video_can_crop_bottom_band_off(tmp_path):
    import subprocess
    mp4 = tmp_path / "v.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=blue:s=320x180:d=2",
                    "-pix_fmt", "yuv420p", str(mp4)], check=True)
    h = Image.open(thumb.khung_tu_video(mp4, 1.0, tmp_path / "k.png", bo_day=0.12)).size[1]
    assert abs(h - 158) <= 2  # cắt dải phụ đề đã in sẵn ở đáy video


def test_make_takes_colours_from_theme(tmp_path, monkeypatch):
    from tttc import theme
    monkeypatch.setattr(theme, "TH", {**theme.TH, "nen": "#0A0B0C"})
    big, _ = thumb.make([("A", "white")], tmp_path / "t.png")
    assert Image.open(big).getpixel((0, 0)) == (10, 11, 12)


def test_khung_makes_1280x720_and_168px_and_validates_lines(tmp_path):
    import pytest
    a = tmp_path / "a.png"
    Image.new("RGB", (800, 800), (40, 40, 40)).save(a)
    big, small = thumb.khung(None, a, ["MỘT", "HAI"], tmp_path / "t.png", "Ảnh: X")
    assert Image.open(big).size == (1280, 720) and Image.open(small).size == (168, 94)
    with pytest.raises(ValueError):
        thumb.khung(None, a, ["A", "B", "C"], tmp_path / "t2.png")
    with pytest.raises(ValueError):
        thumb.khung(None, a, [], tmp_path / "t3.png")


def test_khung_puts_photo_in_right_box_accent_bar_on_left_and_text_on_left(tmp_path):
    a = tmp_path / "a.png"
    Image.new("RGB", (800, 800), (200, 60, 60)).save(a)
    big, _ = thumb.khung(None, a, ["VIỆT NAM", "ĐÃ CÓ TÊN?"], tmp_path / "t.png")
    img = Image.open(big).convert("RGB")
    assert img.getpixel((960, 320)) == (200, 60, 60)                          # ảnh nằm trong ô bên phải
    assert img.getpixel((8, 360)) == theme.rgb(theme.TH["nhan"][0])           # thanh nhấn dọc mép trái theo theme
    assert img.getpixel((10, 700)) != img.getpixel((960, 320))                 # nền ngoài ô là màu nền, không phải ảnh
    left = img.crop((40, 60, 680, 660)).convert("L")
    assert left.getextrema()[1] > 220                                          # có chữ sáng ở nửa trái


def test_khung_background_photo_is_darkened_and_credit_stays_inside(tmp_path, monkeypatch):
    monkeypatch.setattr(thumb, "NHAN_VAT", tmp_path / "khong-co.png")  # tách nhân vật ra để chỉ đo chữ ghi công
    a, bg = tmp_path / "a.png", tmp_path / "bg.png"
    Image.new("RGB", (800, 800), (40, 40, 40)).save(a)
    Image.new("RGB", (1600, 900), (250, 250, 250)).save(bg)
    big, _ = thumb.khung(bg, a, ["MỘT"], tmp_path / "t.png", ghi_cong="Ảnh: " + "Nguyễn Văn A " * 30)
    img = Image.open(big).convert("RGB")
    assert max(img.getpixel((640, 20))) < 140  # ảnh nền sáng bị làm tối
    g = img.convert("L")
    assert g.crop((1110, 630, 1280, 720)).getextrema()[1] < 140  # chữ ghi công (căn trái dưới ô ảnh, ≤ 400 px) không tràn sang phải


def test_khung_takes_accent_and_background_from_theme(tmp_path, monkeypatch):
    monkeypatch.setattr(theme, "TH", {**theme.TH, "nhan": ["#00AAFF", "#0088CC", "#006699"], "nen": "#0A0B0C"})
    a = tmp_path / "a.png"
    Image.new("RGB", (400, 400), (40, 40, 40)).save(a)
    big, _ = thumb.khung(None, a, ["MỘT"], tmp_path / "c.png")
    img = Image.open(big).convert("RGB")
    assert img.getpixel((8, 360)) == (0, 170, 255) and img.getpixel((300, 700)) == (10, 11, 12)

