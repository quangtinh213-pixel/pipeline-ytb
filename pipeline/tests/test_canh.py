import json
import re
from pathlib import Path

from tttc import canh, nhan_vat

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


def test_non_numeric_screen_value_is_an_error_not_a_crash(tmp_path):
    sc = _sc((0, 6), (6, 12), so="8/11", nhan="Ngày", nguon_id="p1")  # ngày tháng không phải số: báo Lỗi, không văng traceback
    errs = _errors(canh.validate(sc, TIMING, tmp_path, SRC))
    assert any("8/11" in e and "số" in e for e in errs)


def test_big_number_start_value_must_match_source_too(tmp_path):
    ok = _sc((0, 6), (6, 12), so=522500, tu=132000, sau=" đ", nguon_id="p1")
    src = [{"id": "p1", "gia_tri": "132.000 đ → 522.500 đ"}]
    assert _errors(canh.validate(ok, TIMING, tmp_path, src)) == []
    bad = _sc((0, 6), (6, 12), so=522500, tu=140000, sau=" đ", nguon_id="p1")
    assert any("140" in e for e in _errors(canh.validate(bad, TIMING, tmp_path, src)))


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


EN_SRC = [{"id": "e1", "gia_tri": "", "trich_dan": "Vietnam: [D:1] National Security X; [D:3] Chemical and Biological X"}]


def _qe(**extra):
    base = dict(mau="trich-bao", nguon_id="e1", trich="Vietnam: [D:1] National Security X", to_vang="National Security X")
    return _sc((0, 6), (6, 12), **{**base, **extra})


def test_english_quote_needs_vietnamese_translation_for_screen(tmp_path):
    errs = _errors(canh.validate(_qe(), TIMING, tmp_path, EN_SRC, kit=None))
    assert any("trich_vi" in e for e in errs)
    ok = _qe(trich_vi="Việt Nam: nhóm D:1 an ninh quốc gia", to_vang_vi="an ninh quốc gia")
    assert _errors(canh.validate(ok, TIMING, tmp_path, EN_SRC, kit=None)) == []


def test_translation_must_be_vietnamese_and_contain_the_highlight(tmp_path):
    en = _qe(trich_vi="Vietnam is in the D:1 national security group", to_vang_vi="national security")
    assert any("tiếng Anh" in e for e in _errors(canh.validate(en, TIMING, tmp_path, EN_SRC, kit=None)))
    lech = _qe(trich_vi="Việt Nam thuộc nhóm D:1", to_vang_vi="an ninh quốc gia")
    assert any("to_vang_vi" in e for e in _errors(canh.validate(lech, TIMING, tmp_path, EN_SRC, kit=None)))


def test_english_label_on_screen_is_an_error(tmp_path):
    sc = _sc((0, 6), (6, 12), mau="minh-hoa", svg="chip", nhan="Export controls on AI chips")
    errs = _errors(canh.validate(sc, TIMING, _svg(tmp_path, "chip"), NGUON, kit=None))
    assert any("tiếng Anh" in e and "nhan" in e for e in errs)
    ok = _sc((0, 6), (6, 12), mau="minh-hoa", svg="chip", nhan="Siết xuất khẩu chip AI")
    assert _errors(canh.validate(ok, TIMING, _svg(tmp_path, "chip"), NGUON, kit=None)) == []


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
    run = lambda dan: _errors(canh.validate(_sc((0, 6), (6, 12), dan=dan), TIMING, tmp_path, NGUON, kit=KIT))
    assert run({"the": "chao", "goc": "phai"}) == []
    assert any("dan" in e for e in run({"the": "bay"}))
    assert any("dan" in e for e in run({"the": "chao", "goc": "giua"}))
    assert any("dan" in e for e in run("chao"))


KIT = {"the": ["chao", "nghi"], "huong": ["truoc", "nghieng-trai", "nghieng-phai", "ngang"],
       "dang": [["chao", "truoc"], ["chao", "nghieng-trai"], ["nghi", "truoc"]], "nham": []}


