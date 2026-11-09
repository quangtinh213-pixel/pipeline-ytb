import unicodedata

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
    assert _w(phong_cach.tu_cam(_script(_filler(100) + " Tóm lại, chip đắt.")), "kết bài")
    assert _w(phong_cach.tu_cam(_script("Tóm lại, chip đắt. " + _filler(100))), "kết bài") == []


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


def test_short_sentences_needed_for_rhythm():
    flat = " ".join(["Câu này dài mười hai chữ để đủ độ dài chuẩn thôi nhé bạn."] * 30)
    assert len(_w(_mui(flat), "câu ngắn")) == 1
    mixed = flat + " " + " ".join(["Đúng thế.", "Không hẳn.", "Vậy là xong."] * 6)
    assert _w(_mui(mixed), "câu ngắn") == []


def test_ending_must_not_recap_with_triad():
    body = " ".join(["Câu thân bài khá dài để đẩy phần kết ra xa phần đầu của bài nói này."] * 20)
    recap = body + " Mình tóm lại. Một, a b. Hai, c d. Ba, e f."
    assert len(_w(_mui(recap), "kết")) == 1
    verdict = body + " Mình sẽ đổi ý nếu hãng bỏ quảng cáo. Bạn đoán bao nhiêu?"
    assert _w(_mui(verdict), "kết") == []


def test_needs_change_of_mind_condition():
    assert len(_w(_mui("Phán quyết là ở bản miễn phí."), "đổi ý")) == 1
    assert _w(_mui("Mình sẽ đổi ý nếu hãng bỏ giới hạn."), "đổi ý") == []


def test_kiem_includes_mui_may_and_is_silent_without_spoken():
    assert phong_cach.mui_may("Chỉ ghi chú.") == []
    assert any("bộ ba" in m for m in phong_cach.kiem(_long(head=OK_HEAD + "Một, a. Hai, b. Ba, c. Một, a. Hai, b. Ba, c. ")))
