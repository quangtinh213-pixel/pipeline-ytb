"""Chia lời đọc thành các cảnh liền nhau theo mốc từ trong giong-timing.json.

Chạy: uv run python -m tttc.chia ../videos/<slug>  → canh-khung.json (Claude điền mau và nội dung từng cảnh).
"""
import json
import sys
from pathlib import Path

LIEN_TU = {"mà", "nhưng", "còn", "thì", "vì", "nên", "rồi"}
CAU, PHAY = ".!?…", ",;:"


def _diem(words: list[dict], j: int, dur: float, muc: float) -> float:
    """Điểm ngắt sau từ j: gần `muc` giây, ưu tiên kết câu, rồi dấu phẩy, rồi đứng trước liên từ."""
    w = words[j]["w"]
    bonus = 3.0 if w[-1:] in CAU else 1.5 if w[-1:] in PHAY else 0.0
    if j + 1 < len(words) and words[j + 1]["w"].lower().strip(",.") in LIEN_TU:
        bonus = max(bonus, 1.0)
    return bonus - abs(dur - muc)


def chia(timing: dict, muc: float = 3.5, toi_thieu: float = 2.0, toi_da: float = 5.5) -> list[dict]:
    words, total = timing["words"], timing["duration"]
    if not words:
        return []

    def bien(j: int) -> float:  # mốc kết thúc nếu ngắt sau từ j: giữa khe hở tới từ kế, từ cuối thì hết tiếng
        return total if j == len(words) - 1 else (words[j]["end"] + words[j + 1]["start"]) / 2

    out, i, t0 = [], 0, 0.0
    while i < len(words):
        cand, fallback = [], i
        for j in range(i, len(words)):
            dur = bien(j) - t0
            if dur > toi_da and j > i:
                break
            fallback = j
            if dur >= toi_thieu and (j == len(words) - 1 or total - bien(j) >= toi_thieu):
                cand.append((_diem(words, j, dur, muc), j))
        j = max(cand)[1] if cand else fallback
        out.append({"id": f"c{len(out) + 1:03}", "start": round(t0, 3), "end": round(bien(j), 3),
                    "loi": " ".join(w["w"] for w in words[i:j + 1])})
        i, t0 = j + 1, bien(j)
    if len(out) > 1 and out[-1]["end"] - out[-1]["start"] < toi_thieu:  # mảnh đuôi không đủ dài: gộp vào cảnh trước
        last = out.pop()
        out[-1].update(end=last["end"], loi=out[-1]["loi"] + " " + last["loi"])
    return out


def main(video_dir: str) -> int:
    d = Path(video_dir)
    timing = json.loads((d / "giong-timing.json").read_text(encoding="utf-8"))
    scenes = chia(timing)
    (d / "canh-khung.json").write_text(json.dumps({"scenes": scenes}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(scenes)} cảnh, trung bình {timing['duration'] / max(len(scenes), 1):.1f} s; đã ghi canh-khung.json")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