def test_validate_dan_with_kit_checks_expression_and_direction(tmp_path):
    def run(**dan):
        return _errors(canh.validate(_sc((0, 6), (6, 12), dan=dan), TIMING, tmp_path, NGUON, kit=KIT))
    assert any("huong" in e for e in run(the="chao", huong="ngang"))           # cặp không có trong kit
    assert run(the="chao", goc="phai") == []                                    # huong mặc định nghieng-trai hợp lệ
    assert any("dan" in e for e in run(the="ngac-nhien"))                       # the không nằm trong kit
    assert any("huong" in e for e in run(the="nghi", goc="phai"))               # nghi + nghieng-trai không có trong kit


def test_validate_dan_needs_the_character_kit_and_reads_default_kit(tmp_path, monkeypatch):
    sc = _sc((0, 6), (6, 12), dan={"the": "ngac-nhien"})
    assert any("kit.json" in e for e in _errors(canh.validate(sc, TIMING, tmp_path, NGUON, kit=None)))  # không có bộ nhân vật: Lỗi rõ ràng
    monkeypatch.setattr(nhan_vat, "KIT", tmp_path / "khong-co" / "kit.json")
    assert any("kit.json" in e for e in _errors(canh.validate(sc, TIMING, tmp_path, NGUON)))
    (tmp_path / "kit.json").write_text(json.dumps(KIT), encoding="utf-8")
    monkeypatch.setattr(nhan_vat, "KIT", tmp_path / "kit.json")  # có tệp: dùng luật của kit mặc định
    assert any("dan" in e for e in _errors(canh.validate(sc, TIMING, tmp_path, NGUON)))
    real = canh.validate(_sc((0, 6), (6, 12), dan={"the": "ngac-nhien"}), TIMING, tmp_path, NGUON, kit=json.loads((nhan_vat.PIPE / "nhan-vat" / "kit.json").read_text()))
    assert _errors(real) == []  # bộ nhân vật thật của kênh có biểu cảm này ở hướng mặc định


def test_validate_dan_phrase_must_be_spoken_in_scene(tmp_path):
    timing = {"duration": 12.0, "words": [{"w": "năm", "start": 1.0, "end": 1.3}, {"w": "trăm", "start": 1.3, "end": 1.6}]}
    sc = {"scenes": [{"id": "c0", "mau": "so-lon", "start": 0, "end": 6, "dan": {"the": "nghi", "tu": "năm trăm"}},
                     {"id": "c1", "mau": "so-lon", "start": 6, "end": 12, "dan": {"the": "nghi", "tu": "năm trăm"}}]}
    errs = _errors(canh.validate(sc, timing, tmp_path, NGUON))
    assert len(errs) == 1 and "c1" in errs[0] and "năm trăm" in errs[0]


def _cue_timing(text):
    ws = text.split()
    return {"words": [{"w": w, "start": i * 0.5, "end": i * 0.5 + 0.4} for i, w in enumerate(ws)], "duration": len(ws) * 0.5}


def test_cues_break_at_comma_before_mid_phrase():
    out = [c[2] for c in canh.cues(_cue_timing("Họ nói giá sẽ tăng, nhưng chưa nói tăng bao nhiêu phần trăm."), 30)]
    assert out[0] == "Họ nói giá sẽ tăng," and all(len(x) <= 30 for x in out)


def test_cues_forced_break_falls_back_to_last_comma():
    out = [c[2] for c in canh.cues(_cue_timing("Một hai ba bốn năm, sáu bảy tám chín mười mười một"), 24)]
    assert out[0] == "Một hai ba bốn năm," and all(len(x) <= 24 for x in out)


def test_cues_short_clause_is_not_split_off_alone():
    out = [c[2] for c in canh.cues(_cue_timing("Năm ngoái, Mỹ bắt chip AI xuất sang Malaysia và Thái Lan phải có thêm giấy phép."), 42)]
    assert out[0] != "Năm ngoái," and all(len(x) <= 42 for x in out)


def test_cues_never_leave_single_word_orphan_inside_a_sentence():
    out = [c[2] for c in canh.cues(_cue_timing("a b c d e f g h i j k l m n o p"), 10)]
    assert all(len(x.split()) >= 2 for x in out) and " ".join(out) == "a b c d e f g h i j k l m n o p"


def test_cues_respect_max_chars_and_sentence_end():
    out = [c[2] for c in canh.cues(_cue_timing("Một hai ba bốn năm. Sáu bảy tám chín mười mười một."), 20)]
    assert out[0].endswith("năm.") and all(len(x) <= 20 for x in out)


