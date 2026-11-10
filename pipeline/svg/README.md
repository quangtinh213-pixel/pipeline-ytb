# Thư viện SVG isometric

Vẽ bằng `ve.py` để mọi hình cùng một kiểu. Thêm hình mới = thêm một hàm vào `ve.py` + một dòng vào `ITEMS`, rồi chạy:

    uv run python svg/ve.py

## Quy ước
- Isometric 30°, dựng bằng `box()` (hộp) và `on_left/on_right/on_top()` (chi tiết trên mặt hộp).
- Mặt hộp: nóc `#FFFFFF`, trái `#BDBDBD`, phải `#6E6E6E`; khối tối dùng `#2A2A2A`; điểm nhấn ngọc lam `#22D3EE` (mặt tối hơn `#10A8C4`, `#0B7F96`). Mọi màu lấy từ `brand/theme.json` (đổi nhận diện: sửa theme rồi `uv run python -m tttc.theme ap-dung`).
- Nét `#08181C` dày 6 (chi tiết 2–4). Nền trong suốt; cảnh đặt trên nền `#08181C`.
- Không chữ trong SVG (chữ là nhãn của mẫu cảnh). Không logo hãng.
- Ngoại lệ màu duy nhất: cờ thật phải đúng màu cờ.
- `save()` tự canh khung nhìn vuông 400×400 quanh hình.
- Mỗi hình chỉ một vật, một điểm nhấn vàng (phần mà lời đọc đang nói tới).

## Nhóm hình (`ITEMS` trong `ve.py`)
- **Nền/đạo cụ chung:** nen-dat, cay, dong-xu, tien, mui-ten-len, mui-ten-xuong, nguoi, nguoi-nhom, tai-lieu, lich, dong-ho, cua-hep (lối vào hẹp), bac-thang (các bậc, bậc cao nhất vàng).
- **Chip/bán dẫn:** chip, chip-bao-mat, wafer, nha-may, nha-may-duc, phong-sach, may-quang-khac, usb, transistor, soi-toc, hat-gao, san-bong, thuoc-do (hai món cuối + soi-toc để so cỡ).
- **Bảo mật:** o-khoa, chia-khoa, khien, ket-sat.
- **AI/dữ liệu/crypto:** may-chu, trung-tam-du-lieu, bo-nao-ai, robot, dam-may, pin, tia-set, tram-phat-song, bong-bong, bieu-do-nen, do-thi-roi, the-ngan-hang, vi-tien.
- **Kinh tế/chính trị:** toa-nha-quoc-hoi, co-viet-nam, container, ta-hang (tàu hàng), cang-bien, oto, can-cung-cau, bua-phan-quyet, thue-phan-tram, hop-thu, cao-oc.
- **Thiết bị/đời sống:** laptop, dien-thoai, kinh-lup, ten-lua, tui-xach.
- **Phông (sân khấu) cho cảnh `minh-hoa`:** `san-khau-*.svg` (may-chu, nha-may, cang, thanh-pho, san-giao-dich, co-quan); mỗi phông có sàn riêng (ô nâng của phòng máy, ngã tư, bãi container…) và vật dựng ở hai cạnh phía sau (cạnh y≈14 chạy sang phải, cạnh x≈14 chạy xuống trái), chừa trống vùng giữa cho vật chính. `viewBox` giữ đúng của `nen-dat.svg` (class `_Phong` mang `vb`) để vật cao vượt mép sàn vẫn đặt vật chính cùng một vị trí; chiều cao bị chặn bởi `_cao()` để không chạm nhãn ở đỉnh khung. Thêm phông = thêm một hàm vào `ve.py` (dùng `_san`, `_bx`, `_ghep`) + một dòng `san-khau-<tên>` vào `ITEMS`; `canh.json` dùng bằng `san_khau: "<tên>"`.

Quy tắc (test `tests/test_svg.py`): không chữ, viewBox vuông chứa hết hình, ≤ 20 KB (phông `san-khau-*` ≤ 40 KB), chỉ màu trong bảng brand lấy từ `brand/theme.json` (ngoại lệ: cay, co-viet-nam, nen-dat và các phông dùng màu nền đất).
Xem cả thư viện: `uv run python svg/sheet.py` → `svg/thu-vien.png` (qlmanage của macOS).
Hình trụ/cầu: dùng `cil()` (đĩa trụ), cầu = chồng đĩa như `bong_bong()`.
