from datetime import datetime, timedelta, timezone

from tttc import chay_kho
from tttc import trang_thai as tt

VN = timezone(timedelta(hours=7))


def _unmet(d, n):
    return [m for m in chay_kho.kiem(d) if m.startswith(f"Chưa đạt {n}:")]


def test_criterion_1_duyet_2_after_15h_is_unmet(tmp_path):
    tt.set_step(tmp_path, "duyet-2", "da-duyet", now=datetime(2026, 11, 10, 15, 20, tzinfo=VN))
    assert _unmet(tmp_path, 1)
    tt.set_step(tmp_path, "duyet-2", "da-duyet", now=datetime(2026, 11, 10, 14, 50, tzinfo=VN))
    assert not _unmet(tmp_path, 1)


def test_criterion_1_unmet_while_review_2_not_done(tmp_path):
    assert _unmet(tmp_path, 1)


def test_criterion_2_manual_interventions(tmp_path):
    assert not _unmet(tmp_path, 2)
    tt.set_field(tmp_path, "can_thiep_tay", ["sửa canh c012"])
    assert _unmet(tmp_path, 2) and "1" in _unmet(tmp_path, 2)[0]


def test_criterion_5_every_step_needs_an_end_time(tmp_path):
    for s in tt.STEPS[: tt.STEPS.index("duyet-2") + 1]:
        tt.set_step(tmp_path, s, "xong", now=datetime(2026, 11, 10, 10, 0, tzinfo=VN))
    assert not _unmet(tmp_path, 5)
    steps = tt.load(tmp_path)
    steps["steps"]["giong"].pop("ket_thuc")
    (tmp_path / "trang-thai.json").write_text(__import__("json").dumps(steps), encoding="utf-8")
    assert _unmet(tmp_path, 5) and "giong" in _unmet(tmp_path, 5)[0]


def test_criterion_7_needs_both_review_rounds(tmp_path):
    (tmp_path / "phan-bien-giong-1.md").write_text("x", encoding="utf-8")
    assert any("phan-bien-giong-2.md" in m for m in _unmet(tmp_path, 7))


def test_criterion_7_flags_style_errors_in_script(tmp_path):
    for n in (1, 2):
        (tmp_path / f"phan-bien-giong-{n}.md").write_text("x", encoding="utf-8")
    (tmp_path / "kich-ban.md").write_text("#### Beat 1\n**Lời đọc:**\nĐây là bước đột phá.\n", encoding="utf-8")
    assert any("Lỗi" in m for m in _unmet(tmp_path, 7))
    (tmp_path / "kich-ban.md").write_text("#### Beat 1\n**Lời đọc:**\nGiá là chín trăm.\n", encoding="utf-8")
    assert not _unmet(tmp_path, 7)


def test_empty_video_reports_unmet_criteria(tmp_path):
    got = {m[:10] for m in chay_kho.kiem(tmp_path)}
    assert {"Chưa đạt 1", "Chưa đạt 3", "Chưa đạt 4", "Chưa đạt 5", "Chưa đạt 7"} <= got
    assert "Chưa đạt 2" not in got  # tiêu chí 2 chỉ báo khi can_thiep_tay không rỗng


def test_main_exit_code_and_summary(tmp_path, capsys):
    assert chay_kho.main(str(tmp_path)) == 1
    out = capsys.readouterr().out
    assert "Chưa đạt 1" in out and "tiêu chí chưa đạt" in out
