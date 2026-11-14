from datetime import date
from unittest.mock import MagicMock

from tttc import reach


def test_doc_csv_doc_cot_theo_ten_bo_dong_cap_kenh_va_cong_don():
    text = (
        "video_thumbnail_impressions_ctr,date,video_id,channel_id,video_thumbnail_impressions\n"
        "0.05,20261109,v1,UC,1000\n"
        "0.10,20261109,v1,UC,500\n"
        "0.02,20261109,,UC,9999\n"
    )
    assert reach.doc_csv(text) == {"v1": (1500.0, 100.0)}
    assert reach.doc_csv("date,channel_id,video_id,video_thumbnail_impressions,video_thumbnail_impressions_ctr\n") == {}


def test_ctr_gop_theo_tong_click_chia_tong_hien_thi():
    ngay = [{"v1": (1000.0, 50.0)}, {"v1": (3000.0, 30.0)}, {}]
    assert reach.ctr(ngay, "v1") == 80 / 4000
    assert reach.ctr(ngay, "khac") is None


def test_bao_cao_theo_ngay_lay_ban_moi_nhat_va_ngay_theo_gio_pst():
    rp = MagicMock()
    rp.jobs.return_value.reports.return_value.list.return_value.execute.return_value = {"reports": [
        {"startTime": "2026-11-09T08:00:00Z", "createTime": "2026-11-11T00:00:00Z", "downloadUrl": "cu"},
        {"startTime": "2026-11-09T08:00:00Z", "createTime": "2026-11-15T00:00:00Z", "downloadUrl": "moi"},
        {"startTime": "2026-11-10T08:00:00Z", "createTime": "2026-11-12T00:00:00Z", "downloadUrl": "n10"},
    ]}
    rp.jobs.return_value.reports.return_value.list_next.return_value = None
    assert reach.bao_cao_theo_ngay(rp, "j1") == {date(2026, 11, 9): "moi", date(2026, 11, 10): "n10"}


def test_job_id_dung_lai_job_co_san_hoac_tao_moi():
    rp = MagicMock()
    rp.jobs.return_value.list.return_value.execute.return_value = {"jobs": [{"id": "j1", "reportTypeId": reach.LOAI}]}
    assert reach.job_id(rp) == "j1"
    rp.jobs.return_value.create.assert_not_called()
    rp.jobs.return_value.list.return_value.execute.return_value = {}
    assert reach.job_id(rp, tao=False) is None
    rp.jobs.return_value.create.return_value.execute.return_value = {"id": "j2"}
    assert reach.job_id(rp) == "j2"
    assert rp.jobs.return_value.create.call_args.kwargs["body"]["reportTypeId"] == "channel_reach_basic_a1"
