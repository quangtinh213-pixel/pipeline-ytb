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


# ---- A: nhịp con theo từ khoá ----

WORDS = [{"w": w, "start": 9 + i * 0.5, "end": 9 + i * 0.5 + 0.4}
         for i, w in enumerate("Gói ChatGPT Plus giá năm trăm nghìn, đắt nhất.".split())]


def test_find_phrase_time():
    assert dung.phrase_time(WORDS, "Plus", 9, 14) == pytest.approx(10.0)
    assert dung.phrase_time(WORDS, "năm trăm", 9, 14) == pytest.approx(11.0)
    assert dung.phrase_time(WORDS, "đắt nhất", 9, 14) == pytest.approx(12.5)  # bỏ dấu câu khi so
    assert dung.phrase_time(WORDS, "Gemini", 9, 14) is None
    assert dung.phrase_time(WORDS, "Gói", 9.5, 14) is None                      # ngoài cửa sổ cảnh


def test_compose_steps_default_and_keyword(video):
    timing = json.loads((video / "giong-timing.json").read_text())
    timing["words"] = WORDS
    (video / "giong-timing.json").write_text(json.dumps(timing, ensure_ascii=False), encoding="utf-8")
    sc = json.loads((video / "canh.json").read_text(encoding="utf-8"))
    sc["scenes"][2]["nhip"] = [None, "đắt nhất"]          # c3 so-lon: bước 2 (dòng dưới) theo từ khoá
    (video / "canh.json").write_text(json.dumps(sc, ensure_ascii=False), encoding="utf-8")
    vals = _host_vals((dung.compose(video) / "index.html").read_text(encoding="utf-8"))
    assert json.loads(vals["c3"]["nhip"]) == pytest.approx([0.05, 3.5])   # 12,5 − 9,0
    assert json.loads(vals["c2"]["nhip"]) == pytest.approx(dung.DEFAULT_STEPS["minh-hoa"])
    assert len(json.loads(vals["c4"]["nhip"])) == 3                       # 2 cột + bước nổi bật


# ---- D: âm thanh hiệu ứng ----

def test_compose_places_sfx(video):
    html = (dung.compose(video) / "index.html").read_text(encoding="utf-8")
    sfx = re.findall(r'<audio id="sfx-\d+" src="assets/sfx/([\w-]+)\.mp3" data-start="([\d.]+)"', html)
    names = [n for n, _ in sfx]
    assert ("whoosh-short", "3.7") in sfx                    # quét khi rời chương (đường nối 4,0 − 0,3)
    assert ("ping", str(round(9 + 0.05 + 1.3, 3))) in sfx    # số lớn đếm xong
    assert "impact-bass-1" in names and "pop" in names
    assert (dung.compose(video) / "assets" / "sfx" / "ping.mp3").exists()
    assert all(float(v) <= 0.4 for v in re.findall(r'id="sfx-\d+"[^>]*data-volume="([\d.]+)"', html))


# ---- B, C: mẫu trích báo và b-roll ----

