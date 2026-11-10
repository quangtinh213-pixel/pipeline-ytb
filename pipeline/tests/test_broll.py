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


def test_download_interrupted_leaves_no_partial_file(tmp_path, monkeypatch):
    import pytest
    item = {"id": 303, "link": "https://videos.example/303.mp4", "tac_gia": "Chi", "trang": "https://pexels.com/303"}
    orig = Path.write_bytes

    def mat_giua_chung(self, data):  # ghi được một phần rồi mất kết nối
        orig(self, data[:2])
        raise OSError("mất kết nối giữa chừng")

    monkeypatch.setattr(Path, "write_bytes", mat_giua_chung)
    with pytest.raises(OSError):
        broll.download(item, tmp_path, get=lambda *a, **k: Resp(content=b"mp4data"))
    assert not (tmp_path / "broll" / "pexels-303.mp4").exists()  # không có tệp cắt cụt bị coi là đã tải

    monkeypatch.setattr(Path, "write_bytes", orig)
    p = broll.download(item, tmp_path, get=lambda *a, **k: Resp(content=b"mp4data"))
    assert p.read_bytes() == b"mp4data"


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


# ---- Tải thêm B-roll theo từng video ----

def _bytes_of_clip(tmp_path, secs=3):
    return _clip(tmp_path / "src.mp4", w=1280, h=720, secs=secs).read_bytes()


def test_tai_ve_rejects_untrusted_host(tmp_path):
    with pytest.raises(ValueError):
        broll.tai_ve("https://evil.example.com/x.mp4", "cang", tmp_path, "Video: A trên Pexels",
                     nguon="https://www.pexels.com/video/1/", mo_ta="x", tu_khoa=["x"])


def test_tai_ve_downloads_normalizes_and_indexes(tmp_path):
    data = _bytes_of_clip(tmp_path)
    calls = []

    def get(url, headers=None, timeout=None, stream=None):
        calls.append(url)
        return Resp(content=data)

    kho = tmp_path / "kho"
    kho.mkdir()
    p = broll.tai_ve("https://videos.pexels.com/video-files/9/9-hd_1920_1080_30fps.mp4", "dien-gio-9", kho,
                     "Video: Dũng trên Pexels", nguon="https://www.pexels.com/video/9/",
                     mo_ta="Cánh quạt điện gió quay", tu_khoa=["điện gió", "năng lượng"], get=get)
    assert p == kho / "dien-gio-9.mp4"
    info = _probe(p)
    v = [s for s in info["streams"] if s["codec_type"] == "video"][0]
    assert (v["width"], v["height"]) == (1920, 1080)
    entry = json.loads((kho / "kho.json").read_text(encoding="utf-8"))[0]
    assert entry["tep"] == "dien-gio-9.mp4" and entry["ghi_cong"] == "Video: Dũng trên Pexels"
    assert entry["tu_khoa"] == ["điện gió", "năng lượng"] and entry["do_dai"] == pytest.approx(3, abs=0.2)
    # tải lại cùng tên: không gọi mạng, không thêm mục trùng
    broll.tai_ve("https://videos.pexels.com/video-files/9/9-hd_1920_1080_30fps.mp4", "dien-gio-9", kho,
                 "Video: Dũng trên Pexels", nguon="https://www.pexels.com/video/9/", mo_ta="x", tu_khoa=[], get=get)
    assert len(calls) == 1 and len(json.loads((kho / "kho.json").read_text(encoding="utf-8"))) == 1


def test_tai_ve_rejects_non_video_payload(tmp_path):
    kho = tmp_path / "kho"
    kho.mkdir()
    with pytest.raises(RuntimeError):
        broll.tai_ve("https://videos.pexels.com/x.mp4", "rac", kho, "Video: A trên Pexels",
                     nguon="https://www.pexels.com/video/1/", mo_ta="x", tu_khoa=[],
                     get=lambda *a, **k: Resp(content=b"<html>blocked</html>"))
    assert not (kho / "rac.mp4").exists()


def test_soi_makes_three_frame_strip(tmp_path):
    from PIL import Image
    out = broll.soi(_clip(tmp_path / "a.mp4", secs=2, audio=False), tmp_path / "soi.jpg")
    assert Image.open(out).size == (3 * 320, 180)


def test_nhap_anh_tinh_thanh_clip(tmp_path):
    from PIL import Image
    src = tmp_path / "tiem-dien-thoai.jpg"
    Image.new("RGB", (800, 600), "red").save(src)
    out = broll.nhap(src, tmp_path / "v", ghi_cong="Ảnh: A trên Wikimedia Commons", do_dai=2)
    assert out.suffix == ".mp4" and abs(broll._duration(out) - 2) < 0.2
    with pytest.raises(ValueError):
        broll.nhap(src, tmp_path / "v2", ghi_cong="Ảnh: A")
