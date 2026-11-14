"""Module giám sát hiệu suất và tự động cấp cứu bao bì (CTR Monitor & Auto-Pivot).

Khi một video có CTR < 4% sau 3 giờ công khai:
- Phát cảnh báo nguy cấp (Báo động đỏ).
- Tự động hoặc hỗ trợ đổi sang phương án Tiêu đề & Thumbnail dự phòng trong dong-goi.json.
"""
import csv
import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

from tttc import dang, theo_doi
from tttc import trang_thai as tt

VN = timezone(timedelta(hours=7))
NGUONG_CTR_CANH_BAO = 5.0
NGUONG_CTR_NGUY_CAP = 4.0


def lay_thong_tin_video(video_id: str, youtube=None) -> dict[str, Any]:
    """Lấy thông tin và số liệu thống kê của video từ YouTube Data API."""
    yt = youtube or dang.client()
    resp = yt.videos().list(part="snippet,statistics,status", id=video_id).execute()
    if not resp.get("items"):
        raise ValueError(f"Không tìm thấy video với ID {video_id} trên YouTube")
    item = resp["items"][0]
    return {
        "id": video_id,
        "title": item["snippet"]["title"],
        "description": item["snippet"]["description"],
        "published_at": item["snippet"].get("publishedAt"),
        "privacy": item["status"].get("privacyStatus"),
        "views": int(item["statistics"].get("viewCount", 0)),
        "likes": int(item["statistics"].get("likeCount", 0)),
        "comments": int(item["statistics"].get("commentCount", 0)),
    }


def danh_gia_ctr(ctr_val: float | str | None) -> str:
    """Đánh giá mức độ an toàn của chỉ số CTR.
    Trả về: 'AN_TOAN' | 'CANH_BAO' | 'NGUY_CAP' | 'CHUA_CO_SO_LIEU'
    """
    if ctr_val is None or ctr_val == "" or ctr_val == "-":
        return "CHUA_CO_SO_LIEU"
    try:
        val_str = str(ctr_val).replace("%", "").strip()
        val = float(val_str)
    except ValueError:
        return "CHUA_CO_SO_LIEU"

    if val < NGUONG_CTR_NGUY_CAP:
        return "NGUY_CAP"
    elif val < NGUONG_CTR_CANH_BAO:
        return "CANH_BAO"
    return "AN_TOAN"


def dang_dung(state: dict) -> int:
    """Phương án đang chạy trên YouTube: bản đã đổi bao bì, nếu chưa đổi thì bản chọn ở duyệt 2."""
    return state.get("pa_dang_dung") or state.get("chon") or 1


def lay_cac_phuong_an(video_dir: Path | str) -> list[dict]:
    """Đọc danh sách các phương án tiêu đề và thumbnail từ dong-goi.json."""
    d = Path(video_dir)
    pkg_file = d / "dong-goi.json"
    if not pkg_file.exists():
        return []
    data = json.loads(pkg_file.read_text(encoding="utf-8"))
    return data.get("phuong_an", [])


