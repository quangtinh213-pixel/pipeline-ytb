# Giọng nam Voice Studio – đánh giá (15/11/2026)

Máy: Xeon E5-2696 v3 (18 nhân), chỉ chạy CPU. Voice Studio 0.5.8, engine OmniVoice (`k2-fsa/OmniVoice`), cổng 127.0.0.1:3900.
Đoạn đọc thử: lời đọc Beat 1 của `videos/2026-11-15-lo-hong-7zip-ai/kich-ban.md` (49 từ, đã phiên âm sẵn).

## Bốn giọng đã tạo (giọng thiết kế, `language=vi`, seed cố định)

| Tệp | Tên trong Voice Studio | profile_id | Mô tả |
|-----|------------------------|------------|-------|
| `1-bien-tap-vien.wav` | NCN - Biên tập viên | `f10cb23c` | nam, trung niên, cao độ vừa |
| `2-tram-am.wav` | NCN - Trầm ấm | `4751c1f6` | nam, trung niên, giọng trầm |
| `3-tre-trung.wav` | NCN - Trẻ trung | `32a7dadf` | nam, thanh niên, cao độ vừa |
| `4-tre-tram.wav` | NCN - Trẻ trầm | `d2b2d460` | nam, thanh niên, giọng trầm |
| `0-vieneu-quoc-tuan.wav` | (VieNeu, giọng đang dùng) | – | để so sánh |

`so-sanh.mp3` = 0 → 1 → 2 → 3 → 4, cùng độ lớn −16 LUFS, cách nhau 1,2 giây.

## Tốc độ tạo

| Cách tạo | Thời gian tạo / độ dài tiếng | Hệ số (giây tạo cho 1 giây tiếng) | Ước tính cho video 9,5 phút |
|----------|------------------------------|-----------------------------------|-----------------------------|
| VieNeu Quốc Tuấn | 15,3 s / 12,4 s (nạp mô hình 11,8 s, một lần) | **1,2** | khoảng 12 phút |
| Voice Studio 16 bước (mặc định) | 98,7–111,3 s / 12,3–13,7 s, đo 5 lần | **7,7–8,1** | khoảng 75 phút |
| Voice Studio 8 bước | 56,2 s / 12,7 s | 4,4 | – (không dùng được, xem dưới) |

- Voice Studio chậm hơn VieNeu khoảng **6,5 lần** trên máy này.
- Mỗi lần chỉ chạy được một việc. Lúc đo có một ứng dụng khác cũng đang tạo giọng (profile `8c2d9e77`, câu "Hé lô xin chào mọi người…") nên việc phải xếp hàng: tổng thời gian chờ lên 320–433 s, và lệnh MCP `generate_speech` bị cắt sau 300 s im lặng (2 lần). Nếu dùng trong pipeline phải gọi thẳng HTTP `POST /generate` và đặt timeout dài.

## Đọc có đúng không (chép lời bằng faster-whisper large-v3, `language=vi`)

| Mẫu | Kết quả |
|-----|---------|
| VieNeu Quốc Tuấn | đúng; "lỗ hổng" bị nghe thành "lỗ hồng" |
| Biên tập viên | "giải nén" nghe thành "dải nén", "lỗ hổng" thành "lỗ hồng" |
| **Trầm ấm** | **đúng hết** |
| Trẻ trung | "giải nén" nghe thành "dài nén" |
| Trẻ trầm | "giải nén" nghe thành "dài nén"; mất ngắt câu |
| Biên tập viên 8 bước | **vô nghĩa** ("Phần âm ghi ấy nên bị hoài điệp…"). Nguyên nhân là thời lượng, không phải số bước (xem phần tối ưu) |

Chép lời chỉ cho biết chữ có rõ không, không nói gì về chất giọng, nhịp hay cảm xúc. Phần đó phải nghe `so-sanh.mp3`.

## Lưu ý khác

- Giọng thiết kế được dựng từ một mẫu "nhận dạng" do engine tự tạo; ASR nhận mẫu đó là tiếng Anh. Tiếng Việt vẫn rõ chữ, nhưng nên nghe kỹ xem thanh điệu có bị lơ lớ không.
- Mỗi bản tạo ra đều qua bước `watermark` (khoảng 2 s). Chưa kiểm tra watermark này có nghe thấy được không.

## Kết luận ban đầu (đã được phần tối ưu bên dưới thay)

