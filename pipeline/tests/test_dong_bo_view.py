import importlib.util
from datetime import datetime, timedelta, timezone
from pathlib import Path

VN = timezone(timedelta(hours=7))
SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "dong-bo-view.py"


def _load():
    spec = importlib.util.spec_from_file_location("dong_bo_view", SCRIPT_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_cap_nhat_doi_thu_matches_topic_fills_delay_and_views():
    mod = _load()
    rows = [
        {
            "tieu_de": "Sự thật vụ Microsoft nâng cấp mạng: Tự tay làm sập 18 giờ",
            "gio_dang": "14/11/2026 15:30",
            "trung_de_ho": "",
            "chenh_gio": "",
            "view_ho_24h": "",
        },
        {
            "tieu_de": "Tin ngắn #shorts",
            "gio_dang": "14/11/2026 16:00",
            "trung_de_ho": "",
            "chenh_gio": "",
            "view_ho_24h": "",
        },
    ]
    rss_items = [
        {
            "id": "0wDK-sZVtj0",
            "tieu_de": "Microsoft 365 sập toàn cầu hơn 13 tiếng: vì sao sửa mãi chưa xong",
            "dang_luc": datetime(2026, 11, 13, 18, 0, tzinfo=VN),
            "view": 4200,
        }
    ]
    now = datetime(2026, 11, 14, 19, 0, tzinfo=VN)
    changed = mod.cap_nhat_doi_thu(rows, rss_items, now)
    assert changed == 1
    assert rows[0]["trung_de_ho"] == "0wDK-sZVtj0"
    assert rows[0]["chenh_gio"] == "+21.5"
    assert rows[0]["view_ho_24h"] == "4200"
    assert rows[1]["trung_de_ho"] == ""  # Shorts không đối chiếu với video dài


def test_cap_nhat_doi_thu_ignores_videos_over_24h_apart():
    mod = _load()
    rows = [
        {
            "tieu_de": "Sự thật vụ Microsoft nâng cấp mạng: Tự tay làm sập 18 giờ",
            "gio_dang": "14/11/2026 15:30",
            "trung_de_ho": "",
            "chenh_gio": "",
            "view_ho_24h": "",
        }
    ]
    rss_items = [
        {
            "id": "old_vid",
            "tieu_de": "Microsoft 365 sập toàn cầu hơn 13 tiếng: vì sao sửa mãi chưa xong",
            "dang_luc": datetime(2026, 11, 12, 15, 30, tzinfo=VN),  # lệch 48 giờ
            "view": 4200,
        }
    ]
    now = datetime(2026, 11, 14, 19, 0, tzinfo=VN)
    changed = mod.cap_nhat_doi_thu(rows, rss_items, now)
    assert changed == 0
    assert rows[0]["trung_de_ho"] == ""


def test_giay_doc_thoi_luong_iso():
    mod = _load()
    assert mod._giay("PT8M10S") == 490 and mod._giay("PT45S") == 45 and mod._giay("PT1H2M3S") == 3723
    assert mod._giay("") == 0


def test_cap_nhat_giu_chan_cho_du_ngay_va_khong_ghi_de():
    from unittest.mock import MagicMock
    mod = _load()
    an = MagicMock()
    an.reports.return_value.query.return_value.execute.return_value = {"rows": [[0.25, 0.8], [0.35, 0.6]]}
    rows = [
        {"link": "https://youtu.be/cu", "gio_dang": "01/11/2026 15:30", "giu_chan_30s": ""},   # đủ 9 ngày
        {"link": "https://youtu.be/moi", "gio_dang": "09/11/2026 15:30", "giu_chan_30s": ""},  # mới 5 ngày
        {"link": "https://youtu.be/co", "gio_dang": "01/11/2026 15:30", "giu_chan_30s": "55%"},  # đã có số
    ]
    now = datetime(2026, 11, 14, 9, 0, tzinfo=VN)
    tl = {"cu": 100.0, "moi": 100.0, "co": 100.0}
    assert mod.cap_nhat_giu_chan(rows, tl, an, now) == 1
    assert [r["giu_chan_30s"] for r in rows] == ["70%", "", "55%"]
    q = an.reports.return_value.query.call_args.kwargs
    assert (q["startDate"], q["endDate"]) == ("2026-11-01", "2026-11-07")
    assert mod.cap_nhat_giu_chan(rows, tl, None, now) == 0
