"""Kiểm tương phản phụ đề từ khung hình của video đã render: mỗi cảnh lấy một khung giữa cảnh, đo dải phụ đề.

Chạy: uv run python -m tttc.tuong_phan ../videos/<slug>   (cần final.mp4 và canh.json; chỉ cảnh báo)
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

from tttc import theme

VUNG = (210, 960, 1710, 1044)  # dải phụ đề ở khung 1920×1080 (bottom 36 px, chữ 44 px, rộng tối đa 1500 px)


def ti_le(png, vung: tuple[int, int, int, int] = VUNG) -> float:
    """Tương phản WCAG giữa độ sáng phân vị 95 và phân vị 5 trong vùng (x0, y0, x1, y1) của ảnh."""
    hist = Image.open(png).convert("L").crop(vung).histogram()
    tong = sum(hist)

    def phan_vi(p: float) -> int:
        dem = 0
        for v, n in enumerate(hist):
            dem += n
            if dem >= p * tong:
                return v
        return 255

    gray = lambda v: f"#{v:02x}{v:02x}{v:02x}"
    return theme.contrast(gray(phan_vi(0.95)), gray(phan_vi(0.05)))


def kiem_phu_de(video_mp4, canh: dict, nguong: float = 4.5, vung=VUNG, run=subprocess.run) -> list[str]:
    out = []
    with tempfile.TemporaryDirectory() as tmp:
        for c in canh["scenes"]:
            png = Path(tmp) / f"{c['id']}.png"
            run(["ffmpeg", "-v", "error", "-y", "-ss", f"{(c['start'] + c['end']) / 2:.3f}", "-i", str(video_mp4),
                 "-frames:v", "1", str(png)], check=True)
            t = ti_le(png, vung)
            if 1.02 < t < nguong:  # dải đồng nhất (t ≈ 1) là khung không có phụ đề, không phải phụ đề khó đọc
                out.append(f"Cảnh báo: cảnh {c['id']} phụ đề khó đọc (tương phản {t:.1f}:1, chuẩn ≥ {nguong})")
    return out


def main(video_dir: str) -> int:
    d = Path(video_dir)
    canh = json.loads((d / "canh.json").read_text(encoding="utf-8"))
    msgs = kiem_phu_de(d / "final.mp4", canh, run=subprocess.run)
    for m in msgs:
        print("-", m)
    print(f"{len(msgs)} cảnh báo trên {len(canh['scenes'])} cảnh")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
