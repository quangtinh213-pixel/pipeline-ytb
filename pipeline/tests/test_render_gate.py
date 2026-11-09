"""Cổng render.sh: chỉ render khi `hyperframes check` thoát 0 và có dòng "Check passed", không có ✗."""
import os
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "render.sh"
FAKE_NPX = """#!/usr/bin/env bash
if [ "$2" = "check" ]; then printf '%b' "$FAKE_CHECK"; exit "$FAKE_RC"; fi
echo render >> "$FAKE_LOG"; exit 0
"""


@pytest.fixture
def run_render(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    npx = bin_dir / "npx"
    npx.write_text(FAKE_NPX, encoding="utf-8")
    npx.chmod(0o755)
    log = tmp_path / "log.txt"
    comp = tmp_path / "comp"
    comp.mkdir()

    def run(check_out: str, rc: int):
        env = dict(os.environ, PATH=f"{bin_dir}:{os.environ['PATH']}", FAKE_CHECK=check_out,
                   FAKE_RC=str(rc), FAKE_LOG=str(log))
        r = subprocess.run(["bash", str(SCRIPT), str(comp), str(tmp_path / "out" / "v.mp4")],
                           env=env, capture_output=True, text=True)
        rendered = log.exists() and "render" in log.read_text(encoding="utf-8")
        return r.returncode, rendered
    return run


def test_passes_when_check_passed(run_render):
    code, rendered = run_render("◇  Check passed\\n", 0)
    assert code == 0 and rendered


def test_warnings_still_allowed(run_render):
    code, rendered = run_render("  ⚠ line_unread: ...\\n0 error(s), 11 warning(s)\\n◇  Check passed\\n", 0)
    assert code == 0 and rendered


def test_stops_on_error_marker(run_render):
    code, rendered = run_render("  ✗ missing asset\\n◇  Check passed\\n", 0)
    assert code != 0 and not rendered


def test_stops_when_check_crashes_silently(run_render):
    code, rendered = run_render("Error: spawn hyperframes ENOENT\\n", 1)
    assert code != 0 and not rendered


def test_stops_on_nonzero_exit_even_with_pass_line(run_render):
    code, rendered = run_render("◇  Check passed\\n", 2)
    assert code != 0 and not rendered
