import json
from datetime import datetime, timedelta, timezone

import pytest
from tttc import trang_thai as tt


def test_new_video_starts_at_chu_de(tmp_path):
    assert tt.next_step(tmp_path) == "chu-de"


def test_next_step_skips_done(tmp_path):
    tt.set_step(tmp_path, "chu-de", "xong")
    tt.set_step(tmp_path, "nguon", "xong")
    assert tt.next_step(tmp_path) == "kich-ban"


def test_next_step_returns_failed_step(tmp_path):
    tt.set_step(tmp_path, "chu-de", "xong")
    tt.set_step(tmp_path, "nguon", "loi", "trang bi chan")
    assert tt.next_step(tmp_path) == "nguon"
    assert tt.load(tmp_path)["steps"]["nguon"]["note"] == "trang bi chan"


def test_next_step_none_while_waiting_review(tmp_path):
    for s in ["chu-de", "nguon", "kich-ban", "phan-bien-giong", "kiem"]:
        tt.set_step(tmp_path, s, "xong")
    tt.set_step(tmp_path, "duyet-1", "cho-duyet")
    assert tt.next_step(tmp_path) is None


def test_next_step_passes_approved_review(tmp_path):
    for s in ["chu-de", "nguon", "kich-ban", "phan-bien-giong", "kiem"]:
        tt.set_step(tmp_path, s, "xong")
    tt.set_step(tmp_path, "duyet-1", "da-duyet")
    assert tt.next_step(tmp_path) == "giong"


def test_is_approved_requires_both(tmp_path):
    tt.set_step(tmp_path, "duyet-1", "da-duyet")
    assert not tt.is_approved(tmp_path)
    tt.set_step(tmp_path, "duyet-2", "da-duyet")
    assert tt.is_approved(tmp_path)


def test_set_step_rejects_unknown_status(tmp_path):
    with pytest.raises(ValueError):
        tt.set_step(tmp_path, "chu-de", "done")


def test_set_step_rejects_unknown_step(tmp_path):
    with pytest.raises(ValueError):
        tt.set_step(tmp_path, "abc", "xong")


def test_set_field_persists(tmp_path):
    tt.set_field(tmp_path, "chon", 2)
    assert json.loads((tmp_path / "trang-thai.json").read_text())["chon"] == 2
    assert tt.load(tmp_path)["chon"] == 2


def test_phan_bien_giong_sits_between_kich_ban_and_kiem():
    assert tt.STEPS.index("phan-bien-giong") == tt.STEPS.index("kich-ban") + 1 == tt.STEPS.index("kiem") - 1


def test_new_video_must_review_voice_before_kiem(tmp_path):
    for s in ["chu-de", "nguon", "kich-ban"]:
        tt.set_step(tmp_path, s, "xong")
    assert tt.next_step(tmp_path) == "phan-bien-giong"


def _old(tmp_path, duyet_1=None):
    steps = {s: {"status": "xong", "note": ""} for s in ["chu-de", "nguon", "kich-ban", "kiem"]}
    if duyet_1:
        steps["duyet-1"] = {"status": duyet_1, "note": ""}
    (tmp_path / "trang-thai.json").write_text(json.dumps({"steps": steps}), encoding="utf-8")


def test_old_video_past_review_1_is_not_pushed_back(tmp_path):
    _old(tmp_path, "da-duyet")
    assert tt.load(tmp_path)["steps"]["phan-bien-giong"]["status"] == "xong"
    assert tt.next_step(tmp_path) == "giong"


def test_old_video_before_review_1_still_needs_voice_review(tmp_path):
    _old(tmp_path)
    assert tt.next_step(tmp_path) == "phan-bien-giong"


def test_dao_dien_sits_between_giong_and_canh():
    assert tt.STEPS.index("dao-dien") == tt.STEPS.index("giong") + 1 == tt.STEPS.index("canh") - 1


def _dung(tmp_path, **st):
    """Tệp cũ (trước bước dao-dien): các bước đến giong xong, thêm các bước ở st."""
    steps = {s: {"status": "xong", "note": ""} for s in ["chu-de", "nguon", "kich-ban", "phan-bien-giong", "kiem", "giong"]}
    steps["duyet-1"] = {"status": "da-duyet", "note": ""}
    steps.update({k: {"status": v, "note": ""} for k, v in st.items()})
    (tmp_path / "trang-thai.json").write_text(json.dumps({"steps": steps}), encoding="utf-8")


