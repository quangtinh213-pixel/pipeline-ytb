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
