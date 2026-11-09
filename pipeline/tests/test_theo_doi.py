import csv
from datetime import datetime, timedelta, timezone

import pytest

from tttc import theo_doi

VN = timezone(timedelta(hours=7))
OLD = "ngay,tieu_de,gio_dang,link,view_24h,view_7d,ctr,giu_chan_30s\n09/11/2026,Tiêu đề,09/11/2026 20:45,https://youtu.be/x,,,,\n"


def test_migrate_adds_columns_without_losing_data(tmp_path):
    p = tmp_path / "theo-doi.csv"
    p.write_text(OLD, encoding="utf-8")
    theo_doi.migrate(p)
    rows = list(csv.DictReader(p.open(encoding="utf-8")))
    assert list(rows[0])[:8] == ["ngay", "tieu_de", "gio_dang", "link", "view_24h", "view_7d", "ctr", "giu_chan_30s"]
    assert list(rows[0])[8:] == theo_doi.EXTRA and rows[0]["tieu_de"] == "Tiêu đề" and rows[0]["chenh_gio"] == ""


def test_migrate_is_idempotent_and_ignores_missing_file(tmp_path):
    p = tmp_path / "theo-doi.csv"
    p.write_text(OLD, encoding="utf-8")
    theo_doi.migrate(p)
    first = p.read_text(encoding="utf-8")
    theo_doi.migrate(p)
    assert p.read_text(encoding="utf-8") == first
    theo_doi.migrate(tmp_path / "khong-co.csv")


def test_chenh_gio_negative_when_earlier():
    a = datetime(2026, 11, 10, 15, 30, tzinfo=VN)
    b = datetime(2026, 11, 10, 18, 0, tzinfo=VN)
    assert theo_doi.chenh_gio(a, b) == -2.5


def test_ty_so_trung_vi_uses_last_ten_complete_rows():
    rows = [{"view_24h": "100", "view_ho_24h": "1000"}, {"view_24h": "", "view_ho_24h": "500"},
            {"view_24h": "300", "view_ho_24h": "1000"}, {"view_24h": "200", "view_ho_24h": "0"}]
    assert theo_doi.ty_so_trung_vi(rows) == pytest.approx(0.2) and theo_doi.ty_so_trung_vi([]) is None


def test_ty_so_trung_vi_caps_at_ten_most_recent():
    rows = [{"view_24h": "1", "view_ho_24h": "100"}] * 5 + [{"view_24h": "50", "view_ho_24h": "100"}] * 10
    assert theo_doi.ty_so_trung_vi(rows) == 0.5
