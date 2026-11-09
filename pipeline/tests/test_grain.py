from PIL import Image

from tttc import grain


def test_grain_is_deterministic_and_seed_dependent(tmp_path):
    a = grain.tao_grain(tmp_path / "a.png", 64, 7).read_bytes()
    assert a == grain.tao_grain(tmp_path / "b.png", 64, 7).read_bytes()
    assert a != grain.tao_grain(tmp_path / "c.png", 64, 8).read_bytes()
    assert Image.open(tmp_path / "a.png").size == (64, 64)


def test_grain_is_roughly_mid_grey_so_overlay_keeps_brightness(tmp_path):
    im = Image.open(grain.tao_grain(tmp_path / "g.png", 128, 7)).convert("L")
    mean = sum(im.getdata()) / (128 * 128)
    assert 120 < mean < 136
