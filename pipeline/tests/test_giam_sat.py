import json
from pathlib import Path
from unittest.mock import MagicMock
from tttc import giam_sat


def test_danh_gia_ctr():
    assert giam_sat.danh_gia_ctr("6.3%") == "AN_TOAN"
    assert giam_sat.danh_gia_ctr("4.5%") == "CANH_BAO"
    assert giam_sat.danh_gia_ctr("1.3%") == "NGUY_CAP"
    assert giam_sat.danh_gia_ctr(None) == "CHUA_CO_SO_LIEU"
    assert giam_sat.danh_gia_ctr("-") == "CHUA_CO_SO_LIEU"


def test_lay_cac_phuong_an(tmp_path):
    pkg = {
        "phuong_an": [
            {"tieu_de": "Phương án 1", "file_thumb": "thumb1.png"},
            {"tieu_de": "Phương án 2", "file_thumb": "thumb2.png"}
        ]
    }
    (tmp_path / "dong-goi.json").write_text(json.dumps(pkg), encoding="utf-8")
    opts = giam_sat.lay_cac_phuong_an(tmp_path)
    assert len(opts) == 2
    assert opts[0]["tieu_de"] == "Phương án 1"


def test_doi_bao_bi_calls_youtube_and_updates_state(tmp_path):
    # Setup test directory
    pkg = {
        "phuong_an": [
            {"tieu_de": "Tiêu đề cũ", "file_thumb": "thumb1.png"},
            {"tieu_de": "Tiêu đề mới cứu nguy", "file_thumb": "thumb2.png"}
        ]
    }
    (tmp_path / "dong-goi.json").write_text(json.dumps(pkg), encoding="utf-8")
    (tmp_path / "thumb2.png").write_bytes(b"fake image data")
    (tmp_path / "trang-thai.json").write_text(
        json.dumps({"video_id": "test_123", "chon": 1, "steps": {}}), encoding="utf-8"
    )

    tracker = tmp_path / "theo-doi.csv"
    tracker.write_text("ngay,tieu_de,gio_dang,link\n10/11/2026,Tiêu đề cũ,18:50,https://youtu.be/test_123\n", encoding="utf-8")

    # Mock YouTube client
    mock_yt = MagicMock()
    mock_videos = MagicMock()
    mock_thumbnails = MagicMock()
    mock_yt.videos.return_value = mock_videos
    mock_yt.thumbnails.return_value = mock_thumbnails

    mock_videos.list.return_value.execute.return_value = {
        "items": [{"snippet": {"title": "Tiêu đề cũ", "description": "desc"}}]
    }
    mock_videos.update.return_value.execute.return_value = {}
    mock_thumbnails.set.return_value.execute.return_value = {}

    res = giam_sat.doi_bao_bi(tmp_path, phuong_an_so=2, youtube=mock_yt, tracker=tracker)

    assert res["video_id"] == "test_123"
    assert res["old_title"] == "Tiêu đề cũ"
    assert res["new_title"] == "Tiêu đề mới cứu nguy"
    assert res["thumb_updated"] is True

    # Check that state was updated to chon = 2
    new_state = json.loads((tmp_path / "trang-thai.json").read_text(encoding="utf-8"))
    assert new_state["chon"] == 2

    # Check tracker file updated
    content = tracker.read_text(encoding="utf-8")
    assert "Tiêu đề mới cứu nguy" in content
    assert "Tiêu đề cũ" not in content
