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

## Nhóm hình (`ITEMS` trong `ve.py`)
- **Nền/đạo cụ chung:** nen-dat, cay, dong-xu, tien, mui-ten-len, mui-ten-xuong, nguoi, nguoi-nhom, tai-lieu, lich, dong-ho, cua-hep (lối vào hẹp), bac-thang (các bậc, bậc cao nhất vàng).
- **Chip/bán dẫn:** chip, chip-bao-mat, wafer, nha-may, nha-may-duc, phong-sach, may-quang-khac, usb, transistor, soi-toc, hat-gao, san-bong, thuoc-do (hai món cuối + soi-toc để so cỡ).
- **Bảo mật:** o-khoa, chia-khoa, khien, ket-sat.
- **AI/dữ liệu/crypto:** may-chu, trung-tam-du-lieu, bo-nao-ai, robot, dam-may, pin, tia-set, tram-phat-song, bong-bong, bieu-do-nen, do-thi-roi, the-ngan-hang, vi-tien.
- **Kinh tế/chính trị:** toa-nha-quoc-hoi, co-viet-nam, container, ta-hang (tàu hàng), cang-bien, oto, can-cung-cau, bua-phan-quyet, thue-phan-tram, hop-thu, cao-oc.
- **Thiết bị/đời sống:** laptop, dien-thoai, kinh-lup, ten-lua, tui-xach.
- **Phông (sân khấu) cho cảnh `minh-hoa`:** `san-khau-*.svg` (may-chu, nha-may, cang, thanh-pho, san-giao-dich, co-quan); mỗi phông là `nen-dat` cộng chi tiết thấp ở rìa sàn (x + y ≥ 2 × chiều cao) nên `viewBox` trùng `nen-dat.svg`, vùng giữa để trống cho vật chính. Thêm phông = thêm một hàm vào `ve.py` + một dòng `san-khau-<tên>` vào `ITEMS`; `canh.json` dùng bằng `san_khau: "<tên>"`.

Quy tắc (test `tests/test_svg.py`): không chữ, viewBox vuông chứa hết hình, ≤ 20 KB (phông `san-khau-*` ≤ 40 KB), chỉ màu trong bảng brand lấy từ `brand/theme.json` (ngoại lệ: cay, co-viet-nam, nen-dat và các phông dùng màu nền đất).
Xem cả thư viện: `uv run python svg/sheet.py` → `svg/thu-vien.png` (qlmanage của macOS).
Hình trụ/cầu: dùng `cil()` (đĩa trụ), cầu = chồng đĩa như `bong_bong()`.
