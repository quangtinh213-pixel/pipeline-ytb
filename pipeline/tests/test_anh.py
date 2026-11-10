import json
from pathlib import Path

from tttc import anh

FIX = json.loads((Path(__file__).parent / "fixtures" / "commons_search.json").read_text())


class Resp:
    def __init__(self, data=None, content=b""):
        self._d, self.content, self.status_code = data, content, 200

    def json(self):
        return self._d

    def raise_for_status(self):
        pass


def _item(lic, artist="Ai đó", file="File:A.jpg"):
    return {"file": file, "url": "https://upload.wikimedia.org/a.jpg", "giay_phep": lic,
            "tac_gia": artist, "link": "https://commons.wikimedia.org/wiki/File:A.jpg"}


def test_search_parses_fixture_in_rank_order():
    calls = []

    def get(url, params=None, headers=None, timeout=None):
        calls.append(headers)
        return Resp(FIX)

    res = anh.search("Jensen Huang", get=get)
    assert [r["file"] for r in res][:2] == ["File:Jensen Huang (cropped).jpg",
                                            "File:Jensen huang stanford 2026-04-30 008.jpg"]
    assert res[1]["giay_phep"] == "CC BY-SA 4.0" and res[1]["url"].startswith("https://")
    assert "NhipCongNghe" in calls[0]["User-Agent"] and "@" not in calls[0]["User-Agent"]


def test_pick_rejects_nonfree_license():
    res = anh.search("x", get=lambda *a, **k: Resp(FIX))
    assert anh.pick(res)["file"] == "File:Jensen huang stanford 2026-04-30 008.jpg"  # bỏ GODL-India
    assert anh.pick([_item("Fair use"), _item(""), _item("CC BY-NC 4.0"), _item("All rights reserved")]) is None


def test_pick_accepts_cc_by_sa_and_pd():
    for lic in ["CC BY-SA 4.0", "CC BY 2.0", "CC0", "Public domain", "PD-USGov"]:
        assert anh.pick([_item(lic)]) is not None, lic


def test_pick_requires_artist_for_cc_not_pd():
    assert anh.pick([_item("CC BY 4.0", artist="")]) is None
    assert anh.pick([_item("Public domain", artist="")])["tac_gia"] == "Không rõ tác giả"


def test_pick_strips_html_from_artist():
    res = anh.search("x", get=lambda *a, **k: Resp(FIX))
    a = anh.pick(res)["tac_gia"]
    assert "<" not in a and "Anders" in a


def test_download_appends_credit(tmp_path):
    get = lambda *a, **k: Resp(content=b"\xff\xd8jpg")
    p1 = anh.download(_item("CC BY 4.0", "Ann", "File:Ảnh một.jpg"), tmp_path, get=get)
    anh.download(_item("Public domain", "Bob", "File:B.png"), tmp_path, get=get)
    assert p1.parent == tmp_path / "anh" and p1.read_bytes() == b"\xff\xd8jpg"
    credits = json.loads((tmp_path / "anh" / "ghi-cong.json").read_text(encoding="utf-8"))
    assert [c["tac_gia"] for c in credits] == ["Ann", "Bob"]
    assert credits[0]["ghi_cong"] == "Ann, Wikimedia Commons, CC BY 4.0"
    assert credits[0]["tep"] == p1.name