def test_compose_trich_bao_and_broll(video):
    nguon = json.loads((video / "nguon.json").read_text(encoding="utf-8"))
    nguon.append({"id": "b1", "gia_tri": "", "trich_dan": "Giá RAM tăng gấp ba lần.", "ten": "VnExpress",
                  "url": "https://vnexpress.net/x", "ngay_truy_cap": "2026-11-07", "trang_thai": "xac-minh"})
    (video / "nguon.json").write_text(json.dumps(nguon, ensure_ascii=False), encoding="utf-8")
    (video / "broll").mkdir()
    (video / "broll" / "pexels-303.mp4").write_bytes(b"x")
    (video / "broll" / "ghi-cong.json").write_text(json.dumps([{"tep": "pexels-303.mp4", "ghi_cong": "Video: Chi trên Pexels"}],
                                                              ensure_ascii=False), encoding="utf-8")
    sc = json.loads((video / "canh.json").read_text(encoding="utf-8"))
    sc["scenes"] += [
        {"id": "c5", "mau": "trich-bao", "start": 20, "end": 25, "nguon_id": "b1", "trich": "Giá RAM tăng gấp ba lần",
         "to_vang": "gấp ba lần"},
        {"id": "c6", "mau": "b-roll", "start": 25, "end": 30, "video": "pexels-303.mp4", "nhan": "QUY MÔ", "so": "01"}]
    (video / "canh.json").write_text(json.dumps(sc, ensure_ascii=False), encoding="utf-8")
    out = dung.compose(video)
    vals = _host_vals((out / "index.html").read_text(encoding="utf-8"))
    assert vals["c5"]["bao"] == "VnExpress" and vals["c5"]["ngay"] == "07/11/2026"
    assert vals["c5"]["tieu_de"] == "Giá RAM tăng gấp ba lần" and vals["c5"]["to_vang"] == "gấp ba lần"
    assert vals["c6"]["ghi_cong"] == "Video: Chi trên Pexels" and vals["c6"]["nhan"] == "QUY MÔ"
    scene = (out / "compositions" / "c6.html").read_text(encoding="utf-8")
    assert 'src="assets/broll/pexels-303.mp4"' in scene and "muted" in scene
    assert (out / "assets" / "broll" / "pexels-303.mp4").exists()


def test_source_line_tu_tinh_shows_formula():
    n = {"id": "t1", "gia_tri": "15 năm", "trang_thai": "tu-tinh", "cong_thuc": "2026 − 2011", "dau_vao": []}
    assert dung._source_line(n) == "Tự tính: 2026 − 2011"


def test_scene_file_injects_dong_helper():
    for mau in ("minh-hoa", "so-lon"):
        s = dung._scene_file(mau, "c1")
        assert "function dongLap" in s and "__DONG__" not in s
    assert 'dongLap(tl, "#mh-chinh"' in dung._scene_file("minh-hoa", "c1").replace("c1-mh-", "mh-")


def test_vars_dong_defaults():
    mh = dung._vars({"mau": "minh-hoa", "svg": "chip"}, {}, {})
    assert mh["dong"] == "bob"
    assert dung._vars({"mau": "minh-hoa", "svg": "chip", "dong": "xoay"}, {}, {})["dong"] == "xoay"
    assert dung._vars({"mau": "so-lon", "so": 5}, {}, {})["dong"] == ""


QT = {"id": "q1", "mau": "quy-trinh", "start": 0, "end": 6, "tieu_de": "Chip đi từ bản vẽ tới tay người dùng",
      "buoc": [{"nhan": "Thiết kế", "svg": "chip"}, {"nhan": "Đúc"}, {"nhan": "Đóng gói"}], "noi_bat": 1}


def test_vars_quy_trinh():
    v = dung._vars(QT, {}, {})
    assert json.loads(v["buoc"]) == [{"nhan": "Thiết kế", "svg": "assets/svg/chip.svg"},
                                     {"nhan": "Đúc", "svg": ""}, {"nhan": "Đóng gói", "svg": ""}]
    assert v["tieu_de"] == QT["tieu_de"] and v["noi_bat"] == 1 and v["dong"] == "dap"


def test_steps_quy_trinh_one_per_step():
    assert dung.steps(QT, []) == pytest.approx([0.5, 1.05, 1.6])
    assert dung.steps(dict(QT, nhip=[None, "đúc"]), [{"w": "đúc", "start": 2.0, "end": 2.3}])[1] == pytest.approx(2.0)


def test_sfx_quy_trinh_one_pop_per_step():
    ev = dung.sfx_events(QT, dung.steps(QT, []))
    assert [(f, v) for f, _, v in ev] == [("pop", 0.2)] * 3
    assert [t for _, t, _ in ev] == pytest.approx([0.5, 1.05, 1.6])


def test_compose_quy_trinh_scene_file_and_prefix(video):
    s = dung._scene_file("quy-trinh", "q1")
    assert 'data-composition-id="q1"' in s and "q1-qt-" in s and "function dongLap" in s


