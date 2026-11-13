# Kho B-roll dùng chung

Clip video thật dùng lại cho nhiều video. `kho.json` là danh mục: tệp, độ dài, mô tả, từ khoá, ghi công.

- Thêm clip: thả tệp vào đây rồi chạy `cd pipeline && uv run python -m tttc.broll` (quét, thêm mục mới vào kho.json).
  Claude xem khung hình, điền `mo_ta`, `tu_khoa`, `ghi_cong`, `boi_canh`.
- Dùng trong video: `broll.nhap(KHO / tep, V, ghi_cong, bat_dau, do_dai)` cắt đoạn cần dùng vào `V/broll/`.
- Chỉ nhận clip giấy phép tự do (Pexels, Pixabay, Wikimedia Commons CC0/CC BY/PD). Không clip có mặt người
  nhận ra được, logo hãng, chữ nước ngoài lớn.

## Bối cảnh Việt Nam (từ 13/11/2026)

Mỗi mục kho.json có `boi_canh`:

| `boi_canh` | Nghĩa | Dùng khi |
|---|---|---|
| `vn` | Quay ở Việt Nam (phố, nhà, quán, người Việt, tiền Việt) | Mọi cảnh |
| `trung-tinh` | Cận vật, màn hình, bàn tay; không lộ nơi chốn hay người nước ngoài | Cảnh vật thể, công nghệ, giấy tờ |
| `ngoai` | Lộ nước ngoài (phố Tây, đô la, xu ngoại, người nước ngoài rõ); `nuoc` = mã nước nếu biết | Chỉ khi lời đọc nói đúng nước đó |
| `chua-ro` | Chưa xác minh nơi quay | Như `trung-tinh`; muốn dùng cho cảnh Việt Nam thì xác minh rồi đổi nhãn |

- Cảnh có người, đường phố, nhà cửa, cửa hàng, chợ, phương tiện, tiền, phong cảnh: **bắt buộc `vn`**.
  Không có clip `vn` hợp thì tìm thêm (mục dưới) hoặc đổi cảnh sang đồ họa, không dùng clip nước ngoài thay.
- Tìm clip Việt Nam, theo thứ tự: kho này → Pexels/Pixabay với từ khoá có "Vietnam", "Hanoi", "Saigon",
  "Ho Chi Minh City", "Da Nang", "Hoi An", "Mekong" → Wikimedia Commons (`Category:Videos of Vietnam`, chỉ CC0/CC BY/
  CC BY-SA/PD) → clip user tự quay ở `V/tu-quay/`. Xác minh nơi quay qua tiêu đề/vị trí trên trang gốc hoặc dấu hiệu
  trong hình (biển hiệu tiếng Việt, xe máy, biển số VN).
- Clip CC BY-SA ghi công đầy đủ: `Video: <tác giả>, CC BY-SA 4.0, Wikimedia Commons`.

Tệp video không đưa lên git (nặng); chỉ `kho.json` và README được lưu.
