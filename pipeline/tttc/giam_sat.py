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

    chon = opts[phuong_an_so - 1]
    new_title = chon["tieu_de"]
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
        media = dang._media(thumb_path, "image/png")
        yt.thumbnails().set(videoId=vid, media_body=media).execute(num_retries=dang.RETRIES)
        thumb_updated = True

    # 3. Cập nhật trang-thai.json
    tt.set_field(d, "chon", phuong_an_so)

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
