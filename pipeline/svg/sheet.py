"""Bảng soi thư viện SVG: mỗi hình một ô kèm tên tệp. Dùng qlmanage (macOS) hoặc Playwright (Windows/Linux) để vẽ SVG.
Chạy: uv run python svg/sheet.py  → svg/thu-vien.png (không đưa lên git)
"""
import shutil
import subprocess
import sys
import tempfile
from html import escape
from pathlib import Path

from PIL import Image, ImageDraw

TILE_W, TILE_H, IMG = 240, 260, 220


def _rasterize(files: list[Path], tmp: Path) -> None:
    if not files:
        return
    if shutil.which("qlmanage"):
        subprocess.run(["qlmanage", "-t", "-s", str(IMG), "-o", str(tmp), *map(str, files)],
                       check=True, capture_output=True)
        return
    from playwright.sync_api import sync_playwright

    imgs = "".join(
        f'<img id="s{k}" src="{escape(f.resolve().as_uri())}" '
        f'style="width:{IMG}px;height:{IMG}px;object-fit:contain;display:block">'
        for k, f in enumerate(files)
    )
    html_file = tmp / "_sheet.html"
    html_file.write_text(
        f"<!doctype html><html><body style='margin:0;background:transparent'>{imgs}</body></html>",
        encoding="utf-8",
    )
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            page = browser.new_page(viewport={"width": IMG + 40, "height": IMG + 40})
            page.goto(html_file.as_uri(), wait_until="load")
            for k, f in enumerate(files):
                page.locator(f"#s{k}").screenshot(path=str(tmp / f"{f.name}.png"), omit_background=True)
        finally:
            browser.close()


def sheet(svg_dir, out_png, cot: int = 8) -> Path:
    files = sorted(Path(svg_dir).glob("*.svg"))
    rows = -(-len(files) // cot)
    img = Image.new("RGB", (cot * TILE_W, rows * TILE_H), (251, 246, 236))
    d = ImageDraw.Draw(img)
    with tempfile.TemporaryDirectory() as tmp:
        _rasterize(files, Path(tmp))
        for k, f in enumerate(files):
            x, y = (k % cot) * TILE_W, (k // cot) * TILE_H
            png = Path(tmp) / f"{f.name}.png"
            if png.exists():
                t = Image.open(png).convert("RGBA")
                img.paste(t, (x + (TILE_W - t.width) // 2, y + 6), t)
            d.text((x + 10, y + IMG + 14), f.stem, fill=(17, 17, 17))
    out = Path(out_png)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    return out


if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    print(sheet(here, sys.argv[1] if len(sys.argv) > 1 else here / "thu-vien.png"))
