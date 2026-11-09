"""Giọng làm thủ công (thu âm, ElevenLabs web, TTS khác): nhập tệp tiếng + kịch bản → giong.mp3 + giong-timing.json.

Pipeline cần mốc thời gian từng từ (chia cảnh, nhịp con, phụ đề). Tệp tiếng không có sẵn mốc nên phải phiên âm
(hyperframes transcribe, whisper) hoặc nhập phụ đề .srt rồi căn từng từ của kịch bản vào đó.
Chạy: uv run python -m tttc.giong_tay ../videos/<slug> giong1.mp3 [giong2.mp3 ...] [--srt phu-de.srt]
"""
import difflib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from tttc import tts
from tttc.canh import _norm

PIPE = Path(__file__).resolve().parent.parent
MIN_KHOP = 0.5  # dưới ngưỡng này coi là tệp tiếng không phải kịch bản này


def _chia_deu(words: list[str], t0: float, t1: float) -> list[tuple[float, float]]:
    """Rải các từ vào [t0, t1] theo số ký tự (kèm khoảng trắng); từ nào cũng kết thúc trước từ sau một chút."""
    tong = sum(len(w) + 1 for w in words)
    out, t = [], t0
    for w in words:
        rong = (t1 - t0) * (len(w) + 1) / tong
        out.append((t, t + rong * 0.92))
        t += rong
    return out


def can_chinh(script_words: list[str], asr: list[dict], duration: float) -> tuple[list[dict], float]:
    """Gán mốc cho từng từ kịch bản: từ khớp lấy mốc phiên âm; khối khác nhau (vd số '500.000' so với 'năm trăm nghìn')
    lấy khoảng của khối phiên âm; từ không có trong phiên âm nội suy giữa hai neo. Trả (từ, tỉ lệ khớp thẳng)."""
    a, b = [_norm(w) for w in script_words], [_norm(x["text"]) for x in asr]
    t: list[tuple[float, float] | None] = [None] * len(a)
    khop = 0
    for tag, i0, i1, j0, j1 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag == "equal":
            khop += i1 - i0
            for k in range(i1 - i0):
                t[i0 + k] = (asr[j0 + k]["start"], asr[j0 + k]["end"])
        elif tag == "replace":
            t[i0:i1] = _chia_deu(script_words[i0:i1], asr[j0]["start"], asr[j1 - 1]["end"])
    i = 0
    while i < len(t):  # các đoạn chưa có mốc: nội suy giữa từ có mốc liền trước và liền sau
        if t[i] is not None:
            i += 1
            continue
        j = i
        while j < len(t) and t[j] is None:
            j += 1
        t0 = t[i - 1][1] if i else 0.0
        t1 = t[j][0] if j < len(t) else duration
        t[i:j] = _chia_deu(script_words[i:j], t0, max(t1, t0))
        i = j
    out, prev = [], 0.0
    for w, (s, e) in zip(script_words, t):
        s = min(max(s, prev), duration)  # mốc không lùi, không vượt độ dài tiếng
        e = min(max(e, s), duration)
        out.append({"w": w, "start": round(s, 3), "end": round(e, 3)})
        prev = s
    return out, khop / max(len(a), 1)


def build_timing(script_md: str, asr: list[dict], duration: float) -> tuple[dict, float]:
    paras = [p.split() for p in tts.spoken_paragraphs(script_md)]
    words, khop = can_chinh([w for p in paras for w in p], asr, duration)
    ranges, k = [], 0
    for i, p in enumerate(paras):
        ranges.append({"i": i, "start": 0.0 if i == 0 else words[k]["start"]})
        k += len(p)
    for r, nxt in zip(ranges, ranges[1:] + [{"start": duration}]):
        r["end"] = nxt["start"]
    return {"duration": duration, "words": words, "paragraphs": ranges}, khop


def _giay(ts: str) -> float:
    h, m, s = ts.replace(",", ".").split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def tu_srt(srt_text: str) -> list[dict]:
    """Phụ đề .srt → danh sách từ; từ trong mỗi cue được rải đều theo số ký tự (mốc chỉ chính xác ở mức cue)."""
    out = []
    for block in re.split(r"\n\s*\n", srt_text.strip()):
        m = re.search(r"(\d+:\d+:\d+[,.]\d+)\s*-->\s*(\d+:\d+:\d+[,.]\d+)\s*\n(.+)", block, re.S)
        if not m:
            continue
        ws = m.group(3).split()
        for w, (s, e) in zip(ws, _chia_deu(ws, _giay(m.group(1)), _giay(m.group(2)))):
            out.append({"text": w, "start": round(s, 3), "end": round(e, 3)})
    return out


def _phien_am(audio, ngon_ngu: str = "vi", model: str = "small", run=subprocess.run) -> list[dict]:
    """Phiên âm bằng `hyperframes transcribe` (whisper đa ngôn ngữ; lần đầu tải mô hình ~466 MB cho `small`)."""
    with tempfile.TemporaryDirectory() as tmp:
        run(["npx", "--no-install", "hyperframes", "transcribe", str(Path(audio).resolve()), "--model", model,
             "--language", ngon_ngu, "--dir", tmp], cwd=PIPE, check=True)
        found = next(Path(tmp).rglob("transcript.json"), None)
        if found is None:
            raise RuntimeError("hyperframes transcribe không tạo transcript.json")
        data = json.loads(found.read_text(encoding="utf-8"))
    ws = data if isinstance(data, list) else data.get("words", [])
    return [{"text": w.get("text", w.get("word", "")), "start": w["start"], "end": w["end"]} for w in ws]


def _duration(p: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def _ghep(audios: list[str], out: Path) -> None:
    """Một hoặc nhiều tệp tiếng (theo thứ tự) → một giong.mp3 128k (mã hoá lại để mốc không lệch)."""
    cmd = ["ffmpeg", "-v", "error", "-y"]
    if len(audios) == 1:
        cmd += ["-i", str(Path(audios[0]).resolve())]
    else:
        lst = out.with_name("giong-ghep.txt")
        lst.write_text("".join(f"file '{Path(a).resolve()}'\n" for a in audios))
        cmd += ["-f", "concat", "-safe", "0", "-i", str(lst)]
    subprocess.run(cmd + ["-c:a", "libmp3lame", "-b:a", "128k", str(out)], check=True)


def main(video_dir: str, audios: list[str], srt: str | None = None, phien_am=None) -> int:
    d = Path(video_dir)
    _ghep(audios, d / "giong.mp3")
    dur = _duration(d / "giong.mp3")
    asr = tu_srt(Path(srt).read_text(encoding="utf-8")) if srt else (phien_am or _phien_am)(d / "giong.mp3")
    if not asr:
        print("Không lấy được từ nào từ tiếng/phụ đề")
        return 1
    timing, khop = build_timing((d / "kich-ban.md").read_text(encoding="utf-8"), asr, dur)
    print(f"Giọng {dur:.1f} s, {len(timing['words'])} từ kịch bản, khớp trực tiếp {khop:.0%}")
    if khop < MIN_KHOP:
        print(f"Chỉ khớp {khop:.0%} (< {MIN_KHOP:.0%}): tệp tiếng có vẻ không phải kịch bản này, chưa ghi giong-timing.json")
        return 1
    (d / "giong-timing.json").write_text(json.dumps(timing, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    srt = args[args.index("--srt") + 1] if "--srt" in args else None
    files = [a for i, a in enumerate(args[1:], 1) if a != "--srt" and (i < 2 or args[i - 1] != "--srt")]
    sys.exit(main(args[0], files, srt=srt))
