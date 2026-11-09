from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from tttc import radar

VN = timezone(timedelta(hours=7))
FIX = Path(__file__).resolve().parent / "fixtures"


class Resp:
    def __init__(self, text, code=200):
        self.text, self.status_code = text, code

    def raise_for_status(self):
        if self.status_code != 200:
            raise RuntimeError(self.status_code)


@pytest.fixture
def fixture_rss():
    return (FIX / "rss-doi-thu.xml").read_text(encoding="utf-8")


def test_doc_rss_parses_entries_in_vietnam_time_and_skips_broken(fixture_rss):
    items = radar.doc_rss("UCx", get=lambda url, **kw: Resp(fixture_rss))
    assert [i["id"] for i in items] == ["aaa111", "bbb222"] and items[0]["view"] == 11180
    assert items[0]["tieu_de"] == 'Video thử một "trích"' and items[0]["dang_luc"].utcoffset() == timedelta(hours=7)
    assert items[0]["dang_luc"].hour == 17


def test_doc_rss_raises_on_http_error_or_bad_xml():
    with pytest.raises(RuntimeError, match="RSS đối thủ"):
        radar.doc_rss("UCx", get=lambda url, **kw: Resp("", 500))
    with pytest.raises(RuntimeError, match="RSS đối thủ"):
        radar.doc_rss("UCx", get=lambda url, **kw: Resp("<not-xml"))


def test_cham_diem_weights_vietnam_angle_double_and_validates():
    assert radar.cham_diem(2, 2, 2) == 8 and radar.cham_diem(2, 2, 0) == 4 and radar.cham_diem(0, 0, 2) == 4
    with pytest.raises(ValueError):
        radar.cham_diem(3, 0, 0)


def _de(t, soc, sl, vn, moi=10):
    return {"tieu_de": t, "soc": soc, "so_lon": sl, "goc_vn": vn, "link": "u", "moi_luc": datetime(2026, 11, 9, moi, tzinfo=VN)}


def test_xep_hang_drops_below_threshold_and_orders_ties_by_vietnam_angle_then_recency():
    top = radar.xep_hang([_de("thấp", 1, 1, 0), _de("A không VN", 2, 2, 0, moi=12),
                          _de("B có VN", 1, 1, 1, moi=8), _de("C có VN mới", 1, 1, 1, moi=9)])
    assert [d["tieu_de"] for d in top] == ["C có VN mới", "B có VN", "A không VN"] and top[0]["diem"] == 4


def test_ghi_chu_de_writes_three_ranked_ideas(tmp_path):
    top = radar.xep_hang([_de(f"Đề {i}", 2, 2, 1, moi=i + 1) for i in range(5)])
    p = radar.ghi_chu_de(tmp_path, top, {"Đề 4": True})
    txt = p.read_text(encoding="utf-8")
    assert p == tmp_path / "chu-de.md" and txt.count("## Đề ") == 3
    assert "Họ đã đăng cùng sự kiện: có" in txt and "góc Việt Nam 1×2" in txt and "Họ đã đăng cùng sự kiện: chưa rõ" in txt
