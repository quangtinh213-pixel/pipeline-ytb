import json
from pathlib import Path

from tttc import broll

FIX = json.loads((Path(__file__).parent / "fixtures" / "pexels_search.json").read_text(encoding="utf-8"))


class Resp:
    def __init__(self, data=None, content=b""):
        self._d, self.content, self.status_code = data, content, 200

    def json(self):
        return self._d

    def raise_for_status(self):
        pass


def test_search_sends_key_and_landscape():
    seen = {}

    def get(url, params=None, headers=None, timeout=None):
        seen.update(params=params, headers=headers)
        return Resp(FIX)

    res = broll.search("cảng container", key="K", get=get)
    assert seen["headers"]["Authorization"] == "K" and seen["params"]["orientation"] == "landscape"
    assert [r["id"] for r in res] == [101, 202, 303]


def test_pick_long_enough_landscape_hd():
    res = broll.search("x", key="K", get=lambda *a, **k: Resp(FIX))
    item = broll.pick(res, min_seconds=8)
    assert item["id"] == 303 and item["link"].endswith("303-hd.mp4")   # bỏ clip 4 s và clip dọc; chọn HD 1920, không UHD
    assert broll.pick(res, min_seconds=30) is None


def test_download_writes_file_and_credit(tmp_path):
    res = broll.search("x", key="K", get=lambda *a, **k: Resp(FIX))
    p = broll.download(broll.pick(res, 8), tmp_path, get=lambda *a, **k: Resp(content=b"mp4"))
    assert p == tmp_path / "broll" / "pexels-303.mp4" and p.read_bytes() == b"mp4"
    cred = json.loads((tmp_path / "broll" / "ghi-cong.json").read_text(encoding="utf-8"))
    assert cred[0]["ghi_cong"] == "Video: Chi trên Pexels" and cred[0]["tep"] == "pexels-303.mp4"
