from datetime import datetime, timezone, timedelta
from tttc import bao_cao

VN = timezone(timedelta(hours=7))


def test_tao_bao_cao_separates_long_and_shorts_and_handles_empty_cells(tmp_path):
    rows = [
        {"ngay": "09/11/2026", "tieu_de": "CEO Nvidia xin lỗi", "gio_dang": "09/11/2026 20:45",
         "link": "https://youtu.be/E17SceQLG9I", "view_24h": "3100", "view_7d": "3208",
         "ctr": "6.3%", "giu_chan_30s": "72%", "avd_pct": "35%", "con_50pct": "32%",
         "khuon_thumb": "ban-co-toi", "goc": "tang-2", "chuoi": "nvidia-de-che-ai"},
        {"ngay": "10/11/2026", "tieu_de": "Cấm bán iPhone cũ", "gio_dang": "10/11/2026 18:50",
         "link": "https://youtu.be/w60qG6ipY1s", "view_24h": "", "view_7d": "93",
         "ctr": "1.3%", "giu_chan_30s": "68%", "avd_pct": "42%", "con_50pct": "40%",
         "khuon_thumb": "ho-so", "goc": "tang-1", "chuoi": ""},
        {"ngay": "12/11/2026", "tieu_de": "iPhone 15 Plus cũ #shorts", "gio_dang": "12/11/2026 08:00",
         "link": "https://youtu.be/1g_MjV4nwTY", "view_24h": "940", "view_7d": "",
         "ctr": "", "giu_chan_30s": "", "o_lai_short": "10%", "khuon_short": "cu"},
    ]
    dt_rows = [
        {"kenh": "@MotCongNghe", "video_id": "siGdK7U9ea4", "tieu_de": "Jensen rời ghế CEO Nvidia",
         "gio_dang": "13/11/2026 17:00", "view_moi_nhat": "98633", "nhom_de": "cluster-a", "breakout": "5.6"},
    ]
    now = datetime(2026, 11, 16, 10, 0, tzinfo=VN)
    p = bao_cao.tao_bao_cao(rows, dt_rows, now, out_dir=tmp_path)
    txt = p.read_text(encoding="utf-8")
    assert p.name == "2026-W47.md"
    assert "Video dài" in txt and "Shorts" in txt
    assert "ban-co-toi" in txt and "cluster-a" in txt and "1.3% < 3%" in txt


def test_tao_bao_cao_with_empty_inputs(tmp_path):
    now = datetime(2026, 11, 16, 10, 0, tzinfo=VN)
    p = bao_cao.tao_bao_cao([], [], now, out_dir=tmp_path)
    assert "n = 0" in p.read_text(encoding="utf-8")
