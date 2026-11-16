"""Khám nghiệm tự động đường giữ chân người xem cho từng video (`videos/<slug>/kham-nghiem.md`).

Khớp 100 điểm `audienceWatchRatio` từ YouTube Analytics với phụ đề `phu-de.srt` và `canh.json`
để tìm chính xác câu thoại và mẫu cảnh tại các cú rơi mạnh nhất (> 5 điểm).
"""
import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from tttc import dang

ROOT = Path(__file__).resolve().parents[2]
VIDEOS_ROOT = ROOT / "videos"
VN = timezone(timedelta(hours=7))
CHO_DU_LIEU = 9
SRT_BLOCK = re.compile(
    r"\d+\s*\n(\d{2}):(\d{2}):(\d{2})[,.](\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2})[,.](\d{3})\s*\n(.*?)(?=\n\n|\Z)",
    re.S,
)


def _mmss(giay: float) -> str:
    s = max(0, int(round(giay)))
    return f"{s // 60}:{s % 60:02d}"


def _sec(h: str, m: str, s: str, ms: str) -> float:
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0


def tim_cu_roi(pts: list[tuple[float, float]], thoi_luong: float, nguong_diem: float = 5.0) -> list[dict]:
    """Tìm các bước nhảy sụt giảm >= `nguong_diem` (tính theo điểm phần trăm 0–100) giữa hai mốc liền kề.
    Bỏ qua vùng ratio <= 0.02 đầu video. Trả về danh sách sắp xếp từ rơi nặng nhất xuống nhẹ nhất."""
    if len(pts) < 2 or thoi_luong <= 0:
        return []
    ordered = sorted((float(r), float(w)) for r, w in pts)
    out = []
    for (r0, w0), (r1, w1) in zip(ordered, ordered[1:]):
        if r1 <= 0.02:
            continue
        drop = round((w0 - w1) * 100.0, 1)
        if drop >= nguong_diem:
            giay = round(r1 * thoi_luong, 1)
            out.append({
                "ratio": r1,
                "giay": giay,
                "mmss": _mmss(giay),
                "roi_diem": drop,
                "con_lai_pct": round(w1 * 100.0, 1),
            })
    return sorted(out, key=lambda x: (-x["roi_diem"], x["giay"]))


def khop_boi_canh(video_dir: Path | str, giay: float) -> dict:
    """Lấy câu thoại trong `phu-de.srt` và mẫu cảnh trong `canh.json` tại thời điểm `giay`."""
    d = Path(video_dir)
    thoai = "—"
    srt_p = d / "phu-de.srt"
    if srt_p.exists():
        try:
            raw = srt_p.read_text(encoding="utf-8", errors="ignore")
            cues = []
            for m in SRT_BLOCK.finditer(raw):
                h0, m0, s0, ms0, h1, m1, s1, ms1, txt = m.groups()
                t0, t1 = _sec(h0, m0, s0, ms0), _sec(h1, m1, s1, ms1)
                clean = " ".join(txt.strip().splitlines()).strip()
                cues.append((t0, t1, clean))
            exact = [c[2] for c in cues if c[0] - 1.5 <= giay <= c[1] + 1.5]
            if exact:
                thoai = " / ".join(exact[:2])
            elif cues:
                nearest = min(cues, key=lambda c: min(abs(giay - c[0]), abs(giay - c[1])))
                if min(abs(giay - nearest[0]), abs(giay - nearest[1])) <= 8.0:
                    thoai = nearest[2]
        except Exception:
            pass

    canh_id, mau = "—", "—"
    canh_p = d / "canh.json"
    if canh_p.exists():
        try:
            scenes = json.loads(canh_p.read_text(encoding="utf-8")).get("scenes", [])
            for sc in scenes:
                st, en = float(sc.get("start", 0)), float(sc.get("end", 0))
                if st <= giay <= en:
                    canh_id = str(sc.get("id", "—"))
                    mau = str(sc.get("mau", "—"))
                    if thoai == "—" and sc.get("loi"):
                        thoai = str(sc["loi"])
                    break
        except Exception:
            pass

    return {"thoai": thoai, "canh_id": canh_id, "mau": mau}


def _noi_suy(pts: list[tuple[float, float]], giay: float, thoi_luong: float) -> float | None:
    if not pts or thoi_luong <= giay or thoi_luong <= 0:
        return None
    full = [(0.0, 1.0)] + sorted((float(r) * thoi_luong, float(w)) for r, w in pts)
    for (t0, w0), (t1, w1) in zip(full, full[1:]):
        if t0 <= giay <= t1:
            val = w0 if t1 == t0 else w0 + (w1 - w0) * (giay - t0) / (t1 - t0)
            return round(val * 100.0, 1)
    return None


