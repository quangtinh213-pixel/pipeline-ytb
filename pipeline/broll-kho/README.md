# Kho B-roll dùng chung

Clip video thật dùng lại cho nhiều video. `kho.json` là danh mục: tệp, độ dài, mô tả, từ khoá, ghi công.

- Thêm clip: thả tệp vào đây rồi chạy `cd pipeline && uv run python -m tttc.broll` (quét, thêm mục mới vào kho.json).
  Claude xem khung hình, điền `mo_ta`, `tu_khoa`, `ghi_cong`.
- Dùng trong video: `broll.nhap(KHO / tep, V, ghi_cong, bat_dau, do_dai)` cắt đoạn cần dùng vào `V/broll/`.
- Chỉ nhận clip giấy phép tự do (Pexels, Pixabay, Wikimedia Commons CC0/CC BY/PD). Không clip có mặt người
  nhận ra được, logo hãng, chữ nước ngoài lớn.

Tệp video không đưa lên git (nặng); chỉ `kho.json` và README được lưu.
