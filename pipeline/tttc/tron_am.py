"""Trộn nhạc nền vào giọng đọc: nhạc tự hạ khi có tiếng, nổi lên ở chỗ lặng (sidechain), vừa độ dài giọng."""
import subprocess
from pathlib import Path


def _duration(p: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def tron(giong: Path, nhac: Path, out: Path, ha_db: float = -20.0, vao: float = 1.0, ra: float = 2.0) -> Path:
    """out dài đúng bằng giong. Nhạc nền ở ha_db + 8 dB lúc lặng; có tiếng thì bị nén thêm ~9 dB, tức khoảng ha_db.
    Ngưỡng 0.003 đo bằng sin −20 dBFS (mức giọng nói thường): ngưỡng cao hơn (0.03) không nén được gì."""
    dur = _duration(Path(giong))
    flt = (f"[1:a]atrim=duration={dur:.3f},asetpts=PTS-STARTPTS,volume={ha_db + 8}dB,"
           f"afade=t=in:d={vao},afade=t=out:st={max(dur - ra, 0):.3f}:d={ra}[m];"
           "[0:a]asplit=2[v][sc];"
           "[m][sc]sidechaincompress=threshold=0.003:ratio=6:attack=20:release=600:makeup=1[duck];"
           "[v][duck]amix=inputs=2:duration=first:normalize=0[o]")
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(giong), "-stream_loop", "-1", "-i", str(nhac),
                    "-filter_complex", flt, "-map", "[o]", "-t", f"{dur:.3f}", "-c:a", "libmp3lame", "-b:a", "128k",
                    str(out)], check=True)
    return out
