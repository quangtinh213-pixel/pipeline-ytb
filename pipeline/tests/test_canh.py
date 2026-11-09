import re
from pathlib import Path

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
    msgs = canh.validate(_sc((0, 1.2), (1.2, 13.2)), {"duration": 13.2}, tmp_path, NGUON)
    assert len(_errors(msgs)) == 2  # 1,2 s (dưới 1,5) và 12 s (trên 10)
    warn = canh.validate(_sc((0, 2), (2, 9)), {"duration": 9.0}, tmp_path, NGUON)
    assert _errors(warn) == [] and len([m for m in warn if m.startswith("Cảnh báo")]) == 2  # 2 s và 7 s
    assert canh.validate(_sc((0, 3), (3, 6)), {"duration": 6.0}, tmp_path, NGUON) == []


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


SRC = [{"id": "p1", "gia_tri": "522.500 đ"}, {"id": "t1", "gia_tri": "5,3 tỷ USD"}]


def test_number_scenes_require_source(tmp_path):
    sc = _sc((0, 6), (6, 12), so=522500, nhan="Plus")
    errs = _errors(canh.validate(sc, TIMING, tmp_path, SRC))
    assert any("nguon_id" in e for e in errs)


def test_screen_value_must_match_source(tmp_path):
    ok = _sc((0, 6), (6, 12), so=522500, sau=" đ", nguon_id="p1")
    assert _errors(canh.validate(ok, TIMING, tmp_path, SRC)) == []
    bad = _sc((0, 6), (6, 12), so=525000, sau=" đ", nguon_id="p1")
    assert any("525" in e for e in _errors(canh.validate(bad, TIMING, tmp_path, SRC)))
    dec = _sc((0, 6), (6, 12), so=5.3, sau=" tỷ USD", nguon_id="t1")
    assert _errors(canh.validate(dec, TIMING, tmp_path, SRC)) == []
    scale = _sc((0, 6), (6, 12), so=5.3, sau=" triệu USD", nguon_id="t1")
    assert _errors(canh.validate(scale, TIMING, tmp_path, SRC))


def test_chart_values_must_match_source(tmp_path):
    chart = {"kieu": "cot", "nhan_x": ["A", "B"], "gia_tri": [522500, 999], "don_vi": "đ", "nguon_id": "p1"}
    sc = _sc((0, 6), (6, 12), mau="bieu-do", bieu_do=chart)
    assert any("999" in e for e in _errors(canh.validate(sc, TIMING, tmp_path, SRC)))


def test_validate_missing_keyword(tmp_path):
    timing = {"duration": 12.0, "words": [{"w": "Plus", "start": 7.0, "end": 7.3}]}
    ok = _sc((0, 6), (6, 12))
    ok["scenes"][1]["nhip"] = ["Plus"]
    assert _errors(canh.validate(ok, timing, tmp_path, SRC)) == []
    bad = _sc((0, 6), (6, 12))
    bad["scenes"][0]["nhip"] = ["Plus"]                       # từ nằm ở cảnh sau
    assert any("Plus" in e for e in _errors(canh.validate(bad, timing, tmp_path, SRC)))


TRICH = [{"id": "b1", "gia_tri": "", "trich_dan": "Giá RAM DDR5 tăng gấp ba lần chỉ trong sáu tháng, theo TrendForce.",
          "url": "https://vnexpress.net/abc", "ngay_truy_cap": "2026-11-07", "trang_thai": "xac-minh"}]


def test_trich_bao_must_quote_source_exactly(tmp_path):
    sc = _sc((0, 6), (6, 12), mau="trich-bao", nguon_id="b1",
             trich="Giá RAM DDR5 tăng gấp ba lần chỉ trong sáu tháng", to_vang="tăng gấp ba lần")
    assert _errors(canh.validate(sc, TIMING, tmp_path, TRICH)) == []
    sai = _sc((0, 6), (6, 12), mau="trich-bao", nguon_id="b1", trich="Giá RAM tăng gấp bốn lần", to_vang="gấp bốn")
    assert any("trích" in e for e in _errors(canh.validate(sai, TIMING, tmp_path, TRICH)))
    lech = _sc((0, 6), (6, 12), mau="trich-bao", nguon_id="b1",
               trich="Giá RAM DDR5 tăng gấp ba lần chỉ trong sáu tháng", to_vang="gấp năm")
    assert any("tô vàng" in e for e in _errors(canh.validate(lech, TIMING, tmp_path, TRICH)))
    thieu = _sc((0, 6), (6, 12), mau="trich-bao", trich="abc", to_vang="")
    assert any("nguon_id" in e for e in _errors(canh.validate(thieu, TIMING, tmp_path, TRICH)))


