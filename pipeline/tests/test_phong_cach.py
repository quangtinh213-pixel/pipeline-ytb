from tttc import phong_cach

OK_HEAD = "Viettel ra chip 28 nanomet, nhưng liệu thế đã đủ? [#v1] "


def _script(spoken: str) -> str:
    return f"#### Beat 1: Mở đầu\n[TRÊN MÀN HÌNH]: chữ lớn\n**Lời đọc:**\n{spoken}\n"


def _filler(n: int) -> str:
    return " ".join(["từ"] * (n - 1) + ["xong."])


def _long(head="", tail="", n=1700):
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
    assert len(_w(phong_cach.kiem(_long(head=OK_HEAD, n=2200)), "lời đọc")) == 1
    assert _w(phong_cach.kiem(_long(head=OK_HEAD, n=1700)), "lời đọc") == []


def test_no_spoken_paragraphs_is_silent():
    assert phong_cach.kiem("Chỉ có ghi chú, không có lời đọc.") == []