def tao_kham_nghiem(
    video_dir: Path | str,
    pts: list[tuple[float, float]],
    thoi_luong: float,
    ctr: str = "",
    hien_thi: str = "",
) -> Path:
    """Sinh tệp `videos/<slug>/kham-nghiem.md` phân tích đường giữ chân và các cú rơi."""
    d = Path(video_dir)
    roi = tim_cu_roi(pts, thoi_luong)
    g30 = _noi_suy(pts, 30.0, thoi_luong)
    c50 = _noi_suy(pts, thoi_luong / 2.0, thoi_luong)

    lines = [
        f"# Khám nghiệm giữ chân · `{d.name}`",
        "",
        f"- **Thời lượng:** {_mmss(thoi_luong)} ({thoi_luong:.0f}s)",
        f"- **CTR / Hiển thị:** {ctr or 'chưa có'} ({hien_thi or 'chưa có'} hiển thị)",
        f"- **Còn xem ở giây 30:** {f'{g30:.1f}%' if g30 is not None else 'chưa có'} (mục tiêu ≥ 75%)",
        f"- **Còn xem ở 50% thời lượng:** {f'{c50:.1f}%' if c50 is not None else 'chưa có'} (mục tiêu ≥ 35%)",
        "",
        "## Các cú rơi mạnh nhất (≥ 5 điểm)",
        "",
    ]
    if not roi:
        lines.append("Không có cú rơi đột ngột nào ≥ 5 điểm giữa hai mốc liền kề.")
    else:
        lines.extend([
            "| Mốc giây | Rơi (điểm) | Còn lại | Cảnh (`mau`) | Câu thoại đang đọc |",
            "|---|---|---|---|---|",
        ])
        for r in roi[:5]:
            ctx = khop_boi_canh(d, r["giay"])
            lines.append(
                f"| `{r['mmss']}` | **-{r['roi_diem']:.1f}** | {r['con_lai_pct']:.1f}% "
                f"| `{ctx['canh_id']}` (`{ctx['mau']}`) | {ctx['thoai']} |"
            )

    out = d / "kham-nghiem.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return out


def lay_duong_giu_chan(analytics, video_id: str, start_date: str, end_date: str) -> list[tuple[float, float]]:
    if analytics is None:
        return []
    try:
        rows = analytics.reports().query(
            ids="channel==MINE",
            startDate=start_date,
            endDate=end_date,
            metrics="audienceWatchRatio",
            dimensions="elapsedVideoTimeRatio",
            filters=f"video=={video_id}",
        ).execute().get("rows") or []
        return [(float(r), float(w)) for r, w in rows]
    except Exception:
        return []


def tim_thu_muc_video(videos_root: Path, video_id: str) -> Path | None:
    if not videos_root.exists():
        return None
    for d in sorted(videos_root.iterdir()):
        tt_p = d / "trang-thai.json"
        if not tt_p.exists():
            continue
        try:
            st = json.loads(tt_p.read_text(encoding="utf-8"))
            if st.get("video_id") == video_id:
                return d
        except Exception:
            continue
    return None


def cap_nhat_kham(
    rows: list[dict],
    thoi_luong: dict[str, float],
    analytics,
    now: datetime,
    videos_root: Path = VIDEOS_ROOT,
    som: bool = False,
) -> int:
    """Tự động sinh `kham-nghiem.md` và điền `roi_lon_nhat` vào `rows` cho các video dài đã có dữ liệu giữ chân."""
    if analytics is None:
        return 0
    changed = 0
    for r in rows:
        tieu = r.get("tieu_de", "")
        if "#shorts" in tieu.lower():
            continue
        m = re.search(r"youtu\.be/([A-Za-z0-9_-]+)", r.get("link", ""))
        v = m.group(1) if m else None
        if not v or v not in thoi_luong:
            continue
        if (r.get("roi_lon_nhat") or "").strip() and not som:
            continue
        try:
            ngay = datetime.strptime(r.get("gio_dang", ""), "%d/%m/%Y %H:%M").date()
        except ValueError:
            continue
        if not som and (now.date() - ngay).days < CHO_DU_LIEU:
            continue
        end_d = now.date().isoformat() if som else (ngay + timedelta(days=6)).isoformat()
        pts = lay_duong_giu_chan(analytics, v, ngay.isoformat(), end_d)
        if not pts:
            continue
        vdir = tim_thu_muc_video(videos_root, v)
        if vdir is not None:
            tao_kham_nghiem(vdir, pts, thoi_luong[v], ctr=r.get("ctr", ""), hien_thi=r.get("hien_thi_7d", ""))
        roi = tim_cu_roi(pts, thoi_luong[v])
        if roi and "roi_lon_nhat" in r:
            r["roi_lon_nhat"] = f"{roi[0]['mmss']} -{roi[0]['roi_diem']:.0f}pt"
            changed += 1
    return changed


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="python -m tttc.kham")
    p.add_argument("video_dir", help="Thư mục video (vd ../videos/<slug>)")
    p.add_argument("--som", action="store_true", help="Lấy dữ liệu giữ chân sớm từ ngày đăng tới hôm nay")
    args = p.parse_args(sys.argv[1:] if argv is None else argv)
    d = Path(args.video_dir)
    st = json.loads((d / "trang-thai.json").read_text(encoding="utf-8"))
    vid = st.get("video_id")
    if not vid:
        print(f"Thư mục {d} chưa có video_id")
        return 1
    tl = dang.thoi_luong(d / "final.mp4") or 500.0
    an = dang.analytics_client()
    pts = lay_duong_giu_chan(an, vid, "2026-11-01", datetime.now(VN).strftime("%Y-%m-%d"))
    if not pts:
        print(f"Chưa có dữ liệu giữ chân trên Analytics cho {vid}")
        return 0
    out = tao_kham_nghiem(d, pts, tl)
    print(f"Đã tạo {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