SS = {"id": "s1", "mau": "so-sanh", "start": 0, "end": 6, "nguon_id": "p1", "ti_le": "gấp ~700 lần",
      "trai": {"nhan": "Nvidia Blackwell", "svg": "chip", "so": 208, "don_vi": "tỷ transistor"},
      "phai": {"nhan": "Chip VGC", "svg": "chip", "so": "300", "don_vi": "triệu transistor", "to": 0.15}}


def test_vars_so_sanh():
    v = dung._vars(SS, {"p1": NGUON[0]}, {})
    trai, phai = json.loads(v["trai"]), json.loads(v["phai"])
    assert trai == {"nhan": "Nvidia Blackwell", "svg": "assets/svg/chip.svg", "so": 208.0, "so_hien": "208",
                    "don_vi": "tỷ transistor", "to": 1.0}
    assert phai["to"] == 0.15 and phai["so"] == 300.0 and phai["so_hien"] == "300"
    assert v["ti_le"] == "gấp ~700 lần" and v["dong"] == "dap" and v["nguon"].startswith("Nguồn: chatgpt.com")


def test_steps_so_sanh_default_and_keyword():
    assert dung.steps(SS, []) == pytest.approx([0.5, 1.1, 1.8])
    t = dung.steps(dict(SS, nhip=[None, "VGC"]), [{"w": "VGC", "start": 2.5, "end": 2.8}])
    assert t[1] == pytest.approx(2.5)


def test_sfx_so_sanh():
    ev = dung.sfx_events(SS, dung.steps(SS, []))
    assert [f for f, _, _ in ev] == ["pop", "pop", "chime"]
    assert len(dung.sfx_events(dict(SS, ti_le=""), dung.steps(SS, []))) == 2


def test_so_sanh_scene_file_prefix():
    s = dung._scene_file("so-sanh", "s1")
    assert 'data-composition-id="s1"' in s and "s1-ss-" in s and "function dongLap" in s


TG = {"id": "g1", "mau": "thoi-gian", "start": 0, "end": 6, "nguon_id": "p1",
      "truc": {"tu": 2024, "den": 2030, "don_vi": "năm"},
      "hang": [{"nhan": "Singapore", "tu": 2024, "den": 2026}, {"nhan": "Hoà Lạc", "tu": 2026, "den": 2030, "noi_bat": True}]}


def test_vars_thoi_gian():
    v = dung._vars(TG, {"p1": NGUON[0]}, {})
    assert json.loads(v["truc"]) == {"tu": 2024, "den": 2030, "don_vi": "năm"}
    assert json.loads(v["hang"]) == [{"nhan": "Singapore", "tu": 2024, "den": 2026, "noi_bat": False},
                                     {"nhan": "Hoà Lạc", "tu": 2026, "den": 2030, "noi_bat": True}]
    assert v["nguon"].startswith("Nguồn: chatgpt.com")


def test_steps_and_sfx_thoi_gian():
    st = dung.steps(TG, [])
    assert st == pytest.approx([0.5, 1.1])
    assert [(f, v) for f, _, v in dung.sfx_events(TG, st)] == [("whoosh-short", 0.2)] * 2
    assert dung.steps(dict(TG, nhip=[None, "Hoà Lạc"]), [{"w": "Hoà", "start": 3.0, "end": 3.2},
                                                       {"w": "Lạc", "start": 3.2, "end": 3.4}])[1] == pytest.approx(3.0)


def test_thoi_gian_scene_file_prefix():
    s = dung._scene_file("thoi-gian", "g1")
    assert 'data-composition-id="g1"' in s and "g1-tg-" in s