def test_cues_keep_one_word_sentences_and_cover_timing():
    t = _cue_timing("Được. Rồi.")
    out = canh.cues(t, 20)
    assert [c[2] for c in out] == ["Được.", "Rồi."]
    assert out[0][0] == t["words"][0]["start"] and out[-1][1] == t["words"][-1]["end"]


def test_cues_empty_timing():
    assert canh.cues({"words": []}) == []


def test_long_pill_label_warns_over_five_words():
    sc = {"scenes": [{"id": "c1", "mau": "minh-hoa", "start": 0, "end": 3, "svg": "chip", "nhan": "một hai ba bốn năm sáu"}]}
    out = canh.validate(sc, {"duration": 3.0, "words": []})
    assert any(m.startswith("Cảnh báo: c1 nhãn dài 6 từ") for m in out)
    sc["scenes"][0]["nhan"] = "một hai ba bốn năm"
    assert not any("nhãn dài" in m for m in canh.validate(sc, {"duration": 3.0, "words": []}))


def test_long_label_check_covers_so_sanh_and_quy_trinh_but_not_so_lon_caption():
    long = "một hai ba bốn năm sáu bảy"
    ss = {"id": "c2", "mau": "so-sanh", "start": 0, "end": 3, "trai": {"nhan": long, "svg": "chip"},
          "phai": {"nhan": "Ngắn", "svg": "chip"}}
    qt = {"id": "c3", "mau": "quy-trinh", "start": 3, "end": 6, "buoc": [{"nhan": "A"}, {"nhan": long}, {"nhan": "C"}]}
    sl = {"id": "c4", "mau": "so-lon", "start": 6, "end": 9, "so": 5, "nhan": long}
    out = canh.validate({"scenes": [ss, qt, sl]}, {"duration": 9.0, "words": []})
    flagged = {m.split()[2] for m in out if "nhãn dài" in m}
    assert flagged == {"c2", "c3"}


def _mh(**kw):
    return {"scenes": [{"id": "c1", "mau": "minh-hoa", "start": 0, "end": 4, "svg": "chip", **kw}]}


T4 = {"duration": 4.0, "words": []}
BC1 = {"svg": "cay", "x": 0.2, "y": 0.6, "to": 1.0}


def _svgs(tmp_path):
    for f in ("nen-dat", "san-khau-may-chu", "chip", "cay"):
        (tmp_path / f"{f}.svg").write_text("<svg/>", encoding="utf-8")
    return tmp_path


def test_minh_hoa_stage_camera_and_layout_valid(tmp_path):
    ok = canh.validate(_mh(san_khau="may-chu", may_quay="day-vao", bo_cuc=[BC1]), T4, _svgs(tmp_path))
    assert [m for m in ok if m.startswith("Lỗi")] == []
    assert canh.san_khau_hop_le(tmp_path) == {"nen-dat", "may-chu"}


def test_minh_hoa_rejects_unknown_stage_camera_and_bad_layout(tmp_path):
    d = _svgs(tmp_path)
    assert any("san_khau" in m for m in canh.validate(_mh(san_khau="mars"), T4, d))
    assert any("may_quay" in m for m in canh.validate(_mh(may_quay="xoay-tit"), T4, d))
    assert any("bo_cuc" in m for m in canh.validate(_mh(bo_cuc=[{**BC1, "x": 1.5}]), T4, d))
    assert any("bo_cuc" in m for m in canh.validate(_mh(bo_cuc=[{**BC1, "to": 3}]), T4, d))
    assert any("bo_cuc" in m for m in canh.validate(_mh(bo_cuc=[BC1] * 5), T4, d))
    assert any("bo_cuc" in m for m in canh.validate(_mh(bo_cuc=[{**BC1, "svg": "khong-co"}]), T4, d))
    assert any("phu" in m and "bo_cuc" in m for m in canh.validate(_mh(phu=["cay"], bo_cuc=[BC1]), T4, d))


def test_old_minh_hoa_without_new_fields_has_no_new_errors(tmp_path):
    assert [m for m in canh.validate(_mh(), T4, _svgs(tmp_path)) if m.startswith("Lỗi")] == []


