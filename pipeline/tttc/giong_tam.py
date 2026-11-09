"""Giọng tạm bằng lệnh `say` của macOS (không tốn tiền, không cần khoá) để chạy thử toàn bộ chuỗi dựng."""
import subprocess
from pathlib import Path


def giong_tam(text: str, out_dir, toc_do: int = 185, giong: str = "Linh") -> dict:
    """Ghi out_dir/giong.mp3 và trả {"duration", "words", "paragraphs": []} cùng định dạng giong-timing.json.
    shortcut: `say` không có mốc từng từ nên chia đều theo số ký tự; giọng ElevenLabs thật có mốc chính xác."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    aiff = out / "g.aiff"
    subprocess.run(["say", "-v", giong, "-r", str(toc_do), "-o", str(aiff), text], check=True)
    mp3 = out / "giong.mp3"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(aiff), "-c:a", "libmp3lame", "-b:a", "128k", str(mp3)],
                   check=True)
    aiff.unlink()
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp3)],
                               capture_output=True, text=True, check=True).stdout)
    ws = text.split()
    words, t, rate = [], 0.0, dur / sum(len(w) + 1 for w in ws)  # mỗi từ chiếm len+1 ký tự (kèm khoảng trắng)
    for w in ws:
        words.append({"w": w, "start": round(t, 3), "end": round(t + len(w) * rate, 3)})
        t += (len(w) + 1) * rate
    return {"duration": dur, "words": words, "paragraphs": []}
