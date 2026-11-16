"""Báo cáo tuần tự động (`docs/bao-cao/<yyyy-Www>.md`): tách riêng Video dài vs Shorts,
so sánh theo nhóm/khuôn thumbnail, tổng hợp thị trường đối thủ từ `doi-thu.csv` và các luật đã kích hoạt.
"""
import argparse
import csv
import statistics
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from tttc import giam_sat

ROOT = Path(__file__).resolve().parents[2]
TRACKER = ROOT / "theo-doi.csv"
DOI_THU = ROOT / "doi-thu.csv"
BAO_CAO_DIR = ROOT / "docs" / "bao-cao"
VN = timezone(timedelta(hours=7))


def _num(v) -> float | None:
    if v is None:
        return None
    s = str(v).replace("%", "").replace(",", ".").strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _med(rows: list[dict], col: str, suffix: str = "") -> str:
    vals = [x for r in rows if (x := _num(r.get(col))) is not None]
    if not vals:
        return "— (n = 0)"
    m = statistics.median(vals)
    fmt = f"{m:.1f}{suffix}" if suffix else f"{m:.0f}"
    return f"{fmt} (n = {len(vals)})"


def tao_bao_cao(
    rows: list[dict],
    doi_thu_rows: list[dict],
    now: datetime,
    out_dir: Path = BAO_CAO_DIR,
    tuan: str | None = None,
) -> Path:
    iso_y, iso_w, _ = now.isocalendar()
    ma_tuan = tuan or f"{iso_y}-W{iso_w:02d}"
    dai = [r for r in rows if "#shorts" not in (r.get("tieu_de") or "").lower()]
    shorts = [r for r in rows if "#shorts" in (r.get("tieu_de") or "").lower()]

    lines = [
        f"# Báo cáo tuần {ma_tuan}",
        "",
        f"- **Ngày tổng hợp:** {now:%d/%m/%Y %H:%M}",
        f"- **Tổng mẫu trong sổ:** n = {len(rows)} ({len(dai)} Video dài, {len(shorts)} Shorts) — *mẫu nhỏ chỉ là hướng nghiêng*",
        "",
        "## 1. Tổng hợp Video dài vs Shorts",
        "",
        "| Loại | Số lượng | Trung vị `view_24h` | Trung vị `view_7d` | Trung vị `ctr` | Trung vị `giu_chan_30s` | Trung vị `con_50pct` | Trung vị `avd_pct` |",
        "|---|---|---|---|---|---|---|---|",
        (
            f"| **Video dài** | n = {len(dai)} | {_med(dai, 'view_24h')} | {_med(dai, 'view_7d')} "
            f"| {_med(dai, 'ctr', '%')} | {_med(dai, 'giu_chan_30s', '%')} "
            f"| {_med(dai, 'con_50pct', '%')} | {_med(dai, 'avd_pct', '%')} |"
        ),
        (
            f"| **Shorts** | n = {len(shorts)} | {_med(shorts, 'view_24h')} | {_med(shorts, 'view_7d')} "
            f"| {_med(shorts, 'ctr', '%')} | ở lại: {_med(shorts, 'o_lai_short', '%')} "
            f"| — | — |"
        ),
        "",
        "## 2. So sánh theo Khuôn Thumbnail & Định vị (Video dài)",
        "",
    ]

    khuons = sorted({(r.get("khuon_thumb") or "chưa gắn") for r in dai})
    if khuons:
        lines.extend([
            "### 2.1 Theo khuôn thumbnail",
            "",
            "| Khuôn (`khuon_thumb`) | Số video | Trung vị `ctr` | Trung vị `view_24h` |",
            "|---|---|---|---|",
        ])
        for k in khuons:
            sub = [r for r in dai if (r.get("khuon_thumb") or "chưa gắn") == k]
            lines.append(f"| `{k}` | n = {len(sub)} | {_med(sub, 'ctr', '%')} | {_med(sub, 'view_24h')} |")
        lines.append("")

    gocs = sorted({(r.get("goc") or "chưa gắn") for r in dai})
    if gocs:
        lines.extend([
            "### 2.2 Theo góc tiếp cận (`goc`)",
            "",
            "| Góc (`goc`) | Số video | Trung vị `view_24h` | Trung vị `giu_chan_30s` |",
            "|---|---|---|---|",
        ])
        for g in gocs:
            sub = [r for r in dai if (r.get("goc") or "chưa gắn") == g]
            lines.append(f"| `{g}` | n = {len(sub)} | {_med(sub, 'view_24h')} | {_med(sub, 'giu_chan_30s', '%')} |")
        lines.append("")

    lines.extend([
        "## 3. Thị trường Đối thủ (`doi-thu.csv`)",
        "",
    ])
    if not doi_thu_rows:
        lines.append("Chưa có dữ liệu đối thủ (n = 0).")
    else:
        ca = [r for r in doi_thu_rows if r.get("nhom_de") == "cluster-a"]
        lines.append(
            f"- Tổng số video đối thủ theo dõi: **n = {len(doi_thu_rows)}** "
            f"(nhóm `cluster-a`: **{len(ca)}/{len(doi_thu_rows)}** video, trung vị view `{_med(ca, 'view_moi_nhat')}`)."
        )
        lines.extend([
            "",
            "| Kênh | Tiêu đề | Nhóm đề | View mới nhất | Breakout |",
            "|---|---|---|---|---|",
        ])
        top_dt = sorted(doi_thu_rows, key=lambda r: _num(r.get("view_moi_nhat")) or 0.0, reverse=True)[:5]
        for r in top_dt:
            lines.append(
                f"| {r.get('kenh', '')} | {r.get('tieu_de', '')[:65]} | `{r.get('nhom_de', '')}` "
                f"| {r.get('view_moi_nhat', '')} | {r.get('breakout', '')}× |"
            )

    lines.extend([
        "",
        "## 4. Luật quyết định đã kích hoạt & Việc cần làm trên YouTube Studio",
        "",
    ])
    luat = giam_sat.luat_so(rows, now)
    if not luat:
        lines.append("- Không có luật ngưỡng tuyệt đối nào kích hoạt.")
    else:
        for *_, msg in luat:
            lines.append(f"- **Luật:** {msg}")

    lines.extend([
        "- **Việc thủ công trên Studio:**",
        "  1. Bật **Test & Compare** với bộ 3 ảnh (`1.png` `ban-co-toi`, `2.png` `ho-so`, `3.png`) cho các video dài mới đăng.",
        "  2. Gắn **Video liên quan (Related Video)** cho các Shorts mới trỏ về video dài cùng chuỗi.",
        "  3. Ghim bình luận câu hỏi / đường dẫn tập trước trong chuỗi.",
    ])

    out_p = Path(out_dir)
    out_p.mkdir(parents=True, exist_ok=True)
    file_p = out_p / f"{ma_tuan}.md"
    file_p.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return file_p


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="python -m tttc.bao_cao")
    p.add_argument("--so", default=str(TRACKER), help="Đường dẫn theo-doi.csv")
    p.add_argument("--doi-thu", default=str(DOI_THU), help="Đường dẫn doi-thu.csv")
    p.add_argument("--tuan", default=None, help="Mã tuần (vd 2026-W46)")
    args = p.parse_args(sys.argv[1:] if argv is None else argv)

    rows = list(csv.DictReader(open(args.so, encoding="utf-8", newline=""))) if Path(args.so).exists() else []
    dt_rows = list(csv.DictReader(open(args.doi_thu, encoding="utf-8", newline=""))) if Path(args.doi_thu).exists() else []
    out = tao_bao_cao(rows, dt_rows, datetime.now(VN), tuan=args.tuan)
    print(f"Đã tạo báo cáo tuần: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
