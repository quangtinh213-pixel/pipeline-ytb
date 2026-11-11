import unicodedata
from pathlib import Path

import pytest

from tttc import phong_cach

OK_HEAD = "Viettel ra chip 28 nanomet, nhưng liệu thế đã đủ? [#v1] "


def _script(spoken: str) -> str:
    return f"#### Beat 1: Mở đầu\n[TRÊN MÀN HÌNH]: chữ lớn\n**Lời đọc:**\n{spoken}\n"


def _filler(n: int) -> str:
    return " ".join(["từ"] * (n - 1) + ["xong."])


def _long(head="", tail="", n=2300):
    body = _filler(n - len(head.split()) - len(tail.split()))
    return _script(head + body + " " + tail)


def _w(msgs, key):
    return [m for m in msgs if key in m]


def test_hook_needs_number_and_question():
    bad = phong_cach.kiem(_long(head="Chào các bạn hôm nay mình nói chuyện chip. "))
    assert len(_w(bad, "90 từ đầu")) == 2
    good = phong_cach.kiem(_long(head=OK_HEAD))
    assert _w(good, "90 từ đầu") == []


def test_closing_needs_question():
    assert len(_w(phong_cach.kiem(_long(head=OK_HEAD, tail="Hẹn gặp lại.")), "60 từ cuối")) == 1
    assert _w(phong_cach.kiem(_long(head=OK_HEAD, tail="Bạn đoán năm nào?")), "60 từ cuối") == []


def test_length_window():
    assert len(_w(phong_cach.kiem(_long(head=OK_HEAD, n=900)), "lời đọc")) == 1
    assert len(_w(phong_cach.kiem(_long(head=OK_HEAD, n=3200)), "lời đọc")) == 1
    assert _w(phong_cach.kiem(_long(head=OK_HEAD, n=2300)), "lời đọc") == []


def test_no_spoken_paragraphs_is_silent():
    assert phong_cach.kiem("Chỉ có ghi chú, không có lời đọc.") == []


# ---- Máy kiểm "mùi máy": cảnh báo, không chặn ----
def _mui(spoken: str):
    return phong_cach.mui_may(_script(spoken))


def test_triad_structure_warns_when_repeated():
    one = "Một, a b c. Hai, d e f. Ba, g h i. Câu khác nữa."
    assert _w(_mui(one), "bộ ba") == []
    many = one + " Một, a. Hai, b. Ba, c. " + one
    assert len(_w(_mui(many), "bộ ba")) == 1


CAM = [("Đây là một bước đột phá của ngành.", "từ cấm"),
       ("Giải pháp hoàn hảo cho mọi nhà.", "từ cấm"),
       ("Không chỉ rẻ hơn mà còn nhanh hơn.", "từ cấm"),
       ("Chiếc chìa khóa vàng của ngành.", "từ cấm")]


@pytest.mark.parametrize("spoken,key", CAM)
def test_tu_cam_flags_banned_phrase_as_error(spoken, key):
    out = phong_cach.tu_cam(_script(spoken))
    assert len(_w(out, key)) == 1 and out[0].startswith("Lỗi:")


def test_translationese_phrase_is_named():
    out = _w(phong_cach.tu_cam(_script("Hãy nhìn đúng những gì trang giá nói. Giá là chín trăm.")), "dịch thô")
    assert len(out) == 1 and "hãy nhìn đúng" in out[0].lower()
    assert _w(phong_cach.tu_cam(_script("Mở bảng giá ra xem họ ghi gì.")), "dịch thô") == []


def test_tu_cam_opening_only_in_first_40_words():
    assert _w(phong_cach.tu_cam(_script("Bạn đã bao giờ tự hỏi vì sao chip đắt? Giá là chín trăm.")), "mở bài")
    late = _filler(60) + " Bạn đã bao giờ tự hỏi vì sao chip đắt?"
    assert _w(phong_cach.tu_cam(_script(late)), "mở bài") == []


def test_tu_cam_closing_only_in_last_60_words():
    # "tóm lại" đã bỏ khỏi danh sách cấm theo template user (11/11/2026); "hãy nhớ rằng" vẫn bị cấm
    assert _w(phong_cach.tu_cam(_script(_filler(100) + " Hãy nhớ rằng chip đắt.")), "kết bài")
    assert _w(phong_cach.tu_cam(_script("Hãy nhớ rằng chip đắt. " + _filler(100))), "kết bài") == []
    assert _w(phong_cach.tu_cam(_script(_filler(100) + " Tóm lại, chip đắt.")), "kết bài") == []


