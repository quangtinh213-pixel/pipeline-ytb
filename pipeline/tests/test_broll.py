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


# ---- B-roll thủ công: kho dùng chung + nhập vào video ----
import subprocess

import pytest


def _clip(path, w=640, h=480, secs=3, audio=True):
    args = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"testsrc=size={w}x{h}:rate=25:duration={secs}"]
    if audio:
        args += ["-f", "lavfi", "-i", f"sine=duration={secs}"]
    subprocess.run(args + ["-c:v", "libx264", "-pix_fmt", "yuv420p", str(path)], check=True)
    return path


def _probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height:format=duration",
                          "-of", "json", str(path)], capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def test_nhap_converts_to_1080p_silent_and_trims(tmp_path):
    src = _clip(tmp_path / "Cang Bien 4K.mp4", secs=3)
    out = broll.nhap(src, tmp_path / "v", ghi_cong="Video: An trên Pexels", bat_dau=0.5, do_dai=2)
    info = _probe(out)
    v = [s for s in info["streams"] if s["codec_type"] == "video"][0]
    assert (v["width"], v["height"]) == (1920, 1080)
    assert not [s for s in info["streams"] if s["codec_type"] == "audio"]
    assert float(info["format"]["duration"]) == pytest.approx(2, abs=0.1)
    assert out.parent == tmp_path / "v" / "broll" and out.name == "cang-bien-4k.mp4"


def test_nhap_records_credit_once(tmp_path):
    src = _clip(tmp_path / "a.mp4", secs=1, audio=False)
    broll.nhap(src, tmp_path / "v", ghi_cong="Video: Bình trên Pixabay")
    broll.nhap(src, tmp_path / "v", ghi_cong="Video: Bình trên Pixabay")
    cred = json.loads((tmp_path / "v" / "broll" / "ghi-cong.json").read_text(encoding="utf-8"))
    assert cred == [{"tep": "a.mp4", "ghi_cong": "Video: Bình trên Pixabay", "nguon_tep": "a.mp4"}]


def test_nhap_requires_credit(tmp_path):
    src = _clip(tmp_path / "a.mp4", secs=1, audio=False)
    with pytest.raises(ValueError):
        broll.nhap(src, tmp_path / "v", ghi_cong="")


def test_quet_kho_adds_new_files_only(tmp_path):
    kho = tmp_path / "kho"
    kho.mkdir()
    _clip(kho / "cang-container-hai-phong.mp4", secs=1, audio=False)
    _clip(kho / "nha may chip.mov", secs=2, audio=False)
    (kho / "ghi-chu.txt").write_text("x")
    moi = broll.quet_kho(kho)
    assert sorted(m["tep"] for m in moi) == ["cang-container-hai-phong.mp4", "nha may chip.mov"]
    data = json.loads((kho / "kho.json").read_text(encoding="utf-8"))
    e = next(x for x in data if x["tep"] == "nha may chip.mov")
    assert e["tu_khoa"] == ["nha", "may", "chip"] and e["do_dai"] == pytest.approx(2, abs=0.1)
    assert e["ghi_cong"] == "" and e["mo_ta"] == ""
    data[0]["ghi_cong"] = "Video: Chi trên Pexels"
    (kho / "kho.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    assert broll.quet_kho(kho) == []                      # chạy lại không thêm trùng, giữ phần đã sửa
    assert json.loads((kho / "kho.json").read_text(encoding="utf-8"))[0]["ghi_cong"] == "Video: Chi trên Pexels"
