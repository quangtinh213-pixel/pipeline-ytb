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


def test_kiem_tra_video_auto_pivots_when_ctr_critical(tmp_path):
    pkg = {
        "phuong_an": [
            {"tieu_de": "Tiêu đề 1", "file_thumb": "thumb1.png"},
            {"tieu_de": "Tiêu đề 2", "file_thumb": "thumb2.png"},
        ]
    }
    (tmp_path / "dong-goi.json").write_text(json.dumps(pkg), encoding="utf-8")
    (tmp_path / "thumb2.png").write_bytes(b"img")
    (tmp_path / "trang-thai.json").write_text(json.dumps({"video_id": "v1", "chon": 1, "steps": {}}), encoding="utf-8")
    tracker = tmp_path / "theo-doi.csv"
    tracker.write_text("ngay,tieu_de,gio_dang,link\n14/11/2026,Tiêu đề 1,15:30,https://youtu.be/v1\n", encoding="utf-8")

    mock_yt = MagicMock()
    mock_yt.videos.return_value.list.return_value.execute.return_value = {
        "items": [{"snippet": {"title": "Tiêu đề 1", "description": "d"}, "statistics": {"viewCount": "42", "likeCount": "2", "commentCount": "0"}, "status": {"privacyStatus": "public"}}]
    }
    mock_yt.videos.return_value.update.return_value.execute.return_value = {}
    mock_yt.thumbnails.return_value.set.return_value.execute.return_value = {}

    res = giam_sat.kiem_tra_video(tmp_path, ctr_val="2.5%", tu_dong_doi=True, youtube=mock_yt, tracker=tracker)
    assert res["trang_thai_ctr"] == "NGUY_CAP"
    assert res["da_doi"]["phuong_an"] == 2
    assert res["da_doi"]["new_title"] == "Tiêu đề 2"


def test_lay_chi_so_analytics_parses_headers_and_handles_missing():
    assert giam_sat.lay_chi_so_analytics("v1", "2026-11-14") is None
    an = MagicMock()
    an.reports.return_value.query.return_value.execute.return_value = {
        "columnHeaders": [{"name": "views"}, {"name": "videoThumbnailImpressionsClickRate"}],
        "rows": [[150, 5.4]],
    }
    got = giam_sat.lay_chi_so_analytics("v1", "2026-11-14", "2026-11-14", analytics=an)
    assert got == {"views": 150, "videoThumbnailImpressionsClickRate": 5.4}


def test_kiem_tra_video_does_not_cycle_after_all_options_tried(tmp_path):
    pkg = {
        "phuong_an": [
            {"tieu_de": "Tiêu đề 1", "file_thumb": "thumb1.png"},
            {"tieu_de": "Tiêu đề 2", "file_thumb": "thumb2.png"},
        ]
    }
    (tmp_path / "dong-goi.json").write_text(json.dumps(pkg), encoding="utf-8")
    (tmp_path / "thumb1.png").write_bytes(b"img1")
    (tmp_path / "thumb2.png").write_bytes(b"img2")
    (tmp_path / "trang-thai.json").write_text(json.dumps({"video_id": "v1", "chon": 1, "steps": {}}), encoding="utf-8")
    tracker = tmp_path / "theo-doi.csv"
    tracker.write_text("ngay,tieu_de,gio_dang,link\n14/11/2026,Tiêu đề 1,15:30,https://youtu.be/v1\n", encoding="utf-8")

    mock_yt = MagicMock()
    mock_yt.videos.return_value.list.return_value.execute.return_value = {
        "items": [{"snippet": {"title": "Tiêu đề 1", "description": "d"}, "statistics": {"viewCount": "42", "likeCount": "2", "commentCount": "0"}, "status": {"privacyStatus": "public"}}]
    }
    mock_yt.videos.return_value.update.return_value.execute.return_value = {}
    mock_yt.thumbnails.return_value.set.return_value.execute.return_value = {}

    res1 = giam_sat.kiem_tra_video(tmp_path, ctr_val="2.5%", tu_dong_doi=True, youtube=mock_yt, tracker=tracker)
    assert res1["da_doi"]["phuong_an"] == 2
    res2 = giam_sat.kiem_tra_video(tmp_path, ctr_val="1.5%", tu_dong_doi=True, youtube=mock_yt, tracker=tracker)
    assert res2["da_doi"] is None
    assert json.loads((tmp_path / "trang-thai.json").read_text(encoding="utf-8"))["chon"] == 2


def _an_giu_chan(rows):
    an = MagicMock()
    an.reports.return_value.query.return_value.execute.return_value = {"rows": rows}
    return an


def test_giu_chan_tai_noi_suy_giua_hai_diem_va_bo_qua_video_ngan():
    # video 100 s: điểm 0.25 = giây 25, 0.35 = giây 35 → giây 30 nằm giữa
    an = _an_giu_chan([[0.25, 0.8], [0.35, 0.6], [1.0, 0.1]])
    assert abs(giam_sat.giu_chan_tai(an, "v1", 30, 100, "2026-11-09", "2026-11-15") - 0.7) < 1e-9
    q = an.reports.return_value.query.call_args.kwargs
    assert q["dimensions"] == "elapsedVideoTimeRatio" and q["filters"] == "video==v1" and q["endDate"] == "2026-11-15"
    assert giam_sat.giu_chan_tai(an, "v1", 30, 25, "a", "b") is None  # video ngắn hơn 30 s
    assert giam_sat.giu_chan_tai(_an_giu_chan([]), "v1", 30, 100, "a", "b") is None
    assert giam_sat.giu_chan_tai(None, "v1", 30, 100, "a", "b") is None


def test_lay_chi_so_analytics_khong_xin_ctr_vi_api_tu_choi():
    an = _an_giu_chan([])
    giam_sat.lay_chi_so_analytics("v1", "2026-11-14", analytics=an)
    assert "ClickRate" not in an.reports.return_value.query.call_args.kwargs["metrics"]
