"""CTR thumbnail từ YouTube Reporting API (báo cáo `channel_reach_basic_a1`).

Analytics API v2 không trả CTR thumbnail (400 "query is not supported"), chỉ Reporting API có: tạo một job,
YouTube sinh mỗi ngày một CSV (ngày theo giờ Thái Bình Dương UTC-8) và tự tạo lại 30 ngày trước lúc tạo job.
Báo cáo đầu tiên có sau khoảng 48 giờ; báo cáo giữ 60 ngày (bản tạo lại giữ 30 ngày).
"""
import csv
import io
from datetime import date, datetime, timedelta, timezone

LOAI = "channel_reach_basic_a1"
PT = timezone(timedelta(hours=-8))  # ngày của báo cáo: 00:00–23:59 PST, không theo giờ mùa hè


def job_id(reporting, tao: bool = True) -> str | None:
    """Id job reach của kênh; chưa có thì tạo (khi `tao`). Gọi lại nhiều lần không tạo trùng."""
    jobs = reporting.jobs().list().execute().get("jobs") or []
    for j in jobs:
        if j.get("reportTypeId") == LOAI:
            return j["id"]
    if not tao:
        return None
    return reporting.jobs().create(body={"reportTypeId": LOAI, "name": "nhip-cong-nghe-reach"}).execute()["id"]


def _ngay(start_time: str) -> date:
    return datetime.fromisoformat(start_time.replace("Z", "+00:00")).astimezone(PT).date()


def bao_cao_theo_ngay(reporting, job: str) -> dict[date, str]:
    """Ngày → downloadUrl. Một ngày có nhiều bản (bản tạo lại) thì lấy bản createTime mới nhất."""
    out: dict[date, tuple[str, str]] = {}
    req = reporting.jobs().reports().list(jobId=job)
    while req is not None:
        resp = req.execute()
        for r in resp.get("reports") or []:
            d = _ngay(r["startTime"])
            if d not in out or r["createTime"] > out[d][0]:
                out[d] = (r["createTime"], r["downloadUrl"])
        req = reporting.jobs().reports().list_next(req, resp)
    return {d: url for d, (_, url) in out.items()}


def doc_csv(text: str) -> dict[str, tuple[float, float]]:
    """CSV một ngày → video_id → (lượt hiển thị, số click). Bỏ dòng cấp kênh/video đã xoá (video_id rỗng).
    Đọc cột theo tên ở dòng tiêu đề vì tài liệu không cam kết thứ tự cột."""
    out: dict[str, tuple[float, float]] = {}
    for row in csv.DictReader(io.StringIO(text)):
        v = (row.get("video_id") or "").strip()
        if not v:
            continue
        impr = float(row.get("video_thumbnail_impressions") or 0)
        # shortcut: coi ctr là tỉ lệ 0–1 (tài liệu không nói đơn vị); kiểm lại với CTR Studio khi có báo cáo thật đầu tiên
        clicks = impr * float(row.get("video_thumbnail_impressions_ctr") or 0)
        a, b = out.get(v, (0.0, 0.0))
        out[v] = (a + impr, b + clicks)
    return out


def tai(reporting, url: str) -> str:
    """Tải nội dung một báo cáo (cách của mẫu chính thức: đặt uri vào request media.download)."""
    from googleapiclient.http import MediaIoBaseDownload
    req = reporting.media().download(resourceName=" ")
    req.uri = url
    buf = io.BytesIO()
    dl = MediaIoBaseDownload(buf, req, chunksize=-1)
    done = False
    while not done:
        _, done = dl.next_chunk()
    return buf.getvalue().decode("utf-8")


def ctr(ngay_csv: list[dict[str, tuple[float, float]]], video_id: str) -> float | None:
    """CTR gộp của một video trên nhiều ngày = tổng click / tổng hiển thị (không lấy trung bình CTR từng ngày). None nếu 0 hiển thị."""
    impr = sum(d.get(video_id, (0.0, 0.0))[0] for d in ngay_csv)
    clicks = sum(d.get(video_id, (0.0, 0.0))[1] for d in ngay_csv)
    return clicks / impr if impr else None


def hien_thi(ngay_csv: list[dict[str, tuple[float, float]]], video_id: str) -> int:
    """Tổng lượt hiển thị thumbnail của một video trên các ngày truyền vào."""
    return int(round(sum(d.get(video_id, (0.0, 0.0))[0] for d in ngay_csv)))
