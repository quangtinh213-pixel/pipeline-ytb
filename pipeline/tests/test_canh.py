import re

from tttc import canh

TIMING = {"duration": 12.0, "words": [], "paragraphs": []}
NGUON = [{"id": "p1"}]


def _svg(tmp_path, *names):
    for n in names:
        (tmp_path / f"{n}.svg").write_text("<svg/>")
    return tmp_path


def _sc(*spans, **extra):
    return {"scenes": [dict({"id": f"c{i}", "mau": "so-lon", "start": a, "end": b}, **extra)
                       for i, (a, b) in enumerate(spans)]}


def _errors(msgs):
    return [m for m in msgs if m.startswith("Lỗi")]


def test_valid_scenes_have_no_errors(tmp_path):
    assert _errors(canh.validate(_sc((0, 6), (6, 12)), TIMING, tmp_path, NGUON)) == []


def test_validate_scenes_rejects_gap_and_overlap(tmp_path):
    gap = _errors(canh.validate(_sc((0, 5), (5.5, 12)), TIMING, tmp_path, NGUON))
    over = _errors(canh.validate(_sc((0, 6.5), (6, 12)), TIMING, tmp_path, NGUON))
    assert any("hở" in e for e in gap) and any("chồng" in e for e in over)


def test_validate_first_starts_zero_last_ends_duration(tmp_path):
    errs = _errors(canh.validate(_sc((0.8, 6), (6, 11)), TIMING, tmp_path, NGUON))
    assert any("bắt đầu" in e for e in errs) and any("kết thúc" in e for e in errs)
    assert _errors(canh.validate(_sc((0, 6), (6, 11.6)), TIMING, tmp_path, NGUON)) == []


def test_validate_flags_long_or_short_scene(tmp_path):
    t = {"duration": 16.0}
    msgs = canh.validate(_sc((0, 1.5), (1.5, 3), (3, 16)), t, tmp_path, NGUON)
    assert len(_errors(msgs)) == 3  # 1,5 s; 1,5 s; 13 s
    warn = canh.validate(_sc((0, 3), (3, 12)), TIMING, tmp_path, NGUON)
    assert _errors(warn) == [] and len([m for m in warn if m.startswith("Cảnh báo")]) == 2


def test_validate_unknown_template(tmp_path):
    sc = _sc((0, 6), (6, 12))
    sc["scenes"][0]["mau"] = "slide"
    assert any("mẫu" in e for e in _errors(canh.validate(sc, TIMING, tmp_path, NGUON)))


def test_validate_missing_svg_file(tmp_path):
    sc = _sc((0, 6), (6, 12), mau="minh-hoa", svg="chip", nhan="X")
    assert any("chip" in e for e in _errors(canh.validate(sc, TIMING, tmp_path, NGUON)))
    assert _errors(canh.validate(sc, TIMING, _svg(tmp_path, "chip"), NGUON)) == []


def test_validate_chart_source_exists(tmp_path):
    chart = {"kieu": "cot", "nhan_x": ["A"], "gia_tri": [1], "don_vi": "đ", "nguon_id": "zz"}
    sc = _sc((0, 6), (6, 12), mau="bieu-do", bieu_do=chart)
    assert any("zz" in e for e in _errors(canh.validate(sc, TIMING, tmp_path, NGUON)))


def _words(text, step=0.4):
    return [{"w": w, "start": i * step, "end": i * step + 0.35} for i, w in enumerate(text.split())]


def test_srt_lines_max_42_chars_and_ordered():
    text = ("Gói ChatGPT Plus có giá năm trăm hai mươi hai nghìn năm trăm đồng mỗi tháng. "
            "Còn Google AI Pro rẻ hơn một chút.")
    srt = canh.to_srt({"words": _words(text)})
    blocks = srt.strip().split("\n\n")
    assert len(blocks) >= 3
    starts = []
    for i, b in enumerate(blocks, 1):
        num, times, line = b.split("\n")
        assert num == str(i) and len(line) <= 42
        assert re.match(r"\d\d:\d\d:\d\d,\d{3} --> \d\d:\d\d:\d\d,\d{3}$", times)
        starts.append(times[:12])
    assert starts == sorted(starts)
    assert " ".join(b.split("\n")[2] for b in blocks) == text


def test_srt_breaks_after_sentence_end():
    srt = canh.to_srt({"words": _words("Xin chào. Hôm nay")})
    assert srt.split("\n\n")[0].endswith("Xin chào.")


def test_srt_time_format_over_one_minute():
    srt = canh.to_srt({"words": [{"w": "A", "start": 61.25, "end": 62.5}]})
    assert "00:01:01,250 --> 00:01:02,500" in srt
