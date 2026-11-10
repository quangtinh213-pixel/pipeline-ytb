import pytest

from tttc import chup


def test_khung_doi_px_sang_phan_tram_co_le():
    assert chup.khung({"x": 152, "y": 82, "width": 304, "height": 82}, le=0) == "10.0,10.0,20.0,10.0"


def test_khung_cat_trong_anh():
    x, y, w, h = map(float, chup.khung({"x": 0, "y": 800, "width": 1520, "height": 100}).split(","))
    assert x == 0 and x + w <= 100 and y + h <= 100.01


def test_khung_ngoai_anh_bao_loi():
    with pytest.raises(ValueError):
        chup.khung({"x": 0, "y": 900, "width": 100, "height": 20})
