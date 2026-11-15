"""Giọng đọc bằng VieNeu-TTS chạy ngay trong máy (không tốn tiền, không cần khoá) → giong.mp3 + giong-timing.json.

Mỗi CÂU là một đơn vị tổng hợp: biết chính xác độ dài từng câu nên mốc từng từ chỉ sai trong phạm vi một câu
(từ rải đều theo số ký tự). Không cần whisper. Câu đã làm thì không làm lại (tên tệp theo nội dung + giọng).
Chạy: uv run python -m tttc.giong_vieneu ../videos/<slug>
      uv run python -m tttc.giong_vieneu nghe-thu <thư mục ra> "Hải Đăng" "Thiện Minh" ...
      uv run python -m tttc.giong_vieneu thu-60s <thư mục video>   # nghe-thu.mp3: ~210 từ đầu bằng giọng đã chọn
"""
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from tttc import tts
from tttc.giong_tay import _chia_deu

PIPE = Path(__file__).resolve().parent.parent
CONFIG, WORKER = PIPE / "config.json", PIPE / "scripts" / "vieneu_worker.py"
# Quãng nghỉ rút từ 0,25/0,5 s xuống 0,14/0,32 s (nghiên cứu đối thủ 14/11/2026, P1): lời liền mạch, không hụt hơi giữa câu.
# giong_phu đọc các dòng ">>" (câu hỏi xen của người xem, mỗi 90–150 s) cho nhịp đối thoại.
DEFAULT = {"python": "~/Documents/VieNeu-TTS/.venv/" + ("Scripts/python.exe" if os.name == "nt" else "bin/python"), "voice": "Hải Đăng",
           "giong_phu": "Trúc Ly", "pause_cau": 0.14, "pause_doan": 0.32, "toc_do": 1.0,
           "phat_am": {}}  # toc_do: hệ số tốc độ (0,9 = chậm 10%)
CAT_LANG = "silenceremove=start_periods=1:start_silence=0.03:start_threshold=-50dB"  # cắt lặng đầu; đảo chiều để cắt lặng cuối


def cau(paragraph: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.!?…])\s+", paragraph.strip()) if s]


def _ten(text: str, voice: str) -> str:
    return hashlib.sha1(f"{text}|{voice}".encode()).hexdigest()[:10]


def _cfg(cfg: dict | None) -> dict:
    return {**DEFAULT, **(cfg if cfg is not None else json.loads(CONFIG.read_text(encoding="utf-8")).get("vieneu", {}))}


SHORTS = {"pause_cau": 0.10, "pause_doan": 0.10}  # Shorts cắt sát khoảng lặng (video dài 0,14/0,32 s)


def cfg_shorts(cfg: dict | None = None) -> dict:
    """Cấu hình VieNeu cho Short viết riêng: các khóa trong vieneu.shorts ghi đè cấp trên. Dùng: synthesize(d, cfg_shorts())."""
    base = _cfg(cfg)
    return {**{k: v for k, v in base.items() if k != "shorts"}, **SHORTS, **base.get("shorts", {})}


def _phat_am(text: str, cfg: dict) -> str:
    for k, v in sorted(cfg["phat_am"].items(), key=lambda kv: len(kv[0]), reverse=True):  # từ ghép dài trước từ ngắn; chỉ đổi chữ gửi cho giọng đọc
        text = re.sub(rf"(?<!\w){re.escape(k)}(?!\w)", v, text)
    return text


_NGOAI_LAI_F = re.compile(r"[fjwz]", re.I)
_NGOAI_LAI_CAP = re.compile(r"^[A-Z]{2,}$|^[A-Za-z]*[a-z][A-Z][A-Za-z]*$")
_NGOAI_LAI_DUOI = re.compile(r"[bdflrsvz]$", re.I)
_NGOAI_LAI_KEP = re.compile(r"([a-z])\1", re.I)
_DAU_VIET = re.compile(r"[ăâđêôơưàáảãạằắẳẵặầấẩẫậèéẻẽẹềếểễệìíỉĩịòóỏõọồốổỗộờớởỡợùúủũụừứửữựỳýỷỹỵ]", re.I)


def tu_chua_phat_am(paragraphs: list[str], cfg: dict) -> list[str]:
    """Liệt kê từ ngoại lai / viết tắt tiếng Anh chưa có trong phat_am để tác giả bổ sung trước khi đọc."""
    thieu: list[str] = []
    seen: set[str] = set()
    for p in paragraphs:
        da_map = _phat_am(p, cfg)
        for raw in da_map.split():
            tok = raw.strip(".,!?:;\"'()[]{}“”‘’…")
            if len(tok) < 2 or _DAU_VIET.search(tok) or tok.isdigit():
                continue
            la_ngoai = bool(
                _NGOAI_LAI_F.search(tok)
                or _NGOAI_LAI_CAP.match(tok)
                or ("-" in tok and any(ch.isalpha() for ch in tok))
                or (re.fullmatch(r"[A-Za-z]+", tok) and (_NGOAI_LAI_DUOI.search(tok) or _NGOAI_LAI_KEP.search(tok)))
            )
            if la_ngoai and tok.lower() not in seen:
                seen.add(tok.lower())
                thieu.append(tok)
    return thieu