def test_new_video_after_giong_needs_dao_dien(tmp_path):
    for s in ["chu-de", "nguon", "kich-ban", "phan-bien-giong", "kiem"]:
        tt.set_step(tmp_path, s, "xong")
    tt.set_step(tmp_path, "duyet-1", "da-duyet")
    tt.set_step(tmp_path, "giong", "xong")
    assert tt.next_step(tmp_path) == "dao-dien"


def test_old_video_with_canh_done_is_not_pushed_back(tmp_path):
    _dung(tmp_path, canh="xong")
    assert tt.load(tmp_path)["steps"]["dao-dien"]["status"] == "xong"
    assert tt.next_step(tmp_path) == "hinh"


def test_old_video_with_canh_running_is_not_pushed_back(tmp_path):
    _dung(tmp_path, canh="loi")
    assert tt.next_step(tmp_path) == "canh"


def test_old_video_giong_done_canh_not_run_needs_dao_dien(tmp_path):
    _dung(tmp_path)
    assert tt.next_step(tmp_path) == "dao-dien"


VN = timezone(timedelta(hours=7))


def at(h, m=0):
    return datetime(2026, 11, 10, h, m, tzinfo=VN)


def test_set_step_records_start_and_end(tmp_path):
    tt.set_step(tmp_path, "giong", "dang-chay", now=at(11, 0))
    tt.set_step(tmp_path, "giong", "xong", "ok", now=at(11, 12))
    s = tt.load(tmp_path)["steps"]["giong"]
    assert (s["status"], s["note"]) == ("xong", "ok")
    assert s["bat_dau"] == at(11, 0).isoformat() and s["ket_thuc"] == at(11, 12).isoformat()


def test_gio_reports_seconds_per_step_and_total(tmp_path):
    tt.set_step(tmp_path, "chu-de", "dang-chay", now=at(6, 30))
    tt.set_step(tmp_path, "chu-de", "xong", now=at(6, 45))
    tt.set_step(tmp_path, "duyet-2", "dang-chay", now=at(14, 0))
    tt.set_step(tmp_path, "duyet-2", "da-duyet", now=at(14, 20))
    g = tt.gio(tmp_path)
    assert g["buoc"]["chu-de"] == 900 and g["buoc"]["duyet-2"] == 1200 and g["tong"] == 28200


def test_gio_total_is_none_without_both_ends(tmp_path):
    tt.set_step(tmp_path, "chu-de", "xong", now=at(6, 45))
    assert tt.gio(tmp_path)["tong"] is None


def test_running_step_is_still_pending(tmp_path):
    for s in ["chu-de", "nguon", "kich-ban", "phan-bien-giong", "kiem"]:
        tt.set_step(tmp_path, s, "xong")
    tt.set_step(tmp_path, "duyet-1", "da-duyet")
    tt.set_step(tmp_path, "giong", "dang-chay")
    assert tt.next_step(tmp_path) == "giong"


def test_old_video_without_timestamps_still_loads(tmp_path):
    (tmp_path / "trang-thai.json").write_text(json.dumps({"steps": {"chu-de": {"status": "xong", "note": ""}}}), encoding="utf-8")
    assert tt.gio(tmp_path) == {"buoc": {}, "tong": None}


def test_shorts_come_after_publishing():
    assert tt.STEPS.index("shorts") > tt.STEPS.index("dang") > tt.STEPS.index("duyet-2")


def test_next_step_after_review_2_is_dang_not_shorts(tmp_path):
    for s in tt.STEPS[: tt.STEPS.index("duyet-2")]:
        tt.set_step(tmp_path, s, "xong")
    tt.set_step(tmp_path, "duyet-1", "da-duyet")
    tt.set_step(tmp_path, "duyet-2", "da-duyet")
    assert tt.next_step(tmp_path) == "dang"


def test_kho_lists_approved_unpublished_evergreen_only(tmp_path):
    def mk(name, loai, duyet2, dang):
        d = tmp_path / name
        d.mkdir()
        tt.set_field(d, "loai", loai)
        tt.set_step(d, "duyet-2", duyet2)
        tt.set_step(d, "dang", dang)
    mk("a-ok", "evergreen", "da-duyet", "chua-chay")
    mk("b-da-dang", "evergreen", "da-duyet", "xong")
    mk("c-nong", "nong", "da-duyet", "chua-chay")
    mk("d-chua-duyet", "evergreen", "cho-duyet", "chua-chay")
    (tmp_path / "e-khong-so").mkdir()
    (tmp_path / "f-tep.txt").write_text("x", encoding="utf-8")
    assert [p.name for p in tt.kho(tmp_path)] == ["a-ok"]
