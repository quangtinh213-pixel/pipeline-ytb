"""Bốn mẫu motion graphic mới (chu-dong, phan-tram, mo-dau, ket-thuc) và chuyển cảnh ba lớp / mống mắt."""
import json

from tttc import canh, dung

NGUON = [{"id": "t1", "gia_tri": "25%", "trich_dan": "", "url": "https://chatgpt.com/vi-VN/pricing",
          "ngay_truy_cap": "2026-11-08", "anh_chup": "", "trang_thai": "tu-tinh", "cong_thuc": "132.000 / 522.500"}]
WORDS = [{"w": w, "start": 3 + i * 0.4, "end": 3 + i * 0.4 + 0.3}
         for i, w in enumerate("Bạn có đang trả tiền cho thứ không dùng tới?".split())]
SCENES = [
    {"id": "c1", "mau": "chuong", "start": 0, "end": 3, "so": "Phần 1", "chuong": "Mở đầu"},
    {"id": "c2", "mau": "chu-dong", "start": 3, "end": 7, "cau": "Bạn có đang trả tiền cho thứ không dùng tới?",
     "nhan_tu": "không dùng tới"},
    {"id": "c3", "mau": "mo-dau", "start": 7, "end": 10, "cau": "ChatGPT có bốn gói"},
    {"id": "c4", "mau": "phan-tram", "start": 10, "end": 14, "so": 25, "nhan": "Một phần tư", "nguon_id": "t1"},
    {"id": "c5", "mau": "ket-thuc", "start": 14, "end": 20},
]
TIMING = {"duration": 20.0, "words": WORDS}


def make(tmp_path, scenes=SCENES):
    d = tmp_path / "v"
    d.mkdir()
    (d / "canh.json").write_text(json.dumps({"scenes": scenes}, ensure_ascii=False), encoding="utf-8")
    (d / "giong-timing.json").write_text(json.dumps(TIMING), encoding="utf-8")
    (d / "nguon.json").write_text(json.dumps(NGUON, ensure_ascii=False), encoding="utf-8")
    (d / "giong.mp3").write_bytes(b"mp3")
    return d


def test_new_scenes_validate_clean():
    msgs = canh.validate({"scenes": SCENES}, TIMING, nguon=NGUON, kit=None)
    assert not [m for m in msgs if m.startswith("Lỗi")], msgs


def test_new_scene_rules():
    bad = [dict(SCENES[0]), dict(SCENES[1], nhan_tu="không có"), dict(SCENES[2]), dict(SCENES[3], so=140),
           dict(SCENES[4], start=14, end=17)]
    msgs = "\n".join(canh.validate({"scenes": bad[:4] + [dict(bad[4], end=20)]}, TIMING, nguon=NGUON, kit=None))
    assert "nhan_tu «không có» không nằm trong cau" in msgs and "phan-tram cần so trong 0–100" in msgs
    order = [dict(SCENES[4], start=0, end=6), dict(SCENES[3], start=6, end=20)]
    assert any("ket-thuc phải là cảnh cuối" in m for m in canh.validate({"scenes": order}, TIMING, nguon=NGUON, kit=None))


def test_percent_must_match_source():
    sc = [dict(SCENES[3], start=0, end=20, so=30)]
    assert any(m.startswith("Lỗi") and "c4" in m for m in canh.validate({"scenes": sc}, TIMING, nguon=NGUON, kit=None))


def test_kinetic_words_follow_voice():
    st = dung.steps(SCENES[1], WORDS)
    assert len(st) == 10 and st[0] == 0.0 and abs(st[-1] - 3.6) < 1e-6


def test_compose_new_scenes_and_transitions(tmp_path):
    o = dung.compose(make(tmp_path))
    html = (o / "index.html").read_text(encoding="utf-8")
    assert (o / "assets" / "brand" / "logo.png").is_file()
    assert 'class="tr-p tr-muc-2"' in html          # rời chương: ba lớp tối
    assert "tr-iris" in html and "tr-vien" in html  # vào mo-dau / phan-tram / ket-thuc: mống mắt
    assert 'id="vien-toi"' in html
    kd = (o / "compositions" / "c2.html").read_text(encoding="utf-8")
    assert '__timelines["c2"]' in kd and '"#c2-cd-tu-"' in kd
    md = (o / "compositions" / "c3.html").read_text(encoding="utf-8")
    assert "{{theme:" not in md and "Nhịp Công Nghệ" in md


def test_transitions_kinds():
    k = dict(dung.transitions(SCENES))
    assert k == {1: "muc", 2: "iris", 3: "iris", 4: "iris"}
