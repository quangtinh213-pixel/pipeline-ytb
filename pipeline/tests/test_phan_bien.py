import json
import subprocess

import pytest

from tttc import phan_bien

OK = {"status": "SUCCESS", "response": "1. Câu sáo rỗng ...", "conversation_id": "abc-123"}


def _run(payload=OK, code=0, calls=None):
    def run(cmd, **kw):
        if calls is not None:
            calls.append((cmd, kw))
        return subprocess.CompletedProcess(cmd, code, stdout=json.dumps(payload), stderr="")
    return run


def test_goi_builds_safe_command():
    calls = []
    phan_bien.goi("P", run=_run(calls=calls))
    cmd = calls[0][0]
    assert cmd[:3] == ["agy", "-p", "P"] and cmd[cmd.index("--output-format") + 1] == "json"
    assert cmd[cmd.index("--print-timeout") + 1] == "600s"
    assert "--dangerously-skip-permissions" not in cmd and "--json-schema" not in cmd


def test_goi_resumes_conversation():
    calls = []
    phan_bien.goi("P", conversation_id="abc-123", run=_run(calls=calls))
    cmd = calls[0][0]
    assert cmd[cmd.index("--conversation") + 1] == "abc-123"


def test_goi_returns_status_response_and_conversation():
    assert phan_bien.goi("P", run=_run()) == OK


def test_goi_saves_raw_stdout(tmp_path):
    phan_bien.goi("P", luu=tmp_path / "raw.json", run=_run())
    assert json.loads((tmp_path / "raw.json").read_text(encoding="utf-8"))["conversation_id"] == "abc-123"


@pytest.mark.parametrize("run", [
    _run({**OK, "status": "ERROR"}), _run(code=1),
    lambda cmd, **kw: subprocess.CompletedProcess(cmd, 0, stdout="không phải json", stderr=""),
    lambda cmd, **kw: (_ for _ in ()).throw(FileNotFoundError()),
    lambda cmd, **kw: (_ for _ in ()).throw(subprocess.TimeoutExpired(cmd, 1)),
], ids=["status-khac-success", "ma-thoat-1", "khong-phai-json", "khong-co-agy", "qua-thoi-gian"])
def test_goi_raises_agyloi_on_every_failure(run):
    with pytest.raises(phan_bien.AgyLoi):
        phan_bien.goi("P", run=run)


def test_loi_doc_drops_screen_lines_and_tags():
    md = "#### Beat 1\n[TRÊN MÀN HÌNH]: chữ lớn\n**Lời đọc:**\nGiá là chín trăm. [#p1]\nXong.\n"
    assert phan_bien.loi_doc(md) == "Giá là chín trăm.\n\nXong."


def test_prompt_round_1_and_2():
    p1 = phan_bien.dung_prompt(1, "LỜI ĐỌC", "TU-CAM", "PHÂN TÍCH")
    assert all(x in p1 for x in ("LỜI ĐỌC", "TU-CAM", "PHÂN TÍCH", "không dùng tool", "tối đa 12"))
    p2 = phan_bien.dung_prompt(2, "LỜI ĐỌC", "TU-CAM", "PHÂN TÍCH", triage_md="BẢNG TRIAGE")
    assert "BẢNG TRIAGE" in p2 and "chưa xử lý" in p2 and "BẢNG TRIAGE" not in p1


def _video(tmp_path):
    (tmp_path / "kich-ban.md").write_text("#### Beat 1\n**Lời đọc:**\nGiá là chín trăm.\n", encoding="utf-8")
    return tmp_path


def test_main_round_1_writes_md_raw_and_prints_conversation(tmp_path, capsys):
    d = _video(tmp_path)
    assert phan_bien.main(["vong", "1", str(d)], run=_run()) == 0
    assert "conversation_id: abc-123" in capsys.readouterr().out
    md = (d / "phan-bien-giong-1.md").read_text(encoding="utf-8")
    assert OK["response"] in md and "## Bảng triage" in md
    assert (d / "phan-bien-giong-1.raw.json").exists()


def test_main_round_2_needs_conversation_and_triage(tmp_path):
    assert phan_bien.main(["vong", "2", str(_video(tmp_path))], run=_run()) == 2


def test_main_round_2_sends_triage_and_resumes_conversation(tmp_path):
    d, calls = _video(tmp_path), []
    (d / "phan-bien-giong-1.md").write_text("BẢNG TRIAGE VÒNG 1", encoding="utf-8")
    assert phan_bien.main(["vong", "2", str(d), "--conversation", "abc-123", "--triage",
                           str(d / "phan-bien-giong-1.md")], run=_run(calls=calls)) == 0
    cmd = calls[0][0]
    assert cmd[cmd.index("--conversation") + 1] == "abc-123" and "BẢNG TRIAGE VÒNG 1" in cmd[2]


def test_main_returns_3_when_agy_fails(tmp_path, capsys):
    assert phan_bien.main(["vong", "1", str(_video(tmp_path))], run=_run({**OK, "status": "ERROR"})) == 3
    assert "agy lỗi" in capsys.readouterr().out