def test_compose_mixes_music_into_voice_track(video, tmp_path, monkeypatch):
    _tone(video / "giong.mp3", 20)
    music = _tone(tmp_path / "nhac.mp3", 5)
    cfg = tmp_path / "config.json"
    cfg.write_text(json.dumps({"nhac_nen": str(music)}), encoding="utf-8")
    monkeypatch.setattr(dung, "CONFIG", cfg)
    out = dung.compose(video)
    html = (out / "index.html").read_text(encoding="utf-8")
    assert 'id="nhac"' not in html and 'id="giong"' in html
    assert (out / "assets" / "giong.mp3").read_bytes() != (video / "giong.mp3").read_bytes()  # bản đã trộn nhạc


def test_compose_without_music_copies_voice(video, tmp_path, monkeypatch):
    cfg = tmp_path / "config.json"
    cfg.write_text(json.dumps({"nhac_nen": ""}), encoding="utf-8")
    monkeypatch.setattr(dung, "CONFIG", cfg)
    out = dung.compose(video)
    assert (out / "assets" / "giong.mp3").read_bytes() == b"mp3" and 'id="nhac"' not in (out / "index.html").read_text(encoding="utf-8")


def test_compose_missing_music_file_gives_clear_error(video, tmp_path, monkeypatch):
    cfg = tmp_path / "config.json"
    cfg.write_text(json.dumps({"nhac_nen": "am-thanh/nhac/khong-co.mp3"}), encoding="utf-8")
    monkeypatch.setattr(dung, "CONFIG", cfg)
    with pytest.raises(FileNotFoundError, match="nhạc nền"):
        dung.compose(video)


def _video_with_dan(video, **dan_extra):
    sc = json.loads(json.dumps(SCENES))
    sc["scenes"][1]["dan"] = dict({"the": "ngac-nhien", "goc": "phai"}, **dan_extra)
    (video / "canh.json").write_text(json.dumps(sc, ensure_ascii=False), encoding="utf-8")
    return video


def test_compose_adds_mascot_clip_for_scene_with_dan(video):
    out = dung.compose(_video_with_dan(video))
    html = (out / "index.html").read_text(encoding="utf-8")
    m = re.search(r'<div id="dan-1" class="clip dan dan-phai" data-start="([\d.]+)" data-duration="([\d.]+)"', html)
    assert m and float(m.group(1)) == 4 and float(m.group(2)) == 5  # đúng đầu và độ dài cảnh c2
    assert 'src="assets/svg/tui-ngac-nhien.svg"' in html and 'src="assets/svg/tui-ngac-nhien-nham.svg"' in html
    assert (out / "assets" / "svg" / "tui-ngac-nhien-nham.svg").exists()
    assert 'id="dan-0"' not in html and html.count('class="clip dan') == 1


def test_compose_scene_range_keeps_mascot_inside_range(video):
    out = dung.compose(_video_with_dan(video, goc="trai"), scene_range=(1, 3), out="cat")
    html = (out / "index.html").read_text(encoding="utf-8")
    m = re.search(r'<div id="dan-0" class="clip dan dan-trai" data-start="([\d.]+)" data-duration="([\d.]+)"', html)
    assert m and float(m.group(1)) == 0 and float(m.group(1)) + float(m.group(2)) <= 10 + 1e-6  # cắt đoạn c2–c3 dài 10 s


def test_compose_vertical_has_no_mascot(video):
    out = dung.compose(_video_with_dan(video), w=1080, h=1920, scene_range=(1, 3), out="short")
    assert "dan-" not in (out / "index.html").read_text(encoding="utf-8").replace("dan-phai", "").replace("dan-trai", "")
    assert 'class="clip dan' not in (out / "index.html").read_text(encoding="utf-8")


def test_compose_takes_colours_from_theme(video, monkeypatch):
    from tttc import theme
    monkeypatch.setattr(theme, "TH", {**theme.TH, "nhan": ["#00AAFF", "#0088CC", "#006699"], "nen": "#0A0B0C"})
    out = dung.compose(video)
    pages = [out / "index.html", *sorted((out / "compositions").glob("*.html"))]
    text = "".join(p.read_text(encoding="utf-8") for p in pages)
    assert "#00AAFF" in text and "#0A0B0C" in text and "#FFC800" not in text  # mực/kem giữ #111111 vì theme thử không đổi chúng


