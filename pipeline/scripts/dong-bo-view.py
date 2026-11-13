"""Đồng bộ lượt xem từ YouTube Data API về theo-doi.csv (view_24h, view_7d theo tuổi video).
Chạy: uv run python scripts/dong-bo-view.py  – nên chạy mỗi ngày để không lỡ cửa sổ 24–48 giờ.
"""
import csv
import re
from datetime import datetime
from pathlib import Path
from tttc.dang import client, _lock
from tttc.theo_doi import VN, dien_view

ROOT = Path(__file__).resolve().parents[2]
TRACKER = ROOT / "theo-doi.csv"
LO = 50  # videos.list nhận tối đa 50 id mỗi lần


def _vid(r: dict) -> str | None:
    m = re.search(r"youtu\.be/([A-Za-z0-9_-]+)", r.get("link", ""))
    return m.group(1) if m else None


def dong_bo():
    if not TRACKER.exists():
        print("Không tìm thấy theo-doi.csv")
        return

    with _lock(TRACKER.with_name(f".{TRACKER.name}.lock")):
        with TRACKER.open(encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []
            rows = list(reader)

        vids = [v for r in rows if (v := _vid(r))]
        if not vids:
            print("Không có video id trong theo-doi.csv")
            return

        yt = client()
        stats = {}
        for i in range(0, len(vids), LO):
            resp = yt.videos().list(part="statistics", id=",".join(vids[i:i + LO])).execute()
            stats |= {it["id"]: it["statistics"].get("viewCount", "0") for it in resp.get("items", [])}

        now = datetime.now(VN)
        updated = sum(dien_view(r, stats[v], now) for r in rows if (v := _vid(r)) in stats)

        tmp = TRACKER.with_name(f".{TRACKER.name}.tmp")
        with tmp.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)
        tmp.replace(TRACKER)
        print(f"Đã điền số view cho {updated}/{len(rows)} video vào theo-doi.csv")


if __name__ == "__main__":
    dong_bo()
