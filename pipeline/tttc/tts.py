"""Giọng đọc ElevenLabs có timestamp từng ký tự → giong.mp3 + giong-timing.json."""
import base64
import hashlib
import json
import re
import subprocess
import sys
import time
import unicodedata
from pathlib import Path

import requests

API = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps?output_format=mp3_44100_128"
CONFIG = Path(__file__).resolve().parent.parent / "config.json"
SPOKEN = re.compile(r"\*\*Lời đọc:?\*\*:?")
TAG = re.compile(r"\[#[\w-]+\]")
VOICE_KEYS = ("stability", "similarity_boost", "style")  # tuỳ chọn trong config.elevenlabs; không đặt thì ElevenLabs dùng mặc định
AUDITION_TEXT = ("Gói ChatGPT Plus giá năm trăm hai mươi hai nghìn năm trăm đồng mỗi tháng. Con chip của Viettel làm "
                 "trên tiến trình hai mươi tám nanomet, còn TSMC đã sản xuất hàng loạt hai nanomet từ cuối năm ngoái. "
                 "Theo Reuters và Bloomberg, Nvidia không có nhà máy nào, Apple cũng vậy. Nói thật là đọc giá xong mình "
                 "phải đếm lại số không mấy lần. Các bạn đoán thử xem, chuyện này kết thúc thế nào?")
_sleep = time.sleep


def _nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def spoken_paragraphs(script_md: str, keep_tags: bool = False) -> list[str]:
    paras, on = [], False
    for line in _nfc(script_md).splitlines():
        s = line.strip()
        if re.fullmatch(r"[-*_]{3,}", s):  # đường kẻ ngang giữa các beat không phải lời đọc
            on = False
            continue
        m = SPOKEN.search(s)
        if m:
            on, s = True, s[m.end():]
        elif s.startswith("#") or "[TRÊN MÀN HÌNH]" in s or s.startswith("* **"):
            on = False
            continue
        if on:
            s = re.sub(r"\s+", " ", (s if keep_tags else TAG.sub("", s)).replace("*", "")).strip()
            if s:
                paras.append(s)
    return paras


def words_from_alignment(alignment: dict, offset: float) -> list[dict]:
    words, cur, start, end = [], "", 0.0, 0.0
    chars = alignment["characters"]
    starts, ends = alignment["character_start_times_seconds"], alignment["character_end_times_seconds"]
    for c, s, e in zip(chars, starts, ends):
        if c.isspace():
            if cur:
                words.append({"w": _nfc(cur), "start": offset + start, "end": offset + end})
            cur = ""
            continue
        if not cur:
            start = s
        cur, end = cur + c, e
    if cur:
        words.append({"w": _nfc(cur), "start": offset + start, "end": offset + end})
    return words


def _duration(p: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(p)], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def seg_name(i: int, text: str, cfg: dict) -> str:
    """Tên tệp theo nội dung + cấu hình giọng: sửa câu thì gọi lại, không sửa thì không tốn tiền."""
    extra = [f"{k}={cfg[k]}" for k in VOICE_KEYS if k in cfg]  # đổi thông số giọng thì tổng hợp lại
    h = hashlib.sha1("|".join([text, cfg["voice_id"], cfg["model_id"], str(cfg["speed"]), *extra]).encode()).hexdigest()
    return f"doan-{i:03}-{h[:8]}"


def _call(post, key: str, cfg: dict, text: str, prev: str, nxt: str) -> dict:
    body = {"text": text, "model_id": cfg["model_id"], "voice_settings": {"speed": cfg["speed"], **{k: cfg[k] for k in VOICE_KEYS if k in cfg}},
            "previous_text": prev, "next_text": nxt}
    for attempt in range(3):
        r = post(API.format(voice_id=cfg["voice_id"]), headers={"xi-api-key": key}, json=body, timeout=120)
        if r.status_code == 429 or r.status_code >= 500:
            _sleep(2 ** attempt * 2)
            continue
        r.raise_for_status()
        return r.json()
    raise RuntimeError(f"ElevenLabs lỗi {r.status_code} sau 3 lần: {text[:40]}")


def _cfg_key(cfg: dict | None, key: str | None) -> tuple[dict, str]:
    cfg = cfg or json.loads(CONFIG.read_text(encoding="utf-8"))["elevenlabs"]
    if key is None:
        import keyring
        key = keyring.get_password("tui-tien-cong-nghe", "elevenlabs")
        if not key:
            raise RuntimeError("Chưa có khoá ElevenLabs trong Keychain (service tui-tien-cong-nghe)")
    return cfg, key


def audition(text: str, voice_ids: list[str], out_dir, post=requests.post, key: str | None = None,
             cfg: dict | None = None) -> list[Path]:
    """Đọc cùng một đoạn bằng nhiều giọng để nghe thử và chọn voice_id; mỗi giọng ra out_dir/<voice_id>.mp3."""
    cfg, key = _cfg_key(cfg, key)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    files = []
    for vid in voice_ids:
        res = _call(post, key, dict(cfg, voice_id=vid), text, "", "")
        files.append(out / f"{vid}.mp3")
        files[-1].write_bytes(base64.b64decode(res["audio_base64"]))
    return files


def synthesize(video_dir, post=requests.post, key: str | None = None, cfg: dict | None = None) -> None:
    d = Path(video_dir)
    cfg, key = _cfg_key(cfg, key)
    paras = spoken_paragraphs((d / "kich-ban.md").read_text(encoding="utf-8"))
    out = d / "giong"
    out.mkdir(exist_ok=True)
    names = [seg_name(i, t, cfg) for i, t in enumerate(paras)]
    for i, text in enumerate(paras):
        mp3, js = out / f"{names[i]}.mp3", out / f"{names[i]}.json"
        if mp3.exists() and js.exists():
            continue  # đã trả tiền cho đoạn này, không gọi lại
        res = _call(post, key, cfg, text, paras[i - 1] if i else "", paras[i + 1] if i + 1 < len(paras) else "")
        mp3.write_bytes(base64.b64decode(res["audio_base64"]))
        js.write_text(json.dumps(res["alignment"], ensure_ascii=False), encoding="utf-8")

    words, ranges, offset = [], [], 0.0
    for i in range(len(paras)):
        dur = _duration(out / f"{names[i]}.mp3")
        align = json.loads((out / f"{names[i]}.json").read_text(encoding="utf-8"))
        words += words_from_alignment(align, offset)
        ranges.append({"i": i, "start": offset, "end": offset + dur})
        offset += dur
    lst = out / "list.txt"
    lst.write_text("".join(f"file '{n}.mp3'\n" for n in names))
    # mã hoá lại khi nối: '-c copy' giữ phần đệm của từng mp3, lệch ~40 ms mỗi chỗ nối
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
                    "-c:a", "libmp3lame", "-b:a", "128k", str(d / "giong.mp3")], check=True)
    timing = {"duration": _duration(d / "giong.mp3"), "words": words, "paragraphs": ranges}
    (d / "giong-timing.json").write_text(json.dumps(timing, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    if sys.argv[1] == "audition":  # uv run python -m tttc.tts audition <thư mục ra> <voice_id>...
        print("\n".join(map(str, audition(AUDITION_TEXT, sys.argv[3:], sys.argv[2]))))
    else:
        synthesize(sys.argv[1])