def _bd(**c):
    base = {"diem": [{"nhan": "Mỹ", "vi_do": 38.9, "kinh_do": -77.0}, {"nhan": "Malaysia", "vi_do": 3.1, "kinh_do": 101.7},
                     {"nhan": "Việt Nam", "vi_do": 21.0, "kinh_do": 105.8, "noi_bat": True}],
            "noi": [{"tu": 0, "den": 1, "nhan": "chip AI"}, {"tu": 1, "den": 2}]}
    return {"scenes": [dict({"id": "c0", "mau": "ban-do", "start": 0, "end": 6}, **{**base, **c}),
                       {"id": "c1", "mau": "chuong", "start": 6, "end": 12, "so": "Phần 2"}]}


def test_ban_do_valid_scene_has_no_errors(tmp_path):
    assert _errors(canh.validate(_bd(), TIMING, tmp_path, NGUON, kit=None)) == []


def test_ban_do_rejects_bad_points_and_links(tmp_path):
    def errs(**c):
        return _errors(canh.validate(_bd(**c), TIMING, tmp_path, NGUON, kit=None))
    assert any("2–6" in e for e in errs(diem=[{"nhan": "A", "vi_do": 1, "kinh_do": 1}]))
    assert any("vi_do" in e for e in errs(diem=[{"nhan": "A", "vi_do": 95, "kinh_do": 1}, {"nhan": "B", "vi_do": 1, "kinh_do": 1}]))
    assert any("kinh_do" in e for e in errs(diem=[{"nhan": "A", "vi_do": 1, "kinh_do": 200}, {"nhan": "B", "vi_do": 1, "kinh_do": 1}]))
    assert any("noi" in e for e in errs(noi=[{"tu": 0, "den": 7}]))
    assert any("noi" in e for e in errs(noi=[{"tu": 1, "den": 1}]))


def test_ban_do_country_code_must_exist_in_map_data(tmp_path):
    ok = _bd(diem=[{"nhan": "Mỹ", "vi_do": 38.9, "kinh_do": -77.0, "nuoc": "USA"}, {"nhan": "Việt Nam", "vi_do": 21, "kinh_do": 105.8, "nuoc": "VNM"}], noi=[{"tu": 0, "den": 1}])
    assert _errors(canh.validate(ok, TIMING, tmp_path, NGUON, kit=None)) == []
    bad = _bd(diem=[{"nhan": "Mỹ", "vi_do": 38.9, "kinh_do": -77.0, "nuoc": "XXX"}, {"nhan": "Việt Nam", "vi_do": 21, "kinh_do": 105.8}], noi=[{"tu": 0, "den": 1}])
    assert any("nuoc" in e and "XXX" in e for e in _errors(canh.validate(bad, TIMING, tmp_path, NGUON, kit=None)))


def test_ban_do_labels_must_be_vietnamese_and_short(tmp_path):
    en = _bd(diem=[{"nhan": "United States of America", "vi_do": 38.9, "kinh_do": -77.0}, {"nhan": "Malaysia", "vi_do": 3.1, "kinh_do": 101.7}])
    assert any("tiếng Anh" in e for e in _errors(canh.validate(en, TIMING, tmp_path, NGUON, kit=None)))
    long = _bd(diem=[{"nhan": "Một hai ba bốn năm sáu bảy", "vi_do": 1, "kinh_do": 1}, {"nhan": "B", "vi_do": 1, "kinh_do": 2}])
    assert any("nhãn dài" in m for m in canh.validate(long, TIMING, tmp_path, NGUON, kit=None))


XH_SRC = [{"id": "x1", "gia_tri": "Nvidia 4,5 nghìn tỷ USD; AMD 1,2 nghìn tỷ USD; Intel 0,8 nghìn tỷ USD"}]


def _xh(**c):
    base = {"hang": [{"nhan": "Nvidia", "so": 4.5}, {"nhan": "AMD", "so": 1.2}, {"nhan": "Intel", "so": 0.8}],
            "don_vi": "nghìn tỷ USD", "nguon_id": "x1", "noi_bat": 0}
    return {"scenes": [dict({"id": "c0", "mau": "xep-hang", "start": 0, "end": 6}, **{**base, **c}),
                       {"id": "c1", "mau": "chuong", "start": 6, "end": 12, "so": "Phần 2"}]}


def test_xep_hang_valid_scene_has_no_errors(tmp_path):
    assert _errors(canh.validate(_xh(), TIMING, tmp_path, XH_SRC, kit=None)) == []


