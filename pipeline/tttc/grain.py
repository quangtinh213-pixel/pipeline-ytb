"""Hạt nhiễu mịn chống dải màu (banding) trên nền gradient: PNG xám ngẫu nhiên xác định theo seed.
Phủ lên cảnh bằng CSS `mix-blend-mode: overlay` với độ mờ thấp (config.json: render.grain, ví dụ 0.02);
xám trung bình ≈ 128 nên overlay không đổi độ sáng chung."""
import random
from pathlib import Path

from PIL import Image


def tao_grain(out, size: int = 256, seed: int = 7) -> Path:
    rng = random.Random(seed)
    im = Image.frombytes("L", (size, size), bytes(rng.randrange(256) for _ in range(size * size)))
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out)
    return out
