# Bộ nhân vật "Nhịp" tạo bằng TobyFlow – 10/11/2026

Brief được duyệt: robot khối hộp isometric, mặt là màn hình LED ngọc lam, không phải người (`nhan-dien-ung-vien.md` mục 3). Model ảnh: Flow, Nano Banana 2.1, tỉ lệ 1:1.

## Quy trình đã chạy (lời nhắc nằm ở `tttc/nhan_vat.py`: `tao_prompt`)
| Pha | Lệnh | Ảnh | Kết quả |
|---|---|---|---|
| Concept | 4 hướng × 2 phương án | 8 | Bạn chọn **1.1 khối hộp** (đầu và thân một khối bo góc) |
| Bản xoay | 4 góc × 2, tham chiếu concept | 8 | Nhất quán; `nghieng-trai` và `nghieng-phai` gần giống nhau, `ngang` không rõ mặt |
| 24 dáng | 6 biểu cảm × 3 góc + 6 ảnh chớp mắt, 2 phương án, tham chiếu concept và 3 bản xoay | 48 | Góc thẳng và nghiêng trái dùng được; góc ngang lệch nhân vật; hào quang ăng-ten bị nhuộm xanh lá |
| Tạo lại | ngạc nhiên, tính toán, bối rối × (thẳng, nghiêng trái), lời nhắc bỏ mọi hào quang | 12 | Hết nhuộm xanh, nét sáng đều ngọc lam |
Tổng 76 ảnh. Bản đầy đủ ở `videos/thu-nghiem/nhan-vat-tho/` (không vào repo); kit chọn ở `pipeline/nhan-vat/`.

## Quyết định
- **Bỏ góc `ngang`** (ảnh không nhất quán, thân lệch). Kit có 3 góc: `truoc`, `nghieng-trai`, `nghieng-phai`.
- **`nghieng-phai` = lật gương `nghieng-trai`** (mô hình ảnh sinh hai góc này gần giống nhau); ăng-ten ở giữa nên lật không lộ.
- **Ảnh chớp mắt sinh từ ảnh mở mắt** (`tach_nen.tao_nham`: tắt các nét sáng ở nửa trên màn hình, giữ miệng, ăng-ten, viền) để hình dáng trùng khít khi phủ lên. Ảnh chớp mắt do mô hình tự tạo bị bỏ vì lệch hình. Chỉ làm cho góc `truoc` (đúng yêu cầu task); góc nghiêng không có chớp mắt vì mắt lệch xuống ngoài vùng nửa trên.
- **Biểu cảm thứ sáu `tinh-toan`** thêm vào brief 5 biểu cảm đã duyệt.
- Mỗi dáng chọn một trong hai phương án theo độ rõ của nét sáng và độ đều của màn hình; tách nền bỏ đốm rác và khử viền xanh lá (`tach_nen`).

## Hạn chế
- Không đủ 4 góc như spec (3 góc); cảnh nào ghi `huong: ngang` bị `tttc.canh` báo Lỗi.
- Ghost mờ của mắt còn thấy rất nhạt ở ảnh chớp mắt.
- Chưa dựng thử một cảnh cho mỗi cặp biểu cảm × góc; đã dựng 6 cảnh (mỗi biểu cảm một góc, cả `goc: phai` và `goc: trai`).
- "Túi" cũ (`svg/tui-*.svg`) vẫn còn, chờ bạn duyệt bộ mới mới gỡ.
