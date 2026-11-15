"""Chia lời đọc thành các cảnh liền nhau theo mốc từ trong giong-timing.json.

Chạy: uv run python -m tttc.chia ../videos/<slug>  → canh-khung.json (Claude điền mau và nội dung từng cảnh).
"""
import json
import re
import sys
from pathlib import Path

from tttc import tts

LIEN_TU = {"mà", "nhưng", "còn", "thì", "vì", "nên", "rồi"}
CAU, PHAY = ".!?…", ",;:"
BEAT_TOI_THIEU = 1.5  # cảnh ngắn nhất được phép khi phải ngắt đúng mốc beat (tttc.canh báo lỗi dưới 1,5 s)


def moc_beat(script_md: str, timing: dict) -> list[float]:
    """Mốc thời gian bắt đầu của mỗi phần/Beat (trừ phần đầu tiên ở t=0) dựa trên kich-ban.md và timing['paragraphs']."""
    paras_t = timing.get("paragraphs") or []
    if not paras_t or not script_md:
        return []
    beats, para_idx, on, pending_beat = [], 0, False, False
    for line in tts._nfc(script_md).splitlines():
        s = line.strip()
        if re.fullmatch(r"[-*_]{3,}", s):
            on = False
            continue
        m = tts.SPOKEN.search(s)
        if m:
            on, s = True, s[m.end():]
        elif s.startswith("#") or "[TRÊN MÀN HÌNH]" in s or s.startswith("* **"):
            if s.startswith("#"):
                pending_beat = True
            on = False
            continue
        if on:
            cleaned = re.sub(r"\s+", " ", tts.TAG.sub("", s).replace("*", "")).strip()
            if cleaned:
                if pending_beat and 0 < para_idx < len(paras_t):
                    t = float(paras_t[para_idx]["start"])
                    if t > 0:
                        beats.append(t)
                pending_beat = False
                para_idx += 1
    return sorted(set(beats))


def _diem(words: list[dict], j: int, dur: float, muc: float) -> float:
    """Điểm ngắt sau từ j: gần `muc` giây, ưu tiên kết câu, rồi dấu phẩy, rồi đứng trước liên từ."""
    w = words[j]["w"]
    bonus = 3.0 if w[-1:] in CAU else 1.5 if w[-1:] in PHAY else 0.0
    if j + 1 < len(words) and words[j + 1]["w"].lower().strip(",.") in LIEN_TU:
        bonus = max(bonus, 1.0)
    return bonus - abs(dur - muc)


def chia(
    timing: dict,
    muc: float = 3.5,
    toi_thieu: float = 2.5,
    toi_da: float = 5.5,
    muc_dau: float | None = None,
    toi_thieu_dau: float | None = None,
    toi_da_dau: float | None = None,
    cua_so_dau: float = 30.0,
    moc_beat_ts: list[float] | None = None,
) -> list[dict]:
    words, total = timing["words"], timing["duration"]
    if not words:
        return []
    beats = sorted(b for b in (moc_beat_ts or []) if 0 < b < total)

    def bien(j: int) -> float:  # mốc kết thúc nếu ngắt sau từ j: giữa khe hở tới từ kế, từ cuối thì hết tiếng
        return total if j == len(words) - 1 else (words[j]["end"] + words[j + 1]["start"]) / 2

    out, i, t0 = [], 0, 0.0
    while i < len(words):
        dau = muc_dau is not None and t0 < cua_so_dau
        cur_muc = muc_dau if dau else muc
        cur_min = (toi_thieu_dau or toi_thieu) if dau else toi_thieu
        cur_max = (toi_da_dau or toi_da) if dau else toi_da
        next_beat = next((b for b in beats if b > t0 + 0.05), None)
        prefer_beat = next_beat is not None and cur_min <= (next_beat - t0) <= cur_max + 0.5
        cand = []
        for j in range(i, len(words)):
            end_t = bien(j)
            dur = end_t - t0
            if dur > cur_max and j > i:
                break
            rem_min = toi_thieu_dau if (toi_thieu_dau and end_t < cua_so_dau) else toi_thieu
            sat_beat = next_beat is not None and abs(end_t - next_beat) <= 0.35
            # beat tới sớm hơn mức tối thiểu: vẫn cho ngắt đúng mốc beat nếu cảnh ≥ BEAT_TOI_THIEU, đừng để cảnh vắt qua chương
            du_dai = dur >= cur_min or (sat_beat and not prefer_beat and dur >= BEAT_TOI_THIEU)
            if du_dai and (j == len(words) - 1 or total - end_t >= rem_min):
                score = _diem(words, j, dur, cur_muc)
                if sat_beat:
                    score += 5.0 - abs(end_t - next_beat)
                elif next_beat is not None and end_t > next_beat + 0.35:
                    score -= 4.0
                cand.append((score, j))
        # chỉ có khe lặng dài làm mọi điểm ngắt vượt cur_max: chịu cảnh dài hơn còn hơn cảnh quá ngắn
        j = max(cand)[1] if cand else next((k for k in range(i, len(words)) if bien(k) - t0 >= cur_min), len(words) - 1)
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
    kb_path = d / "kich-ban.md"
    beats = moc_beat(kb_path.read_text(encoding="utf-8"), timing) if kb_path.exists() else []
    scenes = chia(timing, muc_dau=2.4, toi_thieu_dau=1.8, toi_da_dau=3.2, moc_beat_ts=beats)
    (d / "canh-khung.json").write_text(json.dumps({"scenes": scenes}, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    print(f"{len(scenes)} cảnh, trung bình {timing['duration'] / max(len(scenes), 1):.1f} s; đã ghi canh-khung.json")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
