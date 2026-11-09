import json

from tttc import canh_remap


def T(words, step=1.0):
    ws = [{"w": w, "start": i * step, "end": (i + 1) * step} for i, w in enumerate(words)]
    return {"duration": len(words) * step, "words": ws}


OLD = T("một hai ba bốn năm sáu bảy tám chín mười".split())
CANH = {"scenes": [{"id": "c1", "start": 0.0, "end": 5.0, "mau": "so-lon"},
                   {"id": "c2", "start": 5.0, "end": 10.0, "mau": "minh-hoa", "nhan": "X"}]}


def test_remap_shifts_scenes_when_words_are_inserted():
    new = T("một hai THÊM THÊM ba bốn năm sáu bảy tám chín mười".split())
    out, notes = canh_remap.remap(CANH, OLD, new)
    s = out["scenes"]
    assert s[0]["start"] == 0.0 and s[0]["end"] == s[1]["start"] == 7.0 and s[1]["end"] == new["duration"]
    assert s[1]["mau"] == "minh-hoa" and s[1]["nhan"] == "X" and notes == []


def test_remap_flags_scene_whose_words_were_rewritten():
    new = T("một hai ba bốn năm AAA BBB CCC DDD EEE".split())
    _, notes = canh_remap.remap(CANH, OLD, new)
    assert len(notes) == 1 and "c2" in notes[0] and "cần xem lại" in notes[0]


def test_remap_keeps_scenes_contiguous_when_text_is_shorter():
    new = T("một hai ba bốn năm sáu bảy".split())
    out, _ = canh_remap.remap(CANH, OLD, new)
    s = out["scenes"]
    assert s[0]["start"] == 0.0 and s[-1]["end"] == new["duration"] and s[0]["end"] == s[1]["start"]


def test_remap_does_not_mutate_input():
    before = json.dumps(CANH)
    canh_remap.remap(CANH, OLD, T("một hai THÊM ba".split()))
    assert json.dumps(CANH) == before


def test_main_backs_up_and_writes(tmp_path, capsys):
    (tmp_path / "canh.json").write_text(json.dumps(CANH), encoding="utf-8")
    (tmp_path / "giong-timing.json").write_text(json.dumps(T("một hai THÊM ba bốn năm sáu bảy tám chín mười".split())), encoding="utf-8")
    old = tmp_path / "timing-cu.json"
    old.write_text(json.dumps(OLD), encoding="utf-8")
    assert canh_remap.main(str(tmp_path), str(old)) == 0
    assert json.loads((tmp_path / "canh-truoc-remap.json").read_text(encoding="utf-8")) == CANH
    assert json.loads((tmp_path / "canh.json").read_text(encoding="utf-8"))["scenes"][1]["start"] == 6.0
