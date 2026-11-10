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


def test_green_cast_on_edges_is_removed(tmp_path):
    im = Image.new("RGB", (200, 200), (10, 200, 10))
    ImageDraw.Draw(im).rectangle([60, 60, 140, 140], fill=(200, 210, 215), outline=(60, 180, 90), width=3)  # viền nhuộm xanh lá
    im.save(tmp_path / "g.png")
    out = Image.open(tach_nen.tach_nen(tmp_path / "g.png", tmp_path / "o.png", cao=200)).convert("RGBA")
    assert all(g <= max(r, b) + 1 for r, g, b, a in out.getdata() if a > 0)  # không điểm nào xanh lá trội


def test_stray_specks_far_from_the_subject_do_not_shrink_it(tmp_path):
    im = Image.new("RGB", (200, 300), (10, 200, 10))
    d = ImageDraw.Draw(im)
    d.ellipse([90, 80, 110, 220], fill=(255, 200, 0), outline=(17, 17, 17), width=3)  # vật mảnh
    d.rectangle([194, 4, 197, 7], fill=(255, 255, 255))                                # đốm rác ở góc xa
    im.save(tmp_path / "s.png")
    out = Image.open(tach_nen.tach_nen(tmp_path / "s.png", tmp_path / "o.png", cao=560))
    assert out.width / out.height < 0.3  # cắt theo vật chính, không bị đốm kéo rộng


def _face(tmp_path, with_alpha_margin=True):
    im = Image.new("RGBA", (300, 300), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([40, 60, 260, 260], 30, fill=(220, 225, 230, 255))            # thân trắng
    d.rounded_rectangle([60, 80, 240, 240], 20, fill=(10, 35, 40, 255))               # màn hình tối
    d.ellipse([90, 110, 110, 130], fill=(34, 211, 238, 255)); d.ellipse([190, 110, 210, 130], fill=(34, 211, 238, 255))  # hai mắt
    d.rectangle([130, 200, 170, 206], fill=(34, 211, 238, 255))                       # miệng
    d.rectangle([148, 20, 152, 60], fill=(34, 211, 238, 255))                         # ăng-ten (nằm ngoài màn hình)
    p = tmp_path / "f.png"; im.save(p); return p


def test_blink_clears_eyes_keeps_mouth_antenna_and_silhouette(tmp_path):
    src = _face(tmp_path)
    out = tach_nen.tao_nham(src, tmp_path / "n.png")
    a, b = Image.open(src).convert("RGBA"), Image.open(out).convert("RGBA")
    assert a.size == b.size and a.getchannel("A").tobytes() == b.getchannel("A").tobytes()  # cùng hình dáng
    cyan = lambda px: px[2] > 150 and px[1] > 150 and px[0] < 120
    assert cyan(a.getpixel((100, 120))) and not cyan(b.getpixel((100, 120))) and not cyan(b.getpixel((200, 120)))  # mắt tắt
    assert cyan(b.getpixel((150, 203))) and cyan(b.getpixel((150, 30)))                                            # miệng, ăng-ten còn
