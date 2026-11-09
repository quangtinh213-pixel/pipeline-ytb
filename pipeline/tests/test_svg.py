import re
from pathlib import Path

import pytest

SVG_DIR = Path(__file__).resolve().parent.parent / "svg"


@pytest.mark.parametrize("path", sorted(SVG_DIR.glob("*.svg")), ids=lambda p: p.stem)
def test_svg_content_inside_viewbox(path):
    s = path.read_text(encoding="utf-8")
    vx, vy, vw, vh = map(float, re.search(r'viewBox="([^"]+)"', s).group(1).split())
    for m in re.finditer(r'points="([^"]+)"', s):
        for pair in m.group(1).split():
            x, y = map(float, pair.split(","))
            assert vx <= x <= vx + vw and vy <= y <= vy + vh, f"{path.stem}: điểm ({x}, {y}) nằm ngoài viewBox"