def doi_bao_bi(video_dir: Path | str, phuong_an_so: int, youtube=None, tracker: Path = dang.TRACKER) -> dict:
    """Thực hiện đổi Tiêu đề và Thumbnail của video trên YouTube sang phương án chỉ định (1-based index).
    Đồng thời cập nhật trang-thai.json và theo-doi.csv.
    """
    d = Path(video_dir)
    state = tt.load(d)
    vid = state.get("video_id")
    if not vid:
        raise ValueError(f"Thư mục {d} chưa có video_id đã upload")

    opts = lay_cac_phuong_an(d)
    if not opts or not 1 <= phuong_an_so <= len(opts):
        raise ValueError(f"Phương án {phuong_an_so} không tồn tại trong dong-goi.json (có {len(opts)} phương án)")

    old_chon = dang_dung(state)
    chon = opts[phuong_an_so - 1]
    new_title = chon["tieu_de"]
    dang._check_text(new_title, "", [])  # YouTube từ chối tiêu đề sai luật: báo trước khi gọi API
    thumb_path = d / chon["file_thumb"]

    yt = youtube or dang.client()

    # 1. Cập nhật Tiêu đề trên YouTube
    v_resp = yt.videos().list(part="snippet", id=vid).execute()
    if not v_resp.get("items"):
        raise RuntimeError(f"Không tìm thấy video {vid} trên YouTube để cập nhật")

    snippet = v_resp["items"][0]["snippet"]
    old_title = snippet["title"]
    snippet["title"] = new_title
    yt.videos().update(part="snippet", body={"id": vid, "snippet": snippet}).execute()

    # 2. Cập nhật Thumbnail trên YouTube nếu file ảnh tồn tại
    thumb_updated = False
    if thumb_path.exists():
        media = dang._thumb_media(thumb_path)
        yt.thumbnails().set(videoId=vid, media_body=media).execute(num_retries=dang.RETRIES)
        thumb_updated = True

    # 3. Cập nhật trang-thai.json
    da_thu = list(dict.fromkeys([*(state.get("da_thu_pa") or []), old_chon, phuong_an_so]))
    # không ghi đè `chon`: đó là lựa chọn trong biên nhận duyệt 2, đổi nó làm Shorts mất duyệt
    tt.set_fields(d, pa_dang_dung=phuong_an_so, da_thu_pa=da_thu)

    # 4. Cập nhật theo-doi.csv
    if tracker.exists():
        with dang._lock(tracker.with_name(f".{tracker.name}.lock")):
            with tracker.open(encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames or []
                rows = list(reader)

            link = f"https://youtu.be/{vid}"
            for r in rows:
                if r.get("link") == link:
                    r["tieu_de"] = new_title
                    break

            tmp = tracker.with_name(f".{tracker.name}.tmp")
            with tmp.open("w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
                w.writeheader()
                w.writerows(rows)
            tmp.replace(tracker)

    return {
        "video_id": vid,
        "old_title": old_title,
        "new_title": new_title,
        "thumb_updated": thumb_updated,
        "phuong_an": phuong_an_so
    }


def lay_chi_so_analytics(video_id: str, start_date: str, end_date: str | None = None, analytics=None) -> dict[str, Any] | None:
    """Đọc view/thời lượng xem trung bình từ YouTube Analytics API nếu token có quyền; trả None nếu thiếu quyền hoặc lỗi.
    API không có CTR thumbnail (thử 14/11/2026: 400 "query is not supported"); CTR vẫn lấy từ YouTube Studio."""
    if analytics is None:
        return None
    end_d = end_date or datetime.now(VN).strftime("%Y-%m-%d")
    try:
        resp = analytics.reports().query(
            ids="channel==MINE",
            startDate=start_date,
            endDate=end_d,
            metrics="views,averageViewDuration,averageViewPercentage",
            filters=f"video=={video_id}",
        ).execute()
        rows = resp.get("rows") or []
        headers = [h.get("name") for h in resp.get("columnHeaders") or []]
        if not rows or not headers:
            return None
        return dict(zip(headers, rows[0]))
    except Exception:
        return None


def giu_chan_tai(analytics, video_id: str, giay: float, thoi_luong: float, start_date: str, end_date: str) -> float | None:
    """Tỉ lệ người xem còn ở giây `giay` (audienceWatchRatio, nội suy giữa 100 điểm của báo cáo giữ chân).
    None nếu video ngắn hơn `giay`, chưa có dữ liệu hoặc lỗi API."""
    if analytics is None or thoi_luong <= giay:
        return None
    try:
        rows = analytics.reports().query(
            ids="channel==MINE", startDate=start_date, endDate=end_date,
            metrics="audienceWatchRatio", dimensions="elapsedVideoTimeRatio", filters=f"video=={video_id}",
        ).execute().get("rows") or []
    except Exception:
        return None
    if not rows:
        return None
    pts = [(0.0, 1.0)] + sorted((float(r) * thoi_luong, float(w)) for r, w in rows)  # mỗi điểm là cuối khoảng; giây 0 coi như đủ người
    for (t0, w0), (t1, w1) in zip(pts, pts[1:]):
        if t0 <= giay <= t1:
            return w0 if t1 == t0 else w0 + (w1 - w0) * (giay - t0) / (t1 - t0)
    return None


def kiem_tra_video(
    video_dir: Path | str,
    ctr_val: float | str | None = None,
    tu_dong_doi: bool = False,
    youtube=None,
    tracker: Path = dang.TRACKER,
) -> dict[str, Any]:
    """Kiểm tra trạng thái CTR/lượt xem của video đã đăng và xoay sang phương án dự phòng nếu nguy cấp."""
    d = Path(video_dir)
    state = tt.load(d)
    vid = state.get("video_id")
    if not vid:
        raise ValueError(f"Thư mục {d} chưa có video_id đã upload")
    info = lay_thong_tin_video(vid, youtube=youtube)
    muc = danh_gia_ctr(ctr_val)
    opts = lay_cac_phuong_an(d)
    chon = dang_dung(state)
    out: dict[str, Any] = {"video": info, "trang_thai_ctr": muc, "chon_hien_tai": chon, "da_doi": None}
    if muc == "NGUY_CAP" and tu_dong_doi and len(opts) > 1:
        da_thu = set(state.get("da_thu_pa") or []) | {chon}
        ke_tiep = next(
            (p for step in range(1, len(opts) + 1) if (p := ((chon - 1 + step) % len(opts)) + 1) not in da_thu),
            None,
        )
        if ke_tiep is not None:
            out["da_doi"] = doi_bao_bi(d, ke_tiep, youtube=youtube, tracker=tracker)
    return out


def main(argv: list[str] | None = None) -> int:
    import argparse
    import sys

    p = argparse.ArgumentParser(prog="python -m tttc.giam_sat")
    p.add_argument("video_dir", help="Thư mục video (vd ../videos/<slug>)")
    p.add_argument("--ctr", default=None, help="Giá trị CTR từ YouTube Studio (vd 3.2 hoặc 3.2%%)")
    p.add_argument("--auto-pivot", action="store_true", help="Tự đổi sang phương án kế tiếp nếu CTR < 4%%")
    args = p.parse_args(argv)
    kq = kiem_tra_video(args.video_dir, ctr_val=args.ctr, tu_dong_doi=args.auto_pivot)
    v = kq["video"]
    print(f"{v['id']} · {v['views']} view · {v['likes']} thích · CTR={kq['trang_thai_ctr']} · đang dùng PA {kq['chon_hien_tai']}")
    if kq["da_doi"]:
        print(f"ĐÃ XOAY BAO BÌ → PA {kq['da_doi']['phuong_an']}: {kq['da_doi']['new_title']}")
    elif kq["trang_thai_ctr"] == "NGUY_CAP":
        print("⚠️ BÁO ĐỘNG ĐỎ CTR < 4%: chạy lại với --auto-pivot để xoay sang phương án dự phòng.")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
