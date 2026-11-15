# Giọng Orus clone – cấu hình đã chốt (15/11/2026)

Giọng: Gemini TTS `Orus` (mẫu `mau-orus.wav` + `mau-orus.txt`, 14,5 giây = 2 câu đầu bộ câu thử), clone bằng OmniVoice chạy GPU AMD trên Mac (`~/Documents/Tối ưu GPU Mac lỏ`).

| Tham số | Giá trị | Lý do |
|---------|---------|-------|
| Mô hình | `omnivoice-base-Q8_0.gguf` | lệch chữ 7,8% so với 13,2% của Q4_K_M (5 câu, whisper medium) |
| Số bước | 16 | 32 bước không tốt hơn |
| Thời lượng ép | số từ / 3,0 | 3,6 từ/giây làm đọc sai nhiều |
| Cách tạo | từng câu riêng | tạo cả đoạn thì lặp chữ ("bạn bạn") |
| Seed | 1 hoặc 7 | người nghe chọn; seed 42 hay đọc "giải nén" thành "dài nén" |
| Viết tên | "Bảy Díp" hoặc "Bảy Zíp" đều được | người nghe xác nhận |

Tốc độ: khoảng 1 giây tạo cho 1 giây tiếng (Q4, 16 bước); Q8 chưa đo riêng.
Ghi chú: whisper cũng nghe sai tên riêng nên số lệch chỉ để so sánh tương đối. Khoá Gemini API người dùng đưa trong chat chỉ dùng để tạo mẫu, không lưu vào file.