def test_broll_scene_needs_video_file(tmp_path):
    sc = _sc((0, 6), (6, 12), mau="b-roll", video="pexels-1.mp4", nhan="QUY MÔ")
    assert any("pexels-1.mp4" in e for e in _errors(canh.validate(sc, TIMING, tmp_path, SRC, video_dir=tmp_path)))
    (tmp_path / "broll").mkdir()
    (tmp_path / "broll" / "pexels-1.mp4").write_bytes(b"x")
    assert _errors(canh.validate(sc, TIMING, tmp_path, SRC, video_dir=tmp_path)) == []


def test_validate_rejects_unknown_dong(tmp_path):
    bad = canh.validate(_sc((0, 6), (6, 12), dong="nhay"), TIMING, tmp_path, NGUON)
    assert sum("dong" in m and m.startswith("Lỗi") for m in bad) == 2
    ok = canh.validate(_sc((0, 6), (6, 12), dong="xoay"), TIMING, tmp_path, NGUON)
    assert _errors(ok) == []


def _qt(n, **extra):
    return dict({"buoc": [{"nhan": f"B{i}"} for i in range(n)]}, **extra)


def _qt_scene(**c):
    return {"scenes": [dict({"id": "c0", "mau": "quy-trinh", "start": 0, "end": 6}, **c)]}


def test_validate_quy_trinh_step_count(tmp_path):
    for n, ok in [(2, False), (3, True), (4, True), (6, True), (7, False)]:
        msgs = canh.validate(_qt_scene(**_qt(n)), {"duration": 6.0}, tmp_path, NGUON)
        assert (_errors(msgs) == []) is ok, n


def test_validate_quy_trinh_noi_bat_in_range(tmp_path):
    assert _errors(canh.validate(_qt_scene(**_qt(4, noi_bat=3)), {"duration": 6.0}, tmp_path, NGUON)) == []
    assert any("noi_bat" in e for e in _errors(canh.validate(_qt_scene(**_qt(4, noi_bat=4)), {"duration": 6.0}, tmp_path, NGUON)))


def test_validate_quy_trinh_svg_exists(tmp_path):
    c = _qt_scene(buoc=[{"nhan": "A", "svg": "chip"}, {"nhan": "B"}, {"nhan": "C", "svg": "thieu"}])
    errs = _errors(canh.validate(c, {"duration": 6.0}, _svg(tmp_path, "chip"), NGUON))
    assert len(errs) == 1 and "thieu" in errs[0]


SS_SRC = [{"id": "n1", "gia_tri": "Blackwell 208 tỷ transistor; VGC 300 triệu transistor"}]


def _ss(**c):
    side = lambda so, don_vi: {"nhan": "X", "svg": "chip", "so": so, "don_vi": don_vi}
    base = {"id": "c0", "mau": "so-sanh", "start": 0, "end": 6, "nguon_id": "n1",
            "trai": side(208, "tỷ transistor"), "phai": side(300, "triệu transistor")}
    return {"scenes": [dict(base, **c)]}


def test_check_values_so_sanh_matches_source(tmp_path):
    svg = _svg(tmp_path, "chip")
    assert _errors(canh.validate(_ss(), {"duration": 6.0}, svg, SS_SRC)) == []
    bad = _ss(phai={"nhan": "X", "svg": "chip", "so": 350, "don_vi": "triệu transistor"})
    assert any("350" in e for e in _errors(canh.validate(bad, {"duration": 6.0}, svg, SS_SRC)))
    scale = _ss(phai={"nhan": "X", "svg": "chip", "so": 300, "don_vi": "tỷ transistor"})
    assert any("300" in e for e in _errors(canh.validate(scale, {"duration": 6.0}, svg, SS_SRC)))


def test_validate_so_sanh_requires_nguon_id_when_number(tmp_path):
    svg = _svg(tmp_path, "chip")
    errs = _errors(canh.validate(_ss(nguon_id=None), {"duration": 6.0}, svg, SS_SRC))
    assert any("nguon_id" in e for e in errs)
    no_num = _ss(nguon_id=None, trai={"nhan": "A", "svg": "chip"}, phai={"nhan": "B", "svg": "chip"})
    assert _errors(canh.validate(no_num, {"duration": 6.0}, svg, SS_SRC)) == []


