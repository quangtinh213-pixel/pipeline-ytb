import pytest
from PIL import Image, ImageDraw

from tttc import tach_nen


def _img(tmp_path, bg=(10, 200, 10)):
    im = Image.new("RGB", (200, 300), bg)
    ImageDraw.Draw(im).ellipse([60, 80, 140, 220], fill=(255, 200, 0), outline=(17, 17, 17), width=6)
    p = tmp_path / "a.png"
    im.save(p)
    return p


def test_tach_nen_makes_background_transparent_and_crops_and_resizes(tmp_path):
    out = tach_nen.tach_nen(_img(tmp_path), tmp_path / "o.png", cao=560)
    im = Image.open(out)
    assert im.mode == "RGBA" and im.height == 560
    assert im.getpixel((0, 0))[3] == 0 and im.getpixel((im.width // 2, im.height // 2))[3] == 255
    assert im.width < 560  # đã cắt sát đối tượng hình elip, không còn khung 200×300 nguyên


def test_tach_nen_rejects_non_flat_background(tmp_path):
    im = Image.new("RGB", (100, 100), (0, 0, 0))
    for xy in [(99, 99), (0, 99), (99, 0)]:  # ba góc trắng, một góc đen: nền không phẳng
        im.putpixel(xy, (255, 255, 255))
    im.save(tmp_path / "b.png")
    with pytest.raises(ValueError, match="nền"):
        tach_nen.tach_nen(tmp_path / "b.png", tmp_path / "o.png")


def test_tach_nen_rejects_empty_subject(tmp_path):
    Image.new("RGB", (100, 100), (5, 5, 5)).save(tmp_path / "c.png")
    with pytest.raises(ValueError, match="đối tượng"):
        tach_nen.tach_nen(tmp_path / "c.png", tmp_path / "o.png")


def test_bang_soi_one_tile_per_png(tmp_path):
    for n in ("chao-truoc", "nghi-ngang"):
        Image.new("RGBA", (50, 80), (255, 0, 0, 255)).save(tmp_path / f"{n}.png")
    assert Image.open(tach_nen.bang_soi(tmp_path, tmp_path / "bang.png", cot=2)).width > 100
