"""Chuẩn hóa mức các tệp hiệu ứng âm thanh (am-thanh/sfx/*.mp3) để gain trong dung.sfx_events (0,18–0,45) nghe đều nhau.

Đỉnh về DINH dBFS, nhưng không để độ to trung bình vượt TB_MAX dB (tiếng bass kéo dài sẽ lấn giọng). Chạy lại an toàn:
tệp đã đạt (lệch < 0,5 dB) thì bỏ qua, không mã hóa lại.
Chạy: uv run python -m tttc.chuan_sfx            (nghiên cứu đối thủ 14/11/2026, P2)
"""
import re
import subprocess
import sys
from pathlib import Path

SFX = Path(__file__).resolve().parent.parent / "am-thanh" / "sfx"
DINH, TB_MAX, BO_QUA = -3.0, -18.0, 0.5


def do_muc(p: Path) -> tuple[float, float]:
    """(độ to trung bình, đỉnh) dB của tệp."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(p), "-af", "volumedetect", "-f", "null", "-"],
                       capture_output=True, text=True, check=True)
    tb, dinh = (float(re.search(rf"{k}_volume: (-?[\d.]+) dB", r.stderr).group(1)) for k in ("mean", "max"))
    return tb, dinh


def do_loi(tb: float, dinh: float) -> float:
    """dB cần cộng: đưa đỉnh về DINH, nhưng giảm thêm nếu trung bình sẽ vượt TB_MAX."""
    return min(DINH - dinh, TB_MAX - tb)


def chuan_hoa(thu_muc: Path = SFX) -> list[tuple[str, float]]:
    out = []
    for p in sorted(Path(thu_muc).glob("*.mp3")):
        g = do_loi(*do_muc(p))
        if abs(g) < BO_QUA:
            continue
        tmp = p.with_suffix(".tmp.mp3")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(p), "-af", f"volume={g:.2f}dB",
                        "-c:a", "libmp3lame", "-q:a", "2", str(tmp)], check=True)
        tmp.replace(p)
        out.append((p.name, round(g, 2)))
    return out


if __name__ == "__main__":
    for ten, g in chuan_hoa(Path(sys.argv[1]) if len(sys.argv) > 1 else SFX):
        print(f"{ten}: {g:+.2f} dB")