def test_validate_so_sanh_to_range_and_sides(tmp_path):
    svg = _svg(tmp_path, "chip")
    for to in (0, 1.5):
        bad = _ss(phai={"nhan": "B", "svg": "chip", "to": to})
        assert any("to" in e for e in _errors(canh.validate(bad, {"duration": 6.0}, svg, SS_SRC))), to
    ok = _ss(nguon_id=None, trai={"nhan": "A", "svg": "chip", "to": 1.0}, phai={"nhan": "B", "svg": "chip", "to": 0.15})
    assert _errors(canh.validate(ok, {"duration": 6.0}, svg, SS_SRC)) == []
    thieu = _ss(nguon_id=None, trai={"nhan": "A", "svg": "chip"}, phai=None)
    assert any("phai" in e for e in _errors(canh.validate(thieu, {"duration": 6.0}, svg, SS_SRC)))


TG_SRC = [{"id": "n1", "gia_tri": "Singapore khởi công 2024, sản xuất 2026; Ấn Độ khởi công 2024, chạy thương mại 2028"}]


def _tg(**c):
    base = {"id": "c0", "mau": "thoi-gian", "start": 0, "end": 6, "nguon_id": "n1",
            "truc": {"tu": 2024, "den": 2030, "don_vi": "năm"},
            "hang": [{"nhan": "Singapore", "tu": 2024, "den": 2026}, {"nhan": "Ấn Độ", "tu": 2024, "den": 2028, "noi_bat": True}]}
    return {"scenes": [dict(base, **c)]}


def _tg_errors(sc, src=TG_SRC):
    return _errors(canh.validate(sc, {"duration": 6.0}, Path("."), src))


def test_validate_thoi_gian_rows_in_axis():
    assert _tg_errors(_tg()) == []
    ngoai = _tg(hang=[{"nhan": "A", "tu": 2024, "den": 2026}, {"nhan": "B", "tu": 2024, "den": 2031}])
    assert any("trục" in e for e in _tg_errors(ngoai, [{"id": "n1", "gia_tri": "2024 2026 2031"}]))
    nguoc = _tg(hang=[{"nhan": "A", "tu": 2026, "den": 2026}, {"nhan": "B", "tu": 2024, "den": 2028}])
    assert any("tu < den" in e for e in _tg_errors(nguoc))
    assert any("trục" in e for e in _tg_errors(_tg(truc={"tu": 2030, "den": 2024, "don_vi": "năm"})))


def test_validate_thoi_gian_row_count():
    row = {"nhan": "A", "tu": 2024, "den": 2026}
    assert any("2–5" in e for e in _tg_errors(_tg(hang=[row])))
    assert any("2–5" in e for e in _tg_errors(_tg(hang=[row] * 6)))
    assert _tg_errors(_tg(hang=[row] * 5)) == []


def test_check_values_thoi_gian_years_in_source():
    sai = _tg(hang=[{"nhan": "A", "tu": 2025, "den": 2026}, {"nhan": "B", "tu": 2024, "den": 2028}])
    assert any("2025" in e for e in _tg_errors(sai))
    assert any("nguon_id" in e for e in _tg_errors(_tg(nguon_id=None)))


def test_validate_thoi_gian_row_missing_years_is_error_not_crash():
    thieu = _tg(hang=[{"nhan": "A"}, {"nhan": "B", "tu": 2024, "den": 2028}])
    assert any("tu < den" in e for e in _tg_errors(thieu))


def test_validate_dan_pose_and_corner(tmp_path):
    ok = canh.validate(_sc((0, 6), (6, 12), dan={"the": "chao", "goc": "trai"}), TIMING, tmp_path, NGUON)
    assert _errors(ok) == []
    assert any("dan" in e for e in _errors(canh.validate(_sc((0, 6), (6, 12), dan={"the": "bay"}), TIMING, tmp_path, NGUON)))
    assert any("dan" in e for e in _errors(canh.validate(_sc((0, 6), (6, 12), dan={"the": "chao", "goc": "giua"}), TIMING, tmp_path, NGUON)))
    assert any("dan" in e for e in _errors(canh.validate(_sc((0, 6), (6, 12), dan="chao"), TIMING, tmp_path, NGUON)))


def test_validate_dan_phrase_must_be_spoken_in_scene(tmp_path):
    timing = {"duration": 12.0, "words": [{"w": "năm", "start": 1.0, "end": 1.3}, {"w": "trăm", "start": 1.3, "end": 1.6}]}
    sc = {"scenes": [{"id": "c0", "mau": "so-lon", "start": 0, "end": 6, "dan": {"the": "nghi", "tu": "năm trăm"}},
                     {"id": "c1", "mau": "so-lon", "start": 6, "end": 12, "dan": {"the": "nghi", "tu": "năm trăm"}}]}
    errs = _errors(canh.validate(sc, timing, tmp_path, NGUON))
    assert len(errs) == 1 and "c1" in errs[0] and "năm trăm" in errs[0]
