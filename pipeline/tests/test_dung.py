import json
import re
import subprocess

import pytest
from PIL import Image

from tttc import dung

NGUON = [{"id": "p1", "gia_tri": "522.500 đ", "trich_dan": "", "url": "https://chatgpt.com/vi-VN/pricing",
          "ngay_truy_cap": "2026-11-07", "anh_chup": "nguon/p1.png", "trang_thai": "xac-minh"}]
SCENES = {"scenes": [
    {"id": "c1", "mau": "chuong", "start": 0, "end": 4, "so": "Phần 1", "chuong": "Mở đầu"},
    {"id": "c2", "mau": "minh-hoa", "start": 4, "end": 9, "svg": "chip", "nhan": "Chip"},
    {"id": "c3", "mau": "so-lon", "start": 9, "end": 14, "so": 522500, "sau": " đ", "nhan": "Plus",
     "nguon_id": "p1"},
    {"id": "c4", "mau": "bieu-do", "start": 14, "end": 20, "nhan": "Giá",
     "bieu_do": {"kieu": "cot", "nhan_x": ["Go", "Plus"], "gia_tri": [132000, 522500], "don_vi": "đ",
                 "noi_bat": 1, "nguon_id": "p1"}},
]}
TIMING = {"duration": 20.0, "words": [{"w": "Xin", "start": 0.1, "end": 0.4}, {"w": "chào.", "start": 0.5, "end": 0.9}],
          "paragraphs": []}


@pytest.fixture
def video(tmp_path):
    d = tmp_path / "v"
    d.mkdir()
    (d / "canh.json").write_text(json.dumps(SCENES, ensure_ascii=False), encoding="utf-8")
    (d / "giong-timing.json").write_text(json.dumps(TIMING), encoding="utf-8")
    (d / "nguon.json").write_text(json.dumps(NGUON, ensure_ascii=False), encoding="utf-8")
    (d / "giong.mp3").write_bytes(b"mp3")
    return d


def _hosts(index_html):
    return re.findall(r'<div id="([\w-]+)" data-composition-id="\1" data-composition-src="compositions/\1\.html"'
                      r'\s+data-start="([\d.]+)" data-duration="([\d.]+)"', index_html)


def test_compose_includes_every_scene_once(video):
    out = dung.compose(video)
    html = (out / "index.html").read_text(encoding="utf-8")
    assert [h[0] for h in _hosts(html)] == ["c1", "c2", "c3", "c4"]
    for sid in ["c1", "c2", "c3", "c4"]:
        scene = (out / "compositions" / f"{sid}.html").read_text(encoding="utf-8")
        assert f'data-composition-id="{sid}"' in scene and f'__timelines["{sid}"]' in scene
    assert (out / "assets" / "svg" / "chip.svg").exists() and (out / "assets" / "giong.mp3").exists()
    assert (out / "assets" / "svg" / "tai-lieu.svg").exists()  # ảnh mặc định của mẫu cũng phải có
    assert 'data-duration="20.0"' in html and 'id="giong"' in html


def test_compose_scene_ids_are_unique_per_mount(video):
    sc = dict(SCENES, scenes=[dict(SCENES["scenes"][1], id="a", start=0, end=10),
                              dict(SCENES["scenes"][1], id="b", start=10, end=20)])
    (video / "canh.json").write_text(json.dumps(sc), encoding="utf-8")
    out = dung.compose(video)
    a = (out / "compositions" / "a.html").read_text(encoding="utf-8")
    b = (out / "compositions" / "b.html").read_text(encoding="utf-8")
    ids_a, ids_b = set(re.findall(r'id="([^"]+)"', a)), set(re.findall(r'id="([^"]+)"', b))
    assert ids_a and (ids_a & ids_b) == {"root"}  # #root là bắt buộc của HyperFrames, mỗi cảnh một gốc


def test_compose_maps_variables(video):
    html = (dung.compose(video) / "index.html").read_text(encoding="utf-8")
    vals = {sid: json.loads(v.replace("&#39;", "'")) for sid, v in
            re.findall(r'<div id="([\w-]+)"[^>]*?data-variable-values=\'([^\']*)\'', html)}
    assert vals["c2"]["svg"] == "assets/svg/chip.svg" and vals["c2"]["nhan"] == "Chip"
    assert vals["c3"]["so"] == 522500 and vals["c3"]["nguon"] == "Nguồn: chatgpt.com, 07/11/2026"
    assert json.loads(vals["c4"]["gia_tri"]) == [132000, 522500] and vals["c4"]["noi_bat"] == 1
    assert vals["c3"]["so_hien"] == "522.500"  # chữ hiện ở khung cuối, đúng như nguồn
    assert json.loads(vals["c4"]["so_hien"]) == ["132.000", "522.500"]
    assert vals["c1"]["ten"] == "Mở đầu"


def test_compose_adds_captions_from_timing(video):
    html = (dung.compose(video) / "index.html").read_text(encoding="utf-8")
    assert 'data-track-kind="captions"' in html and "Xin chào." in html


