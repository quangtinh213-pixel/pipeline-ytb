"""Trộn nhạc nền vào giọng đọc: nhạc tự hạ khi có tiếng, nổi lên ở chỗ lặng (sidechain), vừa độ dài giọng,
tổng ra đúng mức YouTube (docs/nghien-cuu/cach-doi-thu-dung-video-2026-11-14.md mục 6, P0 âm thanh)."""
import re
import subprocess
from pathlib import Path


def _duration(p: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def lufs(p: Path) -> float:
    """Độ to tích hợp (LUFS, EBU R128) của cả tệp."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(p), "-af", "ebur128", "-f", "null", "-"],
                       capture_output=True, text=True, check=True)
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)[-1])


def tron(giong: Path, nhac: Path, out: Path, tong_lufs: float = -14.0, nhac_db: float = -13.0,
         vao: float = 1.0, ra: float = 2.0) -> Path:
    """out dài đúng bằng giong. Giọng được khuếch đại về tong_lufs; nhạc chuẩn hóa về tong_lufs + nhac_db ở chỗ lặng
    (tệp nhạc gốc to nhỏ thế nào cũng vậy), có tiếng thì nén nhẹ thêm (ratio 3, release 220 ms để kịp hồi trong quãng
    nghỉ câu), tức nhạc dưới giọng ~16–18 dB. Đỉnh chặn ở −2 dBFS.
    Ngưỡng 0.003 đo bằng sin −20 dBFS (mức giọng nói thường): ngưỡng cao hơn (0.03) không nén được gì."""
    dur = _duration(Path(giong))
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)

    def ve(tang: float) -> float:
        # shortcut: loudnorm một lượt cho nhánh nhạc (lệch ±1 LU), đủ cho nền ambient; nhạc có nhịp mạnh thì đo hai lượt
        flt = (f"[1:a]atrim=duration={dur:.3f},asetpts=PTS-STARTPTS,loudnorm=I={tong_lufs + nhac_db}:TP=-6,"
               f"afade=t=in:d={vao},afade=t=out:st={max(dur - ra, 0):.3f}:d={ra}[m];"
               f"[0:a]volume={tang:.2f}dB,asplit=2[v][sc];"
               "[m][sc]sidechaincompress=threshold=0.003:ratio=3:attack=15:release=220:makeup=1[duck];"
               "[v][duck]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.794:level=0[o]")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(giong), "-stream_loop", "-1", "-i", str(nhac),
                        "-filter_complex", flt, "-map", "[o]", "-t", f"{dur:.3f}", "-ar", "44100",
                        "-c:a", "libmp3lame", "-b:a", "128k", str(out)], check=True)
        return lufs(out)

    tang = tong_lufs - lufs(giong)
    do = ve(tang)
    if abs(do - tong_lufs) > 0.5:  # bộ chặn đỉnh ăn bớt độ to khi giọng nhiều đỉnh nhọn: bù một lượt
        ve(tang + tong_lufs - do)
    return out