def _chia_theo_nhip(words: list[str], t0: float, t1: float, pause_phay: float = 0.12) -> list[tuple[float, float]]:
    """Rải mốc từng từ vào [t0, t1]; dành thêm khe nghỉ ngắn sau dấu phẩy/chấm phẩy nội câu."""
    if not words:
        return []
    last = len(words) - 1
    ngat = [i for i, w in enumerate(words[:-1]) if w[-1:] in (",", ";", ":")]
    if not ngat:
        return _chia_deu(words, t0, t1)
    dur = max(t1 - t0, 0.0)
    tong_nghi = min(len(ngat) * pause_phay, dur * 0.18)
    moi_nghi = tong_nghi / len(ngat)
    # Tổng trọng số thời gian nói cộng thời gian nghỉ nhẹ sau dấu phẩy
    tong_ky_tu = sum(len(w) + 1 for w in words)
    speech_dur = max(dur - tong_nghi, 0.0)
    out, t = [], t0
    for i, w in enumerate(words):
        rong = speech_dur * (len(w) + 1) / tong_ky_tu
        out.append((t, t + rong * 0.92))
        t += rong + (moi_nghi if i != last and i in ngat else 0.0)
    return out


def _tao_wav(jobs: list[dict], work: Path, cfg: dict, run) -> None:
    jobs = [j for j in jobs if not Path(j["out"]).exists()]
    if not jobs:
        return
    jf = work / "jobs.json"
    jf.write_text(json.dumps(jobs, ensure_ascii=False), encoding="utf-8", newline="\n")
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
    voiced = tts.spoken_voiced((d / "kich-ban.md").read_text(encoding="utf-8"))
    raw_paras = [p for p, _ in voiced]
    thieu_pa = tu_chua_phat_am(raw_paras, cfg)
    if thieu_pa:
        print(f"Cảnh báo phát âm: chưa có trong phat_am: {', '.join(thieu_pa[:10])}")
    paras = [cau(p) for p in raw_paras]
    giong = [cfg["giong_phu"] if phu else cfg["voice"] for _, phu in voiced]
    raw = d / "giong-vieneu"
    raw.mkdir(exist_ok=True)
    units = [(pi, k == len(p) - 1, s, giong[pi]) for pi, p in enumerate(paras) for k, s in enumerate(p)]
    for _, _, s, _ in units:
        if re.search(r"\d", s):
            print(f"Cảnh báo: câu có chữ số, nên viết thành chữ để giọng đọc đúng: {s[:70]!r}")
    _tao_wav([{"text": _phat_am(s, cfg), "out": str(raw / f"{_ten(_phat_am(s, cfg), v)}.wav"), "voice": v}
              for _, _, s, v in {(u[2], u[3]): u for u in units}.values()], raw, cfg, run)
    words, ranges, offset, files = [], [], 0.0, []
    for k, (pi, cuoi_doan, s, voice) in enumerate(units):
        nghi = cfg["pause_doan"] if cuoi_doan else cfg["pause_cau"]
        out, goc = raw / f"u{k:04}.wav", raw / f"{_ten(_phat_am(s, cfg), voice)}.wav"
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
                  for w, (a, b) in zip(ws, _chia_theo_nhip(ws, offset, offset + dur - nghi))]
        offset += dur
        files.append(out)
    lst = raw / "list.txt"
    lst.write_text("".join(f"file '{f.resolve()}'\n" for f in files), encoding="utf-8", newline="\n")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c:a", "libmp3lame",
                    "-b:a", "128k", str(d / "giong.mp3")], check=True)
    total = _duration(d / "giong.mp3")
    for r, nxt in zip(ranges, ranges[1:] + [{"start": total}]):
        r["end"] = nxt["start"]
    (d / "giong-timing.json").write_text(json.dumps({"duration": total, "words": words, "paragraphs": ranges},
                                                    ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")


def nghe_thu(video_dir, so_tu: int = 210, cfg: dict | None = None, run=subprocess.run) -> Path:
    """Đọc thử các câu đầu (cộng dồn đến ≥ so_tu từ) bằng giọng đã chọn → nghe-thu.mp3.
    Dùng đúng tên wav theo câu của synthesize nên câu giữ nguyên sẽ được tái dùng khi tạo giọng đầy đủ."""
    d, cfg = Path(video_dir), _cfg(cfg)
    units, n = [], 0
    for p, phu in tts.spoken_voiced((d / "kich-ban.md").read_text(encoding="utf-8")):
        ss = cau(p)
        for k, s in enumerate(ss):
            units.append((s, k == len(ss) - 1, cfg["giong_phu"] if phu else cfg["voice"]))
            n += len(s.split())
            if n >= so_tu:
                break
        if n >= so_tu:
            break
    raw = d / "giong-vieneu"
    raw.mkdir(exist_ok=True)
    _tao_wav([{"text": _phat_am(s, cfg), "out": str(raw / f"{_ten(_phat_am(s, cfg), v)}.wav"), "voice": v}
              for s, v in dict.fromkeys((s, v) for s, _, v in units)], raw, cfg, run)
    files = []
    for k, (s, cuoi_doan, voice) in enumerate(units):
        out = raw / f"nt{k:03}.wav"
        _cat_nghi(raw / f"{_ten(_phat_am(s, cfg), voice)}.wav", out, cfg["pause_doan"] if cuoi_doan else cfg["pause_cau"], cfg["toc_do"])
        files.append(out)
    lst = raw / "nt-list.txt"
    lst.write_text("".join(f"file '{f.resolve()}'\n" for f in files), encoding="utf-8", newline="\n")
    mp3 = d / "nghe-thu.mp3"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c:a", "libmp3lame",
                    "-b:a", "128k", str(mp3)], check=True)
    return mp3


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
    elif sys.argv[1] == "thu-60s":
        print(nghe_thu(sys.argv[2]))
    else:
        synthesize(sys.argv[1])
