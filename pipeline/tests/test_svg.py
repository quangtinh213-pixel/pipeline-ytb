import re
from pathlib import Path

import pytest

from tttc import theme

SVG_DIR = Path(__file__).resolve().parent.parent / "svg"


@pytest.mark.parametrize("path", sorted(SVG_DIR.glob("*.svg")), ids=lambda p: p.stem)
def test_svg_content_inside_viewbox(path):
    s = path.read_text(encoding="utf-8")
    vx, vy, vw, vh = map(float, re.search(r'viewBox="([^"]+)"', s).group(1).split())
    for m in re.finditer(r'points="([^"]+)"', s):
        for pair in m.group(1).split():
            x, y = map(float, pair.split(","))
            assert vx <= x <= vx + vw and vy <= y <= vy + vh, f"{path.stem}: điểm ({x}, {y}) nằm ngoài viewBox"


BRAND = theme.brand_colors()  # bảng màu thư viện lấy từ brand/theme.json
EXTRA = {"cay": {"#5A4426", "#6E5430", "#8A6A3A"}, "co-viet-nam": {"#A51B15", "#DA251D"},
         "nen-dat": {"#141414", "#1A1A1A", "#262626", "#2F2F2F", "#3A3A3A"}}


@pytest.mark.parametrize("path", sorted(SVG_DIR.glob("*.svg")), ids=lambda p: p.stem)
def test_every_svg_follows_library_rules(path):
    s = path.read_text(encoding="utf-8")
    assert "<text" not in s, "không chữ trong SVG"
    vx, vy, vw, vh = map(float, re.search(r'viewBox="([^"]+)"', s).group(1).split())
    assert abs(vw - vh) < 0.2, "viewBox phải vuông"
    assert path.stat().st_size <= 20_000
    colors = {c.upper() for c in re.findall(r"#[0-9A-Fa-f]{6}", s)}
    assert colors <= BRAND | EXTRA.get(path.stem, set()), f"màu ngoài bảng: {colors - BRAND - EXTRA.get(path.stem, set())}"


def test_library_has_at_least_55_shapes():
    assert len(list(SVG_DIR.glob("*.svg"))) >= 55


def test_sheet_makes_one_tile_per_svg(tmp_path):
    import shutil
    if shutil.which("qlmanage") is None:
        pytest.skip("cần qlmanage của macOS")
    from PIL import Image
    d = tmp_path / "svg"
    d.mkdir()
    for n in ("chip", "tien", "cay"):
        shutil.copy(SVG_DIR / f"{n}.svg", d / f"{n}.svg")
    sys_path = str(SVG_DIR)
    import sys
    sys.path.insert(0, sys_path)
    import sheet
    out = sheet.sheet(d, tmp_path / "s.png", cot=2)
    assert Image.open(out).size == (2 * 240, 2 * 260)  # 3 hình, 2 cột → 2 hàng
