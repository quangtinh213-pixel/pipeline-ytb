"""Tạo logo kênh và thumbnail video 1. Chạy: python3 make_brand.py"""
from PIL import Image, ImageDraw, ImageFont

BG, YELLOW, WHITE = "#111111", "#FFC800", "#FFFFFF"
FONT = "/System/Library/Fonts/SFNS.ttf"  # SF Pro, có dấu tiếng Việt

def font(size, weight="Heavy"):
    f = ImageFont.truetype(FONT, size)
    try:
        f.set_variation_by_name(weight)
    except Exception:
        pass  # font không có biến thể thì dùng mặc định
    return f

def centered(d, y, text, f, fill, W):
    w = d.textlength(text, font=f)
    d.text(((W - w) / 2, y), text, font=f, fill=fill)

# Logo 800x800 (YouTube hiển thị dạng tròn, giữ chữ trong vòng tròn giữa)
logo = Image.new("RGB", (800, 800), BG)
d = ImageDraw.Draw(logo)
d.ellipse((60, 60, 740, 740), outline=YELLOW, width=24)
f = font(380)
box = d.textbbox((0, 0), "TT", font=f)
d.text(((800 - (box[2]-box[0])) / 2 - box[0], (800 - (box[3]-box[1])) / 2 - box[1]), "TT", font=f, fill=YELLOW)
logo.save("logo-tui-tien-cong-nghe.png")

# Thumbnail video 1, 1280x720: chỉ 3 chữ "BẢN FREE ĐỦ?"
th = Image.new("RGB", (1280, 720), BG)
d = ImageDraw.Draw(th)
centered(d, 70, "BẢN FREE", font(250), WHITE, 1280)
centered(d, 360, "ĐỦ?", font(300), YELLOW, 1280)
th.save("thumbnail-video-1.png")

# Bản xem thử ở cỡ feed (168 px rộng) để kiểm còn đọc được không
th.resize((168, 94), Image.LANCZOS).save("thumbnail-video-1-feed-168px.png")
logo.resize((98, 98), Image.LANCZOS).save("logo-98px.png")
print("ok")
