# Chuẩn kênh mẫu @MotCongNghe – đo ngày 09/11/2026

Nguồn: vidIQ (số kênh/video đến 08/11), phụ đề tự động của video Viettel (`38bX5RP4OD0`), bản phân tích hình/tiếng do công cụ vidIQ tự xem video, và 3 thumbnail xem trực tiếp.
**Phần "ước lượng" là kết quả của công cụ, chưa ai trong nhóm tự xem video.** Mẫu: 1 video xem kỹ, 13 video có số liệu.

## 1. Kênh
- Lập 21/10/2026; 15 video, 3.210 sub, 786.841 view (sub/view = 0,4%: người xem đến từ đề xuất).
- 10 ngày đầu ~250 view/ngày; bùng nổ từ 31/10.
- 13 video có số: 6 video 59–192 N view, 7 video 1,7–13 N; trung vị ≈ 12,9 N. Một nửa số video không nổ.
- 6 video nổ: sự kiện đang nóng + góc Việt Nam (bầu cử Mỹ/hàng Việt, nhà máy chip Viettel, Binance hack, chip Mỹ sập 12%, DeepSeek, trung tâm dữ liệu). 7 video thấp: chuyện công ty/sản phẩm nước ngoài (Musk, Anthropic, MacBook, RAM, Google, iPhone Duo) và video crypto Việt Nam mới đăng 1 ngày.

## 2. Video mẫu: "Viettel xây nhà máy chip 1,3 tỷ đô, Nvidia không có nhà máy" (12:14, 163 N view)
**Kịch bản (phụ đề thật):**
- 0:00–0:37 mở bằng sự kiện + cặp số gây tò mò (28 nm so với 2 nm) + 3 câu hỏi hứa sẽ trả lời. Sau đó chia 3 phần có thẻ chương.
- Xưng "mình", ví dụ đời thường mỗi ~1–2 phút (ổ khoá; viết sách rồi mang đi in; chip 15 năm = "đứa bé sinh năm ấy giờ vào lớp 10"; sân bóng và hạt gạo), tự hỏi tự đáp, mời người xem đoán.
- Khoảng 30+ con số; mỗi số nói rõ nguồn ngay trong lời ("theo Reuters", "TrendForce kể ra"). Số tự suy ra được gắn nhãn: "phép tính này là mình tự ướm, không phải dự báo của ai".
- Kết: trả lời lại câu hỏi tiêu đề bằng "2 cái thước", rồi mời bình luận một con số dự đoán.
- Tốc độ đọc: bản ước lượng 140–150 từ/phút của công cụ vidIQ **sai**. Đo trên hai đoạn phụ đề thật (19 s và 17 s): 196 và 222 từ/phút (từ = âm tiết, vì tiếng Việt viết cách chữ theo âm tiết). Video 12 phút ≈ 2.300–2.600 từ.

**Hình/tiếng (ước lượng của công cụ):**
- ~75% minh họa isometric có chuyển động liên tục; ~10% ảnh chụp báo có khung nổi bật; ~8% thẻ số lớn; ~5% ảnh thật; ~2% biểu đồ thời gian (so nhịp Việt Nam, Singapore, Ấn Độ).
- Đổi cảnh 2,5–4 giây; nhân vật dẫn chuyện "Mọt" (chớp mắt, vẫy tay); chữ và khung bật lên có độ nảy.
- Nhãn gắn vào vật đang nói, không phụ đề từng từ. Nguồn ghi chữ nhỏ góc dưới phải.
- Nhạc lofi hạ tiếng khi có giọng; hiệu ứng âm thanh dày (pop, whoosh, ding, gõ phím, khoá cạch); có giọng phụ chen vào câu hỏi.
- Dùng logo hãng (13 hãng) và ảnh chân dung thật; tự dựng ~90% hình.

## 3. Thumbnail (3 cái top)
Cả 3 cùng khuôn: chia đôi khung bằng đường răng cưa; trái là mặt người nổi tiếng (Trump, Jensen Huang ×2), phải là vật/logo (Samsung, chip USB, bong bóng nổ); biểu tượng "VS" hoặc không; 2 hộp chữ vàng nền đen chữ đậm, 4–7 chữ; viền cam mảnh; dòng ghi công ảnh nhỏ góc trên phải.

## 4. Thước đo "chuẩn kênh mẫu" cho pipeline
Đo được trước khi render (chạy bằng `tttc.chat_luong`). Ngưỡng là đề xuất, chỉnh được sau 3 video.

| Chỉ số | Kênh mẫu (ước lượng) | Ngưỡng pipeline |
|---|---|---|
| Độ dài trung bình một cảnh | 2,5–4 s | 2,8–4,5 s |
| Cảnh dưới 1,5 s / trên 8 s | – | 0 / tối đa 3% số cảnh |
| Đồ họa tự dựng (minh-hoa, quy-trinh, so-sanh, thoi-gian, so-lon, bieu-do, chuong) | ~85% | ≥ 70% |
| Bằng chứng (trich-bao, trang-nguon) | ~10% | 8–18% |
| Ảnh/video đời thật (b-roll, nhan-vat) | ~5% | ≤ 15% |
| Sự kiện hình mỗi phút (cảnh + bước nhịp + lần nhân vật xuất hiện) | đổi ~2 s | ≥ 30 |
| Hiệu ứng âm thanh mỗi phút | dày | ≥ 15 |
| Tốc độ đọc | ~200 từ/phút (đo 196–222) | 180–230 |
| Nhạc nền | có, hạ khi nói | có, hạ ≥ 6 dB khi có giọng |
| Mở đầu 90 từ đầu | sự kiện + số + câu hỏi | có số và có dấu "?" |
| Cuối video | câu hỏi bình luận | 60 từ cuối có "?" |
| Số có nguồn | nói nguồn trong lời | 0 lỗi `tttc.kiem` |

Kết quả sau đăng (không điều khiển được, chỉ theo dõi trong `theo-doi.csv`): đặt video cạnh trung vị của chính kênh mình, theo quy tắc 0,5x / 3x trong `ke-hoach-nhan-ban-MotCongNghe.md` mục 7.

## 5. Điều tôi chưa biết
- Chưa xem 14 video còn lại; chưa nghe giọng; chưa biết kênh mẫu làm một video mất bao lâu.
- Lý do 6 video nổ là giả thuyết từ tiêu đề và thumbnail, không có retention.
- Kênh mẫu dùng logo hãng và ảnh người thật; mức rủi ro bản quyền của họ không phải thứ ta nên bắt chước theo mặc định.