def test_xep_hang_rejects_bad_rows_and_unsourced_values(tmp_path):
    def errs(sc, src=XH_SRC):
        return _errors(canh.validate(sc, TIMING, tmp_path, src, kit=None))
    assert any("2–8" in e for e in errs(_xh(hang=[{"nhan": "A", "so": 1}])))
    assert any("noi_bat" in e for e in errs(_xh(noi_bat=7)))
    assert any("so" in e for e in errs(_xh(hang=[{"nhan": "A"}, {"nhan": "B", "so": 2}])))
    assert any("9.9" in e for e in errs(_xh(hang=[{"nhan": "A", "so": 9.9}, {"nhan": "B", "so": 1.2}])))  # không khớp nguồn
    assert any("nguon_id" in e for e in errs(_xh(nguon_id=None)))


def test_xep_hang_labels_must_be_vietnamese(tmp_path):
    en = _xh(hang=[{"nhan": "The biggest chip maker", "so": 4.5}, {"nhan": "AMD", "so": 1.2}])
    assert any("tiếng Anh" in e for e in _errors(canh.validate(en, TIMING, tmp_path, XH_SRC, kit=None)))


RACE_SRC = [{"id": "x1", "gia_tri": "2022: 0,4 nghìn tỷ USD; 1,2 nghìn tỷ USD; 2024: 3,3 nghìn tỷ USD; 0,9 nghìn tỷ USD; 2026: 4,5 nghìn tỷ USD; 1,4 nghìn tỷ USD"}]


def _race(**c):
    base = {"moc": ["2022", "2024", "2026"], "don_vi": "nghìn tỷ USD", "nguon_id": "x1", "noi_bat": 0,
            "hang": [{"nhan": "Nvidia", "so": [0.4, 3.3, 4.5]}, {"nhan": "TSMC", "so": [1.2, 0.9, 1.4]}]}
    return {"scenes": [dict({"id": "c0", "mau": "xep-hang", "start": 0, "end": 8}, **{**base, **c}),
                       {"id": "c1", "mau": "chuong", "start": 8, "end": 12, "so": "Phần 2"}]}


def test_xep_hang_race_valid_scene_has_no_errors(tmp_path):
    t = {"duration": 12.0, "words": [], "paragraphs": []}
    assert _errors(canh.validate(_race(), t, tmp_path, RACE_SRC, kit=None)) == []


def test_xep_hang_race_rejects_length_mismatch_and_unsourced_values(tmp_path):
    t = {"duration": 12.0, "words": [], "paragraphs": []}
    errs = lambda sc: _errors(canh.validate(sc, t, tmp_path, RACE_SRC, kit=None))
    assert any("moc" in e for e in errs(_race(hang=[{"nhan": "A", "so": [1, 2]}, {"nhan": "B", "so": [1, 2, 3]}])))
    assert any("7.7" in e for e in errs(_race(hang=[{"nhan": "A", "so": [0.4, 7.7, 4.5]}, {"nhan": "B", "so": [1.2, 0.9, 1.4]}])))
    assert any("moc" in e for e in errs(_race(moc=["2022"])))


def test_broll_keyword_and_split_numbers_must_match_source(tmp_path):
    src = [{"id": "g1", "gia_tri": "Giảm 2.000 đồng; gói 3.000 tỷ đồng"}]
    def errs(**kw):
        sc = {"scenes": [dict({"id": "c1", "mau": "b-roll", "start": 0, "end": 4, "video": "a.mp4"}, **kw)]}
        return _errors(canh.validate(sc, {"duration": 4.0, "words": []}, tmp_path, src, kit=None))
    assert errs(tu_khoa="Mỗi cuốc bớt phí") == []                      # không có số: không cần nguồn
    assert any("nguon_id" in e for e in errs(tu_khoa="Bớt 2.000 đồng"))
    assert errs(tu_khoa="Bớt 2.000 đồng", nguon_id="g1") == []
    assert any("2.500" in e for e in errs(tu_khoa="Bớt 2.500 đồng", nguon_id="g1"))
    assert errs(chia={"so": "3.000", "sau": " tỷ đồng", "nhan": "Gói hỗ trợ"}, nguon_id="g1") == []
    assert any("3.500" in e for e in errs(chia={"so": "3.500", "sau": " tỷ đồng", "nhan": "Gói"}, nguon_id="g1"))
