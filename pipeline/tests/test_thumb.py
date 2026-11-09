from PIL import Image, ImageStat

from tttc import thumb


def test_make_sizes(tmp_path):
    big, small = thumb.make([("BẢN FREE", "white"), ("ĐỦ?", "yellow")], tmp_path / "t.png")
    assert Image.open(big).size == (1280, 720)
    assert Image.open(small).size == (168, 94)


def test_make_uses_brand_colors(tmp_path):
    big, _ = thumb.make([("ĐỦ?", "yellow")], tmp_path / "t.png")
    colors = {c for _, c in Image.open(big).convert("RGB").getcolors(1_000_000)}
    assert (17, 17, 17) in colors and (255, 200, 0) in colors


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


def test_chia_doi_sizes(tmp_path):
    big, small = thumb.chia_doi(_solid(tmp_path / "l.png", (0, 160, 0)), _solid(tmp_path / "r.png", (30, 30, 30)),
                                DONG, tmp_path / "t.png")
    assert Image.open(big).size == (1280, 720) and Image.open(small).size == (168, 94)


def test_chia_doi_uses_left_image_on_left(tmp_path):
    big, _ = thumb.chia_doi(_solid(tmp_path / "l.png", (0, 160, 0)), _solid(tmp_path / "r.png", (30, 30, 30)),
                            DONG, tmp_path / "t.png")
    img = Image.open(big).convert("RGB")
    assert img.getpixel((150, 150))[1] > 120 and img.getpixel((1150, 150)) == (30, 30, 30)


def test_chia_doi_uses_brand_yellow_in_label_area(tmp_path):
    _, small = thumb.chia_doi(_solid(tmp_path / "l.png", (0, 0, 0)), _solid(tmp_path / "r.png", (0, 0, 0)),
                              DONG, tmp_path / "t.png")
    bottom = Image.open(small).convert("RGB").crop((0, 66, 168, 94))
    px = bottom.load()
    yellow = sum(1 for x in range(168) for y in range(28) if px[x, y][0] > 200 and px[x, y][1] > 150 and px[x, y][2] < 80)
    assert yellow / (168 * 28) >= 0.12


def test_chia_doi_without_left_image_splits_right_image(tmp_path):
    big, _ = thumb.chia_doi(None, _halves(tmp_path / "r.png"), DONG, tmp_path / "t.png")
    img = Image.open(big).convert("RGB")
    assert img.getpixel((200, 150))[0] > 150 and img.getpixel((1100, 150))[2] > 150


def test_chia_doi_long_credit_stays_inside(tmp_path):
    black = _solid(tmp_path / "r.png", (0, 0, 0))
    big, _ = thumb.chia_doi(None, black, DONG, tmp_path / "t.png", ghi_cong="Ảnh: " + "Nguyễn Văn A " * 20)
    g = Image.open(big).convert("L")
    assert g.crop((680, 22, 790, 50)).getextrema()[1] < 100  # chữ ghi công không tràn sang trái vùng 460 px
    assert g.crop((800, 22, 1262, 50)).getextrema()[1] > 200  # nhưng có hiện chữ


def test_chia_doi_rejects_more_than_two_lines(tmp_path):
    import pytest
    with pytest.raises(ValueError):
        thumb.chia_doi(None, _solid(tmp_path / "r.png", (0, 0, 0)), ["A", "B", "C"], tmp_path / "t.png")


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


def test_chia_doi_takes_accent_from_theme(tmp_path, monkeypatch):
    from tttc import theme
    monkeypatch.setattr(theme, "TH", {**theme.TH, "nhan": ["#00AAFF", "#0088CC", "#006699"]})
    right = tmp_path / "r.png"
    Image.new("RGB", (400, 400), (40, 40, 40)).save(right)
    big, _ = thumb.chia_doi(None, right, ["MỘT"], tmp_path / "c.png")
    assert Image.open(big).getpixel((3, 3)) == (0, 170, 255)  # viền khung theo màu nhấn của theme