def test_tu_cam_ignores_quoted_source_text():
    assert phong_cach.tu_cam(_script('Bài báo viết “một bước ngoặt của ngành” rồi dừng.')) == []
    assert phong_cach.tu_cam(_script('Bài báo viết "một bước ngoặt của ngành" rồi dừng.')) == []
    assert len(phong_cach.tu_cam(_script("Đây là bước ngoặt của ngành."))) == 1


def test_tu_cam_matches_decomposed_unicode_and_uppercase():
    assert len(phong_cach.tu_cam(_script(unicodedata.normalize("NFD", "ĐỘT PHÁ là từ bị cấm.")))) == 1


def test_tu_cam_silent_without_spoken_paragraphs():
    assert phong_cach.tu_cam("Chỉ có ghi chú, không có lời đọc.") == []


def test_hedging_cap():
    hedge = "Mình nghĩ vậy. Bạn tự xem nhé. Tùy bạn thôi. Mình cho rằng thế. "
    assert len(_w(_mui(hedge), "rào đón")) == 1
    assert _w(_mui("Mình nghĩ vậy. Bạn tự xem nhé."), "rào đón") == []


def test_qua_nhieu_so_mot_doan_va_so_le():
    day = "Phí là 28,76 phần trăm. Tổng thu 40,6 phần trăm. Tài xế còn 52,7 phần trăm. Khoản thưởng 860 tỷ đồng, hỗ trợ xăng 52 tỷ đồng."
    assert len(_w(_mui(day), "con số")) == 1 and len(_w(_mui(day), "số lẻ")) == 1
    gon = "Khách trả một khoản, Grab giữ gần 40 phần trăm."
    assert _w(_mui(gon), "con số") == [] and _w(_mui(gon), "số lẻ") == []


def test_ending_must_not_recap_with_triad():
    body = " ".join(["Câu thân bài khá dài để đẩy phần kết ra xa phần đầu của bài nói này."] * 20)
    recap = body + " Mình tóm lại. Một, a b. Hai, c d. Ba, e f."
    assert len(_w(_mui(recap), "kết")) == 1
    verdict = body + " Mình sẽ đổi ý nếu hãng bỏ quảng cáo. Bạn đoán bao nhiêu?"
    assert _w(_mui(verdict), "kết") == []


def test_change_of_mind_is_no_longer_required():
    assert _w(_mui("Phán quyết là ở bản miễn phí."), "đổi ý") == []


def _sents(lengths):
    return " ".join(" ".join(["từ"] * (n - 1)) + " xong." for n in lengths)


def test_nhip_flags_uniform_sentence_lengths():
    assert len(_w(phong_cach.nhip(_script(_sents([12] * 30))), "độ lệch")) == 1
    assert _w(phong_cach.nhip(_script(_sents([3, 14, 9, 22, 5, 17, 11, 30, 4, 13] * 3))), "độ lệch") == []


def test_nhip_flags_run_longer_than_four_similar_sentences():
    base = [3, 20, 9, 27, 5, 16, 11, 24, 4, 14] * 2
    assert len(_w(phong_cach.nhip(_script(_sents(base + [10, 10, 11, 10, 9] + base))), "câu liền")) == 1
    assert _w(phong_cach.nhip(_script(_sents(base + [10, 10, 11, 10] + base))), "câu liền") == []


def test_nhip_flags_more_than_eight_long_sentences():
    assert len(_w(phong_cach.nhip(_script(_sents([30] * 9 + [5] * 12))), "dài hơn 28")) == 1
    assert _w(phong_cach.nhip(_script(_sents([30] * 8 + [5] * 12))), "dài hơn 28") == []


def test_nhip_counts_emotive_adjectives_and_fillers():
    assert len(_w(phong_cach.nhip(_script("Giá rất cao. " * 6)), "cảm thán")) == 1
    assert _w(phong_cach.nhip(_script("Giá rất cao. " * 5)), "cảm thán") == []
    assert len(_w(phong_cach.nhip(_script("Kiểu như vậy đó. " * 16)), "từ đệm")) == 1
    assert _w(phong_cach.nhip(_script("Kiểu như vậy đó. " * 15)), "từ đệm") == []


def test_nhip_flags_invented_personal_experience():
    assert len(_w(phong_cach.nhip(_script("Hồi mình nợ thẻ năm chục triệu. Giá là chín trăm.")), "trải nghiệm cá nhân")) == 1
    assert _w(phong_cach.nhip(_script("Mình đọc xong tài liệu sáng nay. Giá là chín trăm.")), "trải nghiệm cá nhân") == []


