"""Kiểm canh.json theo timestamp giọng đọc và xuất phụ đề SRT."""
import json
import sys
from pathlib import Path

from tttc.kiem import NUM, _scale, tokens, vi_value

MAU = {"minh-hoa", "bieu-do", "so-lon", "nhan-vat", "trang-nguon", "chuong"}
SVG_DIR = Path(__file__).resolve().parent.parent / "svg"
TOL = 0.5      # lệch cho phép giữa hình và tiếng (giây)
EPS = 0.01     # sai số làm tròn giữa hai cảnh liền nhau


def validate(scenes: dict, timing: dict, svg_dir: Path = SVG_DIR, nguon: list | tuple = ()) -> list[str]:
    """Trả danh sách 'Lỗi: ...' (phải sửa) và 'Cảnh báo: ...' (nên xem)."""
    by_id = {n["id"]: n for n in nguon}
    msgs, ids = [], set(by_id)
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
        nids = nid if isinstance(nid, list) else [nid] if nid else []
        for n in nids:
            if n not in ids:
                msgs.append(f"Lỗi: {cid} trỏ tới nguồn [#{n}] không có trong nguon.json")
        msgs += _check_values(c, [by_id[n] for n in nids if n in by_id], bool(nids))
    return msgs


def _unit_scale(text: str) -> str:
    m = NUM.search("1 " + (text or "").strip())
    return _scale(m.group(2)) if m else ""


def _check_values(c: dict, srcs: list[dict], has_ref: bool) -> list[str]:
    """Số hiện trên màn hình (so-lon, bieu-do) phải có nguồn và khớp giá trị + quy mô trong nguồn."""
    if c["mau"] == "so-lon" and "so" in c:
        vals, scale = [c["so"]], _unit_scale(c.get("truoc", "") + " " + c.get("sau", ""))
    elif c["mau"] == "bieu-do" and c.get("bieu_do"):
        vals, scale = c["bieu_do"]["gia_tri"], _unit_scale(c["bieu_do"].get("don_vi", ""))
    else:
        return []
    if not has_ref:
        return [f"Lỗi: {c['id']} hiện số nhưng thiếu nguon_id"]
    allowed = {(v, sc) for s in srcs for _, v, sc in tokens(s["gia_tri"])}
    out = []
    for v in vals:
        num = vi_value(v) if isinstance(v, str) else float(v)
        if (num, scale) not in allowed:
            out.append(f"Lỗi: {c['id']} hiện {v}{' ' + scale if scale else ''} không khớp nguồn "
                       f"{[s['id'] for s in srcs]}")
    return out


def _ts(t: float) -> str:
    ms = round(t * 1000)
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def cues(timing: dict, max_chars: int = 42) -> list[tuple[float, float, str]]:
    """Gom từ thành dòng phụ đề ≤ max_chars, ngắt sau dấu kết câu."""
    groups, cur = [], []
    for w in timing["words"]:
        if cur and len(" ".join(x["w"] for x in cur + [w])) > max_chars:
            groups.append(cur)
            cur = []
        cur.append(w)
        if w["w"][-1:] in ".!?":
            groups.append(cur)
            cur = []
    if cur:
        groups.append(cur)
    return [(g[0]["start"], g[-1]["end"], " ".join(x["w"] for x in g)) for g in groups]


def to_srt(timing: dict, max_chars: int = 42) -> str:
    return "".join(f"{i}\n{_ts(a)} --> {_ts(b)}\n{t}\n\n" for i, (a, b, t) in enumerate(cues(timing, max_chars), 1))


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
