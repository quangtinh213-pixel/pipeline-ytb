"""Kiểm canh.json theo timestamp giọng đọc và xuất phụ đề SRT."""
import json
import sys
from pathlib import Path

MAU = {"minh-hoa", "bieu-do", "so-lon", "nhan-vat", "trang-nguon", "chuong"}
SVG_DIR = Path(__file__).resolve().parent.parent / "svg"
TOL = 0.5      # lệch cho phép giữa hình và tiếng (giây)
EPS = 0.01     # sai số làm tròn giữa hai cảnh liền nhau


def validate(scenes: dict, timing: dict, svg_dir: Path = SVG_DIR, nguon: list | tuple = ()) -> list[str]:
    """Trả danh sách 'Lỗi: ...' (phải sửa) và 'Cảnh báo: ...' (nên xem)."""
    msgs, ids = [], {n["id"] for n in nguon}
    sc = scenes["scenes"]
    if not sc:
        return ["Lỗi: canh.json không có cảnh nào"]
    if abs(sc[0]["start"]) > TOL:
        msgs.append(f"Lỗi: cảnh đầu bắt đầu ở {sc[0]['start']} s, phải là 0")
    if abs(sc[-1]["end"] - timing["duration"]) > TOL:
        msgs.append(f"Lỗi: cảnh cuối kết thúc ở {sc[-1]['end']} s, tiếng dài {timing['duration']:.2f} s")
    for prev, cur in zip(sc, sc[1:]):
        if cur["start"] > prev["end"] + EPS:
            msgs.append(f"Lỗi: hở {cur['start'] - prev['end']:.2f} s giữa {prev['id']} và {cur['id']}")
        elif cur["start"] < prev["end"] - EPS:
            msgs.append(f"Lỗi: {prev['id']} và {cur['id']} chồng nhau {prev['end'] - cur['start']:.2f} s")
    seen = set()
    for c in sc:
        cid, dur = c["id"], c["end"] - c["start"]
        if cid in seen:
            msgs.append(f"Lỗi: trùng id cảnh {cid}")
        seen.add(cid)
        if c["mau"] not in MAU:
            msgs.append(f"Lỗi: {cid} dùng mẫu không có: {c['mau']}")
        if dur < 2 or dur > 12:
            msgs.append(f"Lỗi: {cid} dài {dur:.1f} s (cho phép 2–12 s)")
        elif dur < 4 or dur > 8:
            msgs.append(f"Cảnh báo: {cid} dài {dur:.1f} s (nên 4–8 s)")
        if c.get("svg") and not (Path(svg_dir) / f"{c['svg']}.svg").exists():
            msgs.append(f"Lỗi: {cid} cần hình {c['svg']}.svg chưa có trong thư viện")
        nid = (c.get("bieu_do") or {}).get("nguon_id") or c.get("nguon_id")
        if nid and nid not in ids:
            msgs.append(f"Lỗi: {cid} trỏ tới nguồn [#{nid}] không có trong nguon.json")
    return msgs


def _ts(t: float) -> str:
    ms = round(t * 1000)
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def to_srt(timing: dict, max_chars: int = 42) -> str:
    cues, cur = [], []
    for w in timing["words"]:
        if cur and len(" ".join(x["w"] for x in cur + [w])) > max_chars:
            cues.append(cur)
            cur = []
        cur.append(w)
        if w["w"][-1:] in ".!?":
            cues.append(cur)
            cur = []
    if cur:
        cues.append(cur)
    return "".join(f"{i}\n{_ts(c[0]['start'])} --> {_ts(c[-1]['end'])}\n{' '.join(x['w'] for x in c)}\n\n"
                   for i, c in enumerate(cues, 1))


def main(video_dir: str) -> int:
    d = Path(video_dir)
    timing = json.loads((d / "giong-timing.json").read_text(encoding="utf-8"))
    nguon = json.loads((d / "nguon.json").read_text(encoding="utf-8")) if (d / "nguon.json").exists() else []
    msgs = validate(json.loads((d / "canh.json").read_text(encoding="utf-8")), timing, SVG_DIR, nguon)
    for m in msgs:
        print("-", m)
    (d / "phu-de.srt").write_text(to_srt(timing), encoding="utf-8")
    errs = [m for m in msgs if m.startswith("Lỗi")]
    print(f"{len(errs)} lỗi, {len(msgs) - len(errs)} cảnh báo; đã ghi phu-de.srt")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
