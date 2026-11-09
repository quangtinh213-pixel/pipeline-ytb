"""Giọng đọc bằng VieNeu-TTS chạy ngay trong máy (không tốn tiền, không cần khoá) → giong.mp3 + giong-timing.json.

Mỗi CÂU là một đơn vị tổng hợp: biết chính xác độ dài từng câu nên mốc từng từ chỉ sai trong phạm vi một câu
(từ rải đều theo số ký tự). Không cần whisper. Câu đã làm thì không làm lại (tên tệp theo nội dung + giọng).
Chạy: uv run python -m tttc.giong_vieneu ../videos/<slug>
      uv run python -m tttc.giong_vieneu nghe-thu <thư mục ra> "Hải Đăng" "Thiện Minh" ...
"""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

from tttc import tts
from tttc.giong_tay import _chia_deu

PIPE = Path(__file__).resolve().parent.parent
CONFIG, WORKER = PIPE / "config.json", PIPE / "scripts" / "vieneu_worker.py"
DEFAULT = {"python": "~/Documents/VieNeu-TTS/.venv/bin/python", "voice": "Hải Đăng", "pause_cau": 0.25,
           "pause_doan": 0.5, "toc_do": 1.0, "phat_am": {}}  # toc_do: hệ số tốc độ (0,9 = chậm 10%)
CAT_LANG = "silenceremove=start_periods=1:start_silence=0.03:start_threshold=-50dB"  # cắt lặng đầu; đảo chiều để cắt lặng cuối


def cau(paragraph: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.!?…])\s+", paragraph.strip()) if s]


def _ten(text: str, voice: str) -> str:
    return hashlib.sha1(f"{text}|{voice}".encode()).hexdigest()[:10]


def _cfg(cfg: dict | None) -> dict:
    return {**DEFAULT, **(cfg if cfg is not None else json.loads(CONFIG.read_text(encoding="utf-8")).get("vieneu", {}))}


def _phat_am(text: str, cfg: dict) -> str:
    for k, v in cfg["phat_am"].items():  # chỉ đổi chữ gửi cho giọng đọc; mốc từ vẫn theo chữ kịch bản
        text = re.sub(rf"(?<!\w){re.escape(k)}(?!\w)", v, text)
    return text


def _tao_wav(jobs: list[dict], work: Path, cfg: dict, run) -> None:
    jobs = [j for j in jobs if not Path(j["out"]).exists()]
    if not jobs:
        return
    jf = work / "jobs.json"
    jf.write_text(json.dumps(jobs, ensure_ascii=False), encoding="utf-8")
    run([str(Path(cfg["python"]).expanduser()), str(WORKER), "--jobs", str(jf)], check=True)


def _duration(p: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def _cat_nghi(src: Path, out: Path, nghi: float, toc_do: float = 1.0) -> None:
    tempo = f"atempo={toc_do}," if toc_do != 1.0 else ""
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-af",
                    f"{CAT_LANG},areverse,{CAT_LANG},areverse,{tempo}apad=pad_dur={nghi}", str(out)], check=True)


def synthesize(video_dir, cfg: dict | None = None, run=subprocess.run) -> None:
    d, cfg = Path(video_dir), _cfg(cfg)
    voice = cfg["voice"]
    paras = [cau(p) for p in tts.spoken_paragraphs((d / "kich-ban.md").read_text(encoding="utf-8"))]
    raw = d / "giong-vieneu"
    raw.mkdir(exist_ok=True)
    units = [(pi, k == len(p) - 1, s) for pi, p in enumerate(paras) for k, s in enumerate(p)]
    for _, _, s in units:
        if re.search(r"\d", s):
            print(f"Cảnh báo: câu có chữ số, nên viết thành chữ để giọng đọc đúng: {s[:70]!r}")
    _tao_wav([{"text": _phat_am(s, cfg), "out": str(raw / f"{_ten(s, voice)}.wav"), "voice": voice}
              for _, _, s in {u[2]: u for u in units}.values()], raw, cfg, run)
    words, ranges, offset, files = [], [], 0.0, []
    for k, (pi, cuoi_doan, s) in enumerate(units):
        nghi = cfg["pause_doan"] if cuoi_doan else cfg["pause_cau"]
        out, goc = raw / f"u{k:04}.wav", raw / f"{_ten(s, voice)}.wav"
        _cat_nghi(goc, out, nghi, cfg["toc_do"])
        try:
            dur = _duration(out)
        except ValueError:
            dur = 0.0
        if dur - nghi < 0.15:  # câu không ra tiếng (vd dòng '---'): xoá để lần sau làm lại, báo rõ câu nào
            goc.unlink(missing_ok=True)
            out.unlink(missing_ok=True)
            raise RuntimeError(f"VieNeu không tạo được tiếng cho câu: {s!r}")
        if not ranges or ranges[-1]["i"] != pi:
            ranges.append({"i": pi, "start": 0.0 if pi == 0 else round(offset, 3)})
        ws = s.split()
        words += [{"w": w, "start": round(a, 3), "end": round(b, 3)}
                  for w, (a, b) in zip(ws, _chia_deu(ws, offset, offset + dur - nghi))]
        offset += dur
        files.append(out)
    lst = raw / "list.txt"
    lst.write_text("".join(f"file '{f.resolve()}'\n" for f in files))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c:a", "libmp3lame",
                    "-b:a", "128k", str(d / "giong.mp3")], check=True)
    total = _duration(d / "giong.mp3")
    for r, nxt in zip(ranges, ranges[1:] + [{"start": total}]):
        r["end"] = nxt["start"]
    (d / "giong-timing.json").write_text(json.dumps({"duration": total, "words": words, "paragraphs": ranges},
                                                    ensure_ascii=False, indent=1), encoding="utf-8")


def audition(out_dir, voices: list[str], text: str = tts.AUDITION_TEXT, cfg: dict | None = None,
             run=subprocess.run) -> list[Path]:
    """Đọc cùng một đoạn bằng nhiều giọng để nghe thử; mỗi giọng ra out_dir/<giọng>.mp3."""
    cfg, out = _cfg(cfg), Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    jobs = [{"text": _phat_am(text, cfg), "out": str(out / f"{v}.wav"), "voice": v} for v in voices]
    _tao_wav(jobs, out, cfg, run)
    files = []
    for v in voices:
        mp3 = out / f"{v}.mp3"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(out / f"{v}.wav"), "-c:a", "libmp3lame", "-b:a", "128k",
                        str(mp3)], check=True)
        files.append(mp3)
    return files


if __name__ == "__main__":
    if sys.argv[1] == "nghe-thu":
        print("\n".join(map(str, audition(sys.argv[2], sys.argv[3:]))))
    else:
        synthesize(sys.argv[1])