def test_nhip_skips_statistics_on_short_excerpts():
    out = phong_cach.nhip(_script(_sents([12] * 10)))
    assert _w(out, "độ lệch") == [] and _w(out, "câu liền") == []


def test_kiem_includes_mui_may_and_is_silent_without_spoken():
    assert phong_cach.mui_may("Chỉ ghi chú.") == []
    assert any("bộ ba" in m for m in phong_cach.kiem(_long(head=OK_HEAD + "Một, a. Hai, b. Ba, c. Một, a. Hai, b. Ba, c. ")))


def test_kiem_includes_tu_cam_and_nhip():
    out = phong_cach.kiem(_long(head=OK_HEAD + "Đây là bước đột phá. " + "Giá rất cao. " * 6))
    assert _w(out, "từ cấm") and _w(out, "cảm thán")


def test_main_exit_code_follows_errors(tmp_path, capsys):
    (tmp_path / "kich-ban.md").write_text(_long(head=OK_HEAD + "Đây là bước đột phá. "), encoding="utf-8")
    assert phong_cach.main(str(tmp_path)) == 1 and "Lỗi" in capsys.readouterr().out
    (tmp_path / "kich-ban.md").write_text(_long(head=OK_HEAD, tail="Bạn đoán năm nào?"), encoding="utf-8")
    assert phong_cach.main(str(tmp_path)) == 0


BASELINE = [Path(__file__).resolve().parents[2] / "videos" / v for v in
            ("2026-11-15-nvidia-siet-chip/kich-ban-v2.md", "2026-11-11-cam-nhap-may-cu/kich-ban.md")]


@pytest.mark.parametrize("p", BASELINE, ids=lambda p: p.parent.name)
def test_approved_scripts_stay_clean(p):
    if not p.exists():
        pytest.skip("kịch bản đã duyệt không có trong máy này")
    assert phong_cach.kiem(p.read_text(encoding="utf-8")) == []


def test_uoc_tinh_phut_counts_spoken_words_only():
    md = _long(head=OK_HEAD, n=2300)
    assert abs(phong_cach.uoc_tinh_phut(md, 230) - 2300 / 230) < 0.05
    assert phong_cach.uoc_tinh_phut("Chỉ ghi chú.", 230) == 0.0


def test_main_prints_estimate_when_config_has_wpm(tmp_path, capsys, monkeypatch):
    import json
    cfg = tmp_path / "config.json"
    cfg.write_text(json.dumps({"vieneu": {"wpm_du_kien": 230}}), encoding="utf-8")
    monkeypatch.setattr(phong_cach, "CONFIG", cfg)
    (tmp_path / "kich-ban.md").write_text(_long(head=OK_HEAD, tail="Bạn đoán năm nào?"), encoding="utf-8")
    phong_cach.main(str(tmp_path))
    assert "ước tính 10.0 phút ở 230 từ/phút" in capsys.readouterr().out


def _mau(loai: str, n: int) -> str:
    return f"# Tiêu đề\nLoại: {loai}\n\n" + _script(_filler(n))


def test_template_loai_dat_khung_do_dai_rieng():
    assert phong_cach.loai_cua(_mau("gia", 300)) == "gia"
    assert phong_cach.loai_cua(_script(_filler(300))) is None
    assert _w(phong_cach.kiem(_mau("gia", 300)), "khung") == []  # đúng khung 250–400, không đòi hook số/câu hỏi
    assert len(_w(phong_cach.kiem(_mau("gia", 100)), "khung 250–400")) == 1
    assert len(_w(phong_cach.kiem(_mau("shorts", 150)), "khung")) == 0
    assert len(_w(phong_cach.kiem(_script(_filler(300))), "khung 2000")) == 1  # không có Loại: vẫn là video dài


def test_template_loai_la_la_loi():
    assert len(_w(phong_cach.kiem(_mau("khong-co", 300)), "Lỗi: loại")) == 1


def test_template_tom_lai_va_mình_khong_bi_chan():
    spoken = "Anh em ơi, hãng ra máy mới. No cap, pin đỡ hơn. Tóm lại là xịn nhưng không đỉnh. Anh em thấy sao, comment cho mình biết với?"
    bad = phong_cach.kiem(f"# T\nLoại: ra-mat\n\n" + _script(spoken))
    assert _w(bad, "Lỗi") == []
