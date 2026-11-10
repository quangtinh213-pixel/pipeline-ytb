"""Tạo logo, avatar và banner của kênh Nhịp Công Nghệ từ brand/theme.json và bộ nhân vật. Chạy: python3 make_brand.py

Kích thước (kiểm 10/11/2026 trên các trang hướng dẫn kích thước YouTube): avatar 800×800 (YouTube cắt tròn; Studio yêu cầu ít nhất 98×98 px, tối đa 4 MB);
banner 2560×1440, vùng an toàn 1546×423 ở giữa (mọi chữ và nhân vật nằm trong vùng này); tệp ≤ 6 MB.
"""
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
TH = json.loads((HERE / "theme.json").read_text(encoding="utf-8"))  # màu thương hiệu một nguồn
BG, BG2, ACC, WHITE, MUTED = TH["nen"], TH["nen_sang"], TH["nhan"][0], TH["muc"], TH["muted"]
FONT = "/System/Library/Fonts/SFNS.ttf"  # SF Pro, có dấu tiếng Việt
NHAN_VAT = HERE.parent / "pipeline" / "nhan-vat"
TEN, DINH_VI, PHU = "Nhịp Công Nghệ", "Tin nóng công nghệ – kinh tế, góc nhìn Việt Nam", "Mọi con số đều dẫn nguồn gốc"


def font(size, weight="Heavy"):
    f = ImageFont.truetype(FONT, size)
    try:
        f.set_variation_by_name(weight)
    except Exception:
        pass  # font không có biến thể thì dùng mặc định
    return f


def vua(d, text, max_w, size, weight="Heavy"):
    """Cỡ chữ lớn nhất ≤ size mà chữ vẫn vừa max_w."""
    while size > 16 and d.textlength(text, font=font(size, weight)) > max_w:
        size -= 4
    return font(size, weight)


def nhan_vat(ten="chao-truoc", cao=500):
    c = Image.open(NHAN_VAT / f"{ten}.png").convert("RGBA")
    return c.resize((int(c.width * cao / c.height), cao), Image.LANCZOS)


def xung(d, x0, x1, y, bien=70, ruot=6, mau=ACC):
    """Đường nhịp (như điện tâm đồ) chạy ngang từ x0 đến x1 tại cao độ y."""
    pts, x = [(x0, y)], x0 + 300
    while x < x1:
        pts += [(x, y), (x + 40, y - bien), (x + 80, y + bien * 0.8), (x + 120, y)]
        x += 560
    d.line(pts + [(x1, y)], fill=mau, width=ruot, joint="curve")


# Avatar 800×800 (cắt tròn: nhân vật nằm gọn trong vòng tròn giữa, đọc được ở 98 px)
av = Image.new("RGB", (800, 800), BG2)
d = ImageDraw.Draw(av)
d.ellipse((40, 40, 760, 760), outline=ACC, width=28)
c = nhan_vat("chao-truoc", 470)
av.paste(c, ((800 - c.width) // 2, 400 - c.height // 2 + 20), c)
av.save(HERE / "avatar-800.png")
av.resize((98, 98), Image.LANCZOS).save(HERE / "logo-98px.png")  # xem thử ở cỡ hiển thị nhỏ nhất

# Logo ngang 1600×400: nhân vật + tên kênh (dùng trong video, thumbnail, tài liệu)
lg = Image.new("RGB", (1600, 400), BG)
d = ImageDraw.Draw(lg)
c = nhan_vat("chao-truoc", 300)
lg.paste(c, (60, 50), c)
d.text((420, 36), "NHỊP", font=font(130), fill=ACC)
d.text((420, 190), "CÔNG NGHỆ", font=vua(d, "CÔNG NGHỆ", 1100, 130), fill=WHITE)  # chừa lề dưới cho dấu của chữ hoa
lg.save(HERE / "logo-nhip-cong-nghe.png")

# Banner 2560×1440: nội dung nằm trong vùng an toàn 1546×423 ở giữa (x 507–2053, y 508–931)
bn = Image.new("RGB", (2560, 1440), BG)
d = ImageDraw.Draw(bn)
for x in range(60, 2560, 120):
    for y in range(60, 1440, 120):
        d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=TH["duong"])
xung(d, 0, 2560, 1120, 90, 8, TH["thanh"])
xung(d, 0, 2560, 330, 60, 6, TH["thanh"])
c = nhan_vat("chao-truoc", 390)
bn.paste(c, (520, 518), c)
x0, w = 520 + c.width + 50, 2053 - (520 + c.width + 50)
d.text((x0, 548), TEN.upper(), font=vua(d, TEN.upper(), w, 110), fill=WHITE)
d.text((x0, 548 + 150), DINH_VI, font=vua(d, DINH_VI, w, 54, "Bold"), fill=ACC)
d.text((x0, 548 + 150 + 90), PHU, font=vua(d, PHU, w, 46, "Medium"), fill=MUTED)
bn.save(HERE / "banner-2560x1440.png")
print("ok")
