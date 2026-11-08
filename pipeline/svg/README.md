# Thư viện SVG isometric

Vẽ bằng `ve.py` để mọi hình cùng một kiểu. Thêm hình mới = thêm một hàm vào `ve.py` + một dòng vào `ITEMS`, rồi chạy:

    uv run python svg/ve.py

## Quy ước
- Isometric 30°, dựng bằng `box()` (hộp) và `on_left/on_right/on_top()` (chi tiết trên mặt hộp).
- Mặt hộp: nóc `#FFFFFF`, trái `#BDBDBD`, phải `#6E6E6E`; khối tối dùng `#2A2A2A`; điểm nhấn vàng `#FFC800` (mặt tối hơn `#E0B000`, `#C79C00`).
- Nét `#111111` dày 6 (chi tiết 2–4). Nền trong suốt; cảnh đặt trên nền `#111111`.
- Không chữ trong SVG (chữ là nhãn của mẫu cảnh). Không logo hãng.
- Ngoại lệ màu duy nhất: cờ thật phải đúng màu cờ.
- `save()` tự canh khung nhìn vuông 400×400 quanh hình.
- Mỗi hình chỉ một vật, một điểm nhấn vàng (phần mà lời đọc đang nói tới).
