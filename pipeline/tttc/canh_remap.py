"""Chuyển cảnh cũ sang mốc mới khi kịch bản đổi sau khi đã có cảnh.

Chạy: uv run python -m tttc.canh_remap ../videos/<slug> <giong-timing-cu.json>
Cảnh có dưới 60% từ khớp lời mới được nội suy mốc và báo để xem lại.
"""
import copy
import difflib
import json
import shutil
import sys
from pathlib import Path

from tttc.canh import _norm

MIN_KHOP = 0.6


def remap(canh: dict, old_timing: dict, new_timing: dict) -> tuple[dict, list[str]]:
    old_w, new_w = old_timing["words"], new_timing["words"]
    sm = difflib.SequenceMatcher(None, [_norm(w["w"]) for w in old_w], [_norm(w["w"]) for w in new_w], autojunk=False)
    map_ = {a + k: b + k for a, b, size in sm.get_matching_blocks() for k in range(size)}
    k_scale = new_timing["duration"] / old_timing["duration"] if old_timing["duration"] else 1.0
    out, notes, starts = copy.deepcopy(canh), [], []
    for c in out["scenes"]:
        idx = [i for i, w in enumerate(old_w) if c["start"] - 0.01 <= w["start"] < c["end"]]
        khop = [i for i in idx if i in map_]
        ty_le = len(khop) / len(idx) if idx else 1.0
        if ty_le < MIN_KHOP:
            notes.append(f"Cảnh báo: cảnh {c['id']} chỉ khớp {ty_le:.0%} lời, cần xem lại")
        first_ok = idx and idx[0] in map_
        starts.append(new_w[map_[idx[0]]]["start"] if first_ok
                      else new_w[map_[khop[0]]]["start"] if khop and ty_le >= MIN_KHOP
                      else c["start"] * k_scale)
    starts[0] = 0.0
    for i in range(1, len(starts)):  # mốc không lùi và không vượt tổng thời lượng mới
        starts[i] = min(max(starts[i], starts[i - 1]), new_timing["duration"])
    for i, c in enumerate(out["scenes"]):
        c["start"] = round(starts[i], 3)
        c["end"] = round(starts[i + 1] if i + 1 < len(starts) else new_timing["duration"], 3)
    return out, notes


def main(video_dir: str, old_timing_path: str) -> int:
    d = Path(video_dir)
    canh = json.loads((d / "canh.json").read_text(encoding="utf-8"))
    old = json.loads(Path(old_timing_path).read_text(encoding="utf-8"))
    new = json.loads((d / "giong-timing.json").read_text(encoding="utf-8"))
    shutil.copy(d / "canh.json", d / "canh-truoc-remap.json")
    out, notes = remap(canh, old, new)
    (d / "canh.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    for n in notes:
        print("-", n)
    print(f"{len(out['scenes'])} cảnh, {len(notes)} cảnh báo; bản cũ ở canh-truoc-remap.json")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
