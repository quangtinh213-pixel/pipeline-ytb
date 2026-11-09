import shutil

import pytest

from tttc import giong_tam

pytestmark = pytest.mark.skipif(shutil.which("say") is None, reason="cần lệnh say của macOS")


def test_giong_tam_timing_covers_duration(tmp_path):
    text = "Xin chào các bạn. Hôm nay mình so ba gói trí tuệ nhân tạo."
    t = giong_tam.giong_tam(text, tmp_path)
    assert (tmp_path / "giong.mp3").stat().st_size > 0
    assert len(t["words"]) == len(text.split()) and t["paragraphs"] == []
    assert 0 <= t["words"][0]["start"] < t["words"][-1]["end"] <= t["duration"] + 1e-6