def test_compose_does_not_copy_generated_contact_sheet(video, tmp_path, monkeypatch):
    import shutil
    svg = tmp_path / "svg"
    shutil.copytree(dung.SVG, svg)
    (svg / "thu-vien.png").write_bytes(b"png")  # bảng soi do svg/sheet.py sinh, không thuộc dự án video
    monkeypatch.setattr(dung, "SVG", svg)
    out = dung.compose(video)
    assert not (out / "assets" / "svg" / "thu-vien.png").exists() and (out / "assets" / "svg" / "chip.svg").exists()


def test_render_args_only_includes_set_keys():
    assert dung.render_args({"bitrate": "8M", "max_bitrate": "12M", "keyframe": 2, "grain": 0}) == \
        ["--video-bitrate", "8M", "--max-bitrate", "12M", "--keyframe-interval", "2"]
    assert dung.render_args({}) == [] and dung.render_args({"bitrate": "8M"}) == ["--video-bitrate", "8M"]


def test_compose_adds_grain_overlay_only_when_enabled(video, monkeypatch):
    monkeypatch.setattr(dung, "_render_cfg", lambda: {"grain": 0.02})
    out = dung.compose(video)
    assert (out / "assets" / "grain.png").exists()
    assert "assets/grain.png" in (out / "index.html").read_text(encoding="utf-8")
    monkeypatch.setattr(dung, "_render_cfg", lambda: {})
    out = dung.compose(video)
    assert not (out / "assets" / "grain.png").exists() and "grain" not in (out / "index.html").read_text(encoding="utf-8")


def test_minh_hoa_variables_for_stage_layout_and_camera(video):
    sc = json.loads((video / "canh.json").read_text(encoding="utf-8"))
    sc["scenes"][1].update({"san_khau": "may-chu", "may_quay": "day-vao",
                            "bo_cuc": [{"svg": "cay", "x": 0.2, "y": 0.6, "to": 1.0}]})
    (video / "canh.json").write_text(json.dumps(sc, ensure_ascii=False), encoding="utf-8")
    html = (dung.compose(video) / "index.html").read_text(encoding="utf-8")
    vals = {sid: json.loads(v.replace("&#39;", "'")) for sid, v in
            re.findall(r'<div id="([\w-]+)"[^>]*?data-variable-values=\'([^\']*)\'', html)}
    c2 = vals["c2"]
    assert c2["phong"] == "assets/svg/phong-may-chu.svg" and c2["may_quay"] == "day-vao" and c2["thoi_luong"] == 5.0
    assert json.loads(c2["bo_cuc"]) == [{"svg": "assets/svg/cay.svg", "x": 0.2, "y": 0.6, "to": 1.0}]


def test_old_minh_hoa_defaults_to_ground_slab_and_still_camera(video):
    html = (dung.compose(video) / "index.html").read_text(encoding="utf-8")
    vals = {sid: json.loads(v.replace("&#39;", "'")) for sid, v in
            re.findall(r'<div id="([\w-]+)"[^>]*?data-variable-values=\'([^\']*)\'', html)}
    assert vals["c2"]["phong"] == "assets/svg/nen-dat.svg" and vals["c2"]["may_quay"] == "dung"
    assert vals["c2"]["bo_cuc"] == "[]"


def test_sfx_pops_for_each_layout_prop_without_index_error():
    c = {"mau": "minh-hoa", "start": 0, "end": 4, "bo_cuc": [{}] * 4}
    ev = dung.sfx_events(c, [0.72, 0.5, 0.58])
    assert [e[0] for e in ev] == ["pop"] * 5 and all(e[1] >= 0 for e in ev)
    old = dung.sfx_events({"mau": "minh-hoa", "start": 0, "end": 4, "phu": ["cay", "dong-xu"]}, [0.72, 0.5, 0.58])
    assert [e[1] for e in old] == [0.55, 0.5, 0.58]  # hành vi cũ giữ nguyên
