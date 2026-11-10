"""Chụp trang web cho cảnh trang-nguon: ảnh đúng tỉ lệ vùng trang của mẫu (1520×820) + khung tô quanh câu trích.

Chạy: uv run python -m tttc.chup <url> ../videos/<slug>/nguon/<id>.png ["câu trích nguyên văn"]
In ra khung "x,y,w,h" (% ảnh) để ghi vào canh.khung. Lần đầu: uv run playwright install chromium
"""
import sys
from pathlib import Path

W, H = 1520, 820  # vùng trang trong templates/canh/trang-nguon.html
# bỏ thanh dính, banner cookie, quảng cáo nổi: mọi thứ fixed/sticky và iframe
DON = """() => document.querySelectorAll('body *').forEach(e => {
  if (e.tagName === 'IFRAME' || ['fixed', 'sticky'].includes(getComputedStyle(e).position)) e.remove(); })"""


def khung(box: dict, le: float = 12, w: int = W, h: int = H) -> str:
    """Hộp chữ (px, theo khung nhìn) → "x,y,w,h" theo %, nới lề và cắt trong ảnh."""
    x0, y0 = max(box["x"] - le, 0), max(box["y"] - le, 0)
    x1, y1 = min(box["x"] + box["width"] + le, w), min(box["y"] + box["height"] + le, h)
    if x1 <= x0 or y1 <= y0:
        raise ValueError("Câu trích nằm ngoài khung chụp")
    return ",".join(f"{v:.1f}" for v in (x0 / w * 100, y0 / h * 100, (x1 - x0) / w * 100, (y1 - y0) / h * 100))


def chup(url: str, out, cau: str = "") -> str:
    from playwright.sync_api import sync_playwright
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=2, locale="vi-VN")
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(2500)  # ảnh và phông chữ tải xong
        page.evaluate(DON)
        k = "0,0,0,0"
        if cau:
            # shortcut: chỉ khớp câu nằm gọn trong một phần tử; câu vắt qua thẻ <b>/<a> thì rút ngắn câu trích
            loc = page.get_by_text(cau).first
            if not loc.count():
                b.close()
                raise ValueError(f"Không thấy câu trích trên trang: {cau!r}")
            loc.evaluate("e => e.scrollIntoView({block: 'center'})")
            k = khung(loc.bounding_box())
        page.screenshot(path=str(out))
        b.close()
    return k


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    print(chup(*sys.argv[1:4]))