- Nếu chọn giọng Voice Studio thì chọn **Trầm ấm (`4751c1f6`)**: đọc đúng nhất, nghe hợp tin công nghệ–kinh tế.
- Qua ứng dụng Voice Studio mất khoảng 75 phút cho một video, so với khoảng 12 phút của VieNeu.

## Tối ưu: gọi thẳng engine OmniVoice (đo 15/11/2026)

Script: `do_omni.py` (chạy bằng python của Voice Studio: `%APPDATA%\VoiceStudio\runtime\project\.venv\Scripts\python.exe`). Giọng Trầm ấm = mẫu nhận dạng `%APPDATA%\OmniVoice\voices\4751c1f6.wav` (lời mẫu là tiếng Anh: "Here's a quick sample of this voice so you can hear how it sounds.") + instruct `male, middle-aged, low pitch` + seed 42. Bộ thử: 8 câu Beat 1–3 của video 7-Zip, khoảng 56 s tiếng. Nạp mô hình mất khoảng 20 s, một lần.

### Lỗi đọc sai là do thời lượng, không phải số bước

Mô hình tự ước lượng thời lượng câu tiếng Việt quá ngắn, khoảng 4,3–4,5 từ/giây, và khi đó đọc ra câu vô nghĩa. Cả 4 câu Beat 2 tạo qua Voice Studio đều hỏng theo kiểu này. **Ép `duration = số từ / 3,5`** thì mọi câu đều đọc ra chữ, kể cả ở 8 bước. Bắt buộc phải làm nếu đưa vào pipeline.

### Tốc độ (giây tạo cho 1 giây tiếng; ước tính cho video 9,5 phút = 570 s tiếng)

| Cách chạy | Hệ số | Video 9,5 phút |
|-----------|-------|----------------|
| Qua ứng dụng Voice Studio, 16 bước | 7,8 | khoảng 74 phút |
| Trực tiếp, 1 tiến trình × 18 luồng, 16 bước | 5,0 | khoảng 47 phút |
| Trực tiếp, 12 bước | 4,3 | khoảng 41 phút |
| **Trực tiếp, 8 bước** | **2,7** | **khoảng 26 phút** |
| VieNeu Quốc Tuấn (so sánh) | 1,2 | khoảng 12 phút |

Gọi trực tiếp nhanh hơn ứng dụng vì ứng dụng mỗi lần đều chép lời lại mẫu nhận dạng bằng whisper, đóng watermark, và xếp hàng chung với các việc khác.

### Những cách không giúp được

| Thử | Kết quả (16 bước) |
|-----|-------------------|
| Gom lô 4 câu / 8 câu | 6,4 / 7,3: **chậm hơn** từng câu |
| 2 tiến trình × 9 luồng | 5,0 |
| 3 tiến trình × 6 luồng | 4,9 |
| 3 tiến trình × 12 luồng | 5,5 |
| Lượng tử hoá int8 (`quantize_dynamic`) | 6,4 và **hỏng tiếng** (CPU không có VNNI, giống VieNeu) |

Thêm tiến trình hay luồng đều không nhanh hơn: nút thắt là băng thông bộ nhớ, không phải số nhân. Riêng CFG luôn chạy hai lượt (có điều kiện và không điều kiện) trong một lô; muốn bỏ lượt thứ hai thì phải sửa mã engine.

### Đọc đúng (chép lời, 8 câu)

Cả 3 mức bước sai lặt vặt ngang nhau, mỗi mức khoảng 5 chỗ:
- Lỗi gặp ở mọi mức: "giải nén" thành "dài nén", "lỗ hổng" thành "lỗ hồng".
- 8 bước có thêm: "Vợi" (Lỗi), "tiệp" (tệp), "lỗ ổng".
- 12 bước có thêm: "tim tặc" (tin tặc).

Nghe so sánh: `tram-am-16buoc-8cau.mp3`, `tram-am-12buoc-8cau.mp3`, `tram-am-8buoc-8cau.mp3`.

### Đề xuất

Nếu dùng Voice Studio cho video dài thì dùng **8 bước**, gọi thẳng engine, ép thời lượng, tạo từng câu và lưu đệm theo câu như VieNeu. Mất khoảng 26 phút mỗi video, chạy nền sau duyệt 1. Nên tắt ứng dụng Voice Studio khi tạo để có thêm RAM và không phải tranh tài nguyên.
