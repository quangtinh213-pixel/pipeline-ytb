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