def test_compose_scene_range_rebases_time(video):
    out = dung.compose(video, w=1080, h=1920, scene_range=(1, 3), out="short-1")
    html = (out / "index.html").read_text(encoding="utf-8")
    hosts = _hosts(html)
    assert [h[0] for h in hosts] == ["c2", "c3"]
    assert float(hosts[0][1]) == 0 and float(hosts[1][1]) == 5
    assert 'data-width="1080" data-height="1920"' in html
    assert 'data-media-start="4' in html  # giọng cắt đúng đoạn


def _tone(path, seconds, video=False):
    src = ["-f", "lavfi", "-i", f"color=c=black:s=320x180:d={seconds}"] if video else []
    args = ["ffmpeg", "-v", "error", "-y", *src, "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=mono",
            "-t", str(seconds)]
    args += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac"] if video else ["-c:a", "libmp3lame"]
    subprocess.run(args + [str(path)], check=True)
    return path


def test_check_av_detects_drift(tmp_path):
    v = _tone(tmp_path / "v.mp4", 10, video=True)
    assert dung.check_av(v, _tone(tmp_path / "a.mp3", 10)) == []
    errs = dung.check_av(v, _tone(tmp_path / "b.mp3", 11))
    assert len(errs) == 1 and "lệch" in errs[0]


def test_contact_sheet_size(tmp_path):
    v = _tone(tmp_path / "v.mp4", 6, video=True)
    sc = {"scenes": [{"id": "a", "start": 0, "end": 2}, {"id": "b", "start": 2, "end": 4},
                     {"id": "c", "start": 4, "end": 6}]}
    out = dung.contact_sheet(v, sc, tmp_path / "sheet.png")
    assert Image.open(out).size == (3 * 384, 216)


def test_vi_number_keeps_decimals():
    assert dung.vi_number(5.3) == "5,3" and dung.vi_number(2.5) == "2,5"
    assert dung.vi_number(522500) == "522.500" and dung.vi_number("5,3") == "5,3"
    assert dung.vi_number(1234567.25) == "1.234.567,25"


def test_contact_sheet_creates_folder(tmp_path):
    v = _tone(tmp_path / "v.mp4", 2, video=True)
    out = dung.contact_sheet(v, {"scenes": [{"id": "a", "start": 0, "end": 2}]}, tmp_path / "frames" / "s.png")
    assert out.exists()


def _host_vals(html):
    return {sid: json.loads(v.replace("&#39;", "'")) for sid, v in
            re.findall(r'<div id="([\w-]+)"[^>]*?data-variable-values=\'([^\']*)\'', html)}


def test_compose_assigns_grounds(video):
    vals = _host_vals((dung.compose(video) / "index.html").read_text(encoding="utf-8"))
    assert vals["c1"]["nen"] == "vang"           # chương: nền vàng
    assert vals["c2"]["nen"] == "kem"            # chương 1 (lẻ): nền kem
    sc = json.loads((video / "canh.json").read_text(encoding="utf-8"))
    sc["scenes"][1]["nen"] = "toi"               # canh.json ghi đè được
    (video / "canh.json").write_text(json.dumps(sc, ensure_ascii=False), encoding="utf-8")
    assert _host_vals((dung.compose(video) / "index.html").read_text(encoding="utf-8"))["c2"]["nen"] == "toi"


def test_compose_adds_transitions(video):
    html = (dung.compose(video) / "index.html").read_text(encoding="utf-8")
    assert re.search(r'id="tr-1"[^>]*data-start="3.7"', html) and 'class="tr-p tr-muc"' in html  # rời chương
    assert 'id="tr-2"' not in html                                                         # cắt thẳng
    assert re.search(r'id="tr-3"[^>]*data-start="13.7"', html) and "tr-dip" in html
    assert 'tl.fromTo("#tr-1-p"' in html


def test_compose_maps_new_variables(video):
    sc = json.loads((video / "canh.json").read_text(encoding="utf-8"))
    sc["scenes"][1].update(phu=["cay", "dong-xu"])
    sc["scenes"][2].update(huong="len", svg="tien")
    sc["scenes"][3]["bieu_do"]["chu_thich"] = "ĐẮT NHẤT"
    sc["scenes"].append({"id": "c5", "mau": "trang-nguon", "start": 20, "end": 24, "anh": "p1.png",
                         "khung": "1,2,3,4", "nguon_id": "p1"})
    (video / "canh.json").write_text(json.dumps(sc, ensure_ascii=False), encoding="utf-8")
    vals = _host_vals((dung.compose(video) / "index.html").read_text(encoding="utf-8"))
    assert vals["c2"]["phu1"] == "assets/svg/cay.svg" and vals["c2"]["phu2"] == "assets/svg/dong-xu.svg"
    assert vals["c3"]["huong"] == "len" and vals["c3"]["svg"] == "assets/svg/tien.svg"
    assert vals["c4"]["chu_thich"] == "ĐẮT NHẤT"
    assert vals["c5"]["url"] == "chatgpt.com/vi-VN/pricing"
