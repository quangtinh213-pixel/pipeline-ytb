# Định vị đối đầu @MotCongNghe và vận hành 1 video/ngày

Ngày: 09/11/2026 · Trạng thái: chờ bạn duyệt spec
Thay thế: định vị A ("công nghệ × túi tiền") trong `ke-hoach-nhan-ban-MotCongNghe.md` mục 4 và `lich-4-tuan-dinh-vi-A.md`.
Spec đi cùng: `2026-11-09-nhan-dien-moi-design.md` (nhận diện mới) `2026-11-09-chat-luong-hinh-anh-design.md` (chất lượng hình ảnh, bước đạo diễn) và `2026-11-09-giong-van-kich-ban-design.md` (giọng văn kịch bản tự nhiên, phản biện chéo với agy).

## 1. Mục tiêu

Kênh cạnh tranh trực tiếp với @MotCongNghe: cùng công thức, cùng mảng (tin nóng công nghệ–kinh tế có góc Việt Nam), cùng loại đề, **đăng sớm hơn họ trong ngày**, nhịp đích **1 video/ngày**, nhận diện hoàn toàn riêng (spec 2). Chỉ chạy thật sau khi pipeline qua cổng "chắc" (mục 7).

Thành công được đo ở mục 9. Spec này không hứa ngang kênh mẫu trong 30 ngày đầu.

Ràng buộc: không lộ mặt; giọng tổng hợp VieNeu chạy trong máy; ~30 giờ/tuần; hai điểm duyệt giữ nguyên; mọi số liệu có nguồn tận gốc; bạn có mặt duyệt hai lần mỗi ngày (đã xác nhận 09/11).

## 2. Quyết định đã chốt (09/11/2026)

| Mục | Quyết định |
|---|---|
| Mức nhân bản | Giống công thức và mảng; nhận diện làm lại |
| Làm lại | Bảng màu + khung thumbnail, nhân vật + giọng, tên/logo/avatar/banner |
| Giữ nguyên | Phong cách hình isometric trong video |
| Nhịp | Đích 1 video/ngày; làm chắc pipeline trước khi chạy thật |
| Cách đua | Bám sát đề của họ, đăng sớm hơn (đề xuất ban đầu của tôi là "cùng sự kiện, khác tầng phân tích"; bạn không chọn) |
| Thứ tự | Pipeline chắc + nhận diện mới → chạy khô 3 ngày → chạy thật |

## 3. Dữ liệu kênh mẫu (đo 09/11/2026, vidIQ và RSS công khai)

- Lập 21/10/2026; 3.500 sub; 846 N view; 15–16 video dài. 10 ngày đầu ~250 view/ngày, bùng nổ từ 31/10.
- Nhịp: 9 video trong 5 ngày 05–09/11 (cao nhất 3 video ngày 06/11); 11 video trong 7 ngày 03–09/11. Độ dài 7:29–17:51, đa số 11–14 phút.
- Giờ đăng (giờ Việt Nam, mẫu 16 video): 12 video lúc 17:00–20:05; 4 video lúc 10:30–12:30.
- View (16 video): trung vị ≈ 12,5 N; 4 video trên 130 N (198 N, 190 N, 167 N, 137 N); 3 video 47–95 N; 9 video dưới 13 N (có 2–3 video mới đăng chưa chín).
- Mẫu đề: trong 7 video từ 47 N trở lên, 4 có góc Việt Nam rõ trong tiêu đề (bầu cử Mỹ/hàng Việt, Viettel chip, chip Mỹ sập/giá RAM, trung tâm dữ liệu); 3 không có (Binance hack, DeepSeek, Nvidia "bẫy tình"). Ngược lại "Google sập 500 tỷ USD" có cú sốc và số lớn nhưng chỉ 12,9 N. **Không có luật nào chắc từ mẫu này**; luật radar (mục 4) là giả thuyết khởi điểm và phải hiệu chỉnh bằng dữ liệu của chính kênh.
- Chưa biết: retention của họ, giọng của họ, thời gian họ làm một video.

## 4. Luật đua

### 4.1 Ranh giới nội dung
- Radar chỉ dùng **tiêu đề, giờ đăng và số view** của họ làm tín hiệu chọn đề. Không dùng lời, kịch bản, hình, ví dụ của họ làm nguồn.
- Kịch bản viết từ nguồn gốc của mình; máy kiểm nguồn `tttc.kiem` và bước phản biện độc lập giữ nguyên.
- Bám đề = cùng sự kiện. Không bám cấu trúc câu, ví dụ đời thường hay hình của một video cụ thể.

### 4.2 Chấm đề (radar)

| Câu | Hỏi | Điểm | Trọng số |
|---|---|---|---|
| 1. Cú sốc | Có biến động/sự kiện trong 48 giờ qua? | 0–2 | ×1 |
| 2. Số lớn | Có con số (tỷ đô, %, triệu người) nêu được từ nguồn gốc? | 0–2 | ×1 |
| 3. Góc Việt Nam | Liên quan người, công ty, hàng hóa, giá, thuế ở Việt Nam? | 0–2 | ×2 |

Tối đa 8 điểm. Đề đạt khi ≥ 4 điểm. Cùng điểm thì đề có góc Việt Nam (câu 3 > 0) xếp trước, rồi tới đề mới hơn. Khác luật cũ: câu 3 = 0 **không còn tự động loại** (3/7 video nổ của họ không có góc Việt Nam rõ), nhưng nặng gấp đôi.

Đầu ra `chu-de.md`: 3 đề tốt nhất, mỗi đề có điểm từng câu, link tin gốc, và cờ `ho_da_dang` (RSS của họ có video cùng sự kiện trong 24 giờ qua không). Họ đã đăng cùng đề thì **vẫn làm** (theo quyết định bám đề), chỉ ghi cờ.

### 4.3 Quy tắc giờ đăng
Mục tiêu đăng (hẹn giờ) trong **15:00–16:30**, tức trước khung 17:00–20:05 của họ. `config.json:gio_dang_mac_dinh` đổi từ `19:00` sang `15:30`. Đây là giả thuyết: giờ nào cho kết quả tốt hơn sẽ đo ở mục 9 và đổi sau.

## 5. Đồng hồ một ngày (giờ Việt Nam; mốc là mục tiêu, chưa đo)

| Giờ | Việc | Ai |
|---|---|---|
| 06:30 | Radar: quét nguồn tin, đọc RSS đối thủ, ghi `chu-de.md` | tự chạy |
| 07:00–10:30 | Đề 1 chạy thẳng: nguồn → kịch bản → biên tập giọng và agy 2 vòng (spec 4) → kiểm số liệu và phản biện sự thật | tự chạy |
| trước 11:00 | **Duyệt 1** (đổi đề được tại đây) | bạn |
| 11:00–13:30 | Giọng → đạo diễn (≤ 45 phút, spec 3) → cảnh → hình → `chat_luong` → render | máy + Claude |
| 13:30–14:30 | Đóng gói, soi hình | máy |
| trước 14:30 | **Duyệt 2** | bạn |
| 15:00–16:30 | Đăng (hẹn giờ) | tự chạy |
| tối | Shorts, cập nhật sổ, dọn | máy |

Chạy theo lịch cần máy mở và không ngủ lúc 06:30. Cách đặt lịch (tác vụ định kỳ của Claude hay cơ chế khác) chọn ở bước kế hoạch; yêu cầu là có thông báo khi bản chờ duyệt 1 sẵn sàng.

**Ngày xấu**
- Radar không ra đề đạt điểm: lấy một video từ kho dự trữ evergreen (mục 6).
- Đổi đề ở duyệt 1 sau khi đề 1 đã chạy nguồn/kịch bản: chấp nhận mất việc đã làm, không ép kịp 17:00.
- Duyệt 1 trễ quá 12:00 hoặc render trễ: bỏ mục tiêu "sớm hơn", đăng trong ngày hoặc sáng mai. Không bao giờ đăng bản chưa qua duyệt và máy kiểm.
- Mỗi tuần một ngày chạy từ kho dự trữ để bạn chỉ duyệt một lần.

## 6. Làm chắc pipeline

Hiện trạng đọc từ ba tệp SKILL và hai video đã dựng (`videos/2026-11-13-goi-ai-dang-tien`, `videos/2026-11-15-nvidia-siet-chip`; video nvidia sổ ghi đã đăng 09/11 20:45). Sổ trạng thái chưa ghi giờ từng bước nên **chưa có số giờ thật**.

| # | Việc | Tiêu chí nghiệm thu |
|---|---|---|
| H0 | **Viết lại thẻ phong cách** `docs/phong-cach-kich-ban.md` theo công thức kênh mẫu: mở bằng sự kiện + cặp số + câu hỏi; 3 phần có chương; ví dụ đời thường mỗi 1–2 phút; nói nguồn trong lời; kết trả lời câu hỏi tiêu đề và mời bình luận một con số. Giữ các luật an toàn cũ (không nhận định suông, nguồn tận gốc, nhãn "mình tự tính", không khuyên đầu tư, không phán xét hãng, nói rõ cái chưa kiểm). "Phán quyết túi tiền" và "điều kiện đổi ý" chuyển thành tùy chọn. Giọng văn, danh sách cấm và phản biện với agy do spec 4 lo; ở đây chỉ cập nhật công thức, cấu trúc và `config.json:nguon_tin` nếu cần. | Một video thử qua `python -m tttc.phong_cach` 0 Lỗi; bạn đọc thẻ mới và xác nhận (xem mục 11) |
| H1 | **Ghi giờ từng bước**: `trang-thai.json` lưu thời điểm bắt đầu/kết thúc mỗi bước; có lệnh in thời lượng từng bước và tổng | Hai video hiện có chạy lại một bước bất kỳ thì ra số giờ; có báo cáo tổng từ chọn đề đến duyệt 2 |
| H2 | **Phần cơ học của `canh.json` tự động** (mốc từ `canh-khung.json`, cảnh `chuong` ở đầu beat, `nguon_id`, `nhip`, ánh xạ biến mẫu). Phần sáng tạo (ý đồ, phông, ẩn dụ, camera) do bước đạo diễn trong `2026-11-09-chat-luong-hinh-anh-design.md` | `canh.json` sinh từ `dao-dien.json` đạt `tttc.canh` 0 lỗi và `tttc.chat_luong` 0 lỗi mà không sửa tay phần cơ học; ghi số cảnh phải sửa |
| H3 | **Khóa kịch bản trước giọng**: giọng văn do spec 4 lo (danh sách cấm, biên tập ba lượt, phản biện 2 vòng với agy, nghe thử 60 giây); ước tính tốc độ đọc chạy trước điểm duyệt 1 | Không còn video phải làm lại giọng chỉ vì "mùi máy" hoặc độ dài |
| H4 | **Tốc độ đọc**: chỉnh `vieneu.toc_do` và độ dài kịch bản mục tiêu để tốc độ đo thật nằm trong 180–230 từ/phút (hiện 234 và 249) | Hai video thử đo trong ngưỡng, hoặc ngưỡng được sửa có lý do ghi trong `docs/nghien-cuu/` |
| H5 | **Ánh xạ lại cảnh khi kịch bản đổi** sau khi đã có cảnh (video nvidia phải làm tay: `canh-remap.json`) | Một lệnh chuyển cảnh cũ sang mốc mới, báo cảnh nào cần xem lại |
| H6 | **Shorts tách khỏi đường găng**: dựng ở khoảng tối, đăng sáng hôm sau | Chặng dựng video dài không chờ Shorts |
| H7 | **Radar** theo mục 4.2 + đọc RSS đối thủ (`https://www.youtube.com/feeds/videos.xml?channel_id=UC91zSg_iPgJZZL6KB91BewQ`, đã chạy thử: 15 video gần nhất kèm giờ đăng và view) | Ghi `chu-de.md` đúng định dạng; mỗi video của họ được ghi vào sổ theo mục 9 |
| H8 | **Kho dự trữ evergreen**: video đã qua duyệt 2, chưa đăng, đánh dấu `loai: evergreen` trong `trang-thai.json` | Luôn có ≥ 3 video khi chạy thật |
| H9 | **Hạn mức YouTube**: kiểm hạn mức thật của dự án Google Cloud. `dang.py` gọi `videos.insert` cho video dài và từng Short, cộng `thumbnails.set`, `captions.insert`, `playlistItems.insert`. Theo hiểu biết của tôi (chưa kiểm) mỗi `videos.insert` tốn 1.600 đơn vị trên hạn mức mặc định 10.000/ngày, nên 1 video + 3 Shorts đã tới khoảng 6.900 | Biết con số thật; nếu không đủ cho 1 video + Shorts/ngày kèm dư để chạy lại, xin tăng hạn mức hoặc giảm Shorts |

Cập nhật kèm theo: ba tệp SKILL (`video-moi`, `video-dung`, `video-dang`) nhắc "Túi Tiền Công Nghệ" và luật chọn đề cũ; `video-moi` bỏ phụ thuộc vào `lich-4-tuan-dinh-vi-A.md`.

## 7. Cổng chạy thật

**Chạy khô** = dựng trọn vòng đến duyệt 2 nhưng không đăng. Bắt đầu sau khi spec 2 xong các bước lớp màu, bộ nhân vật và khung thumbnail (tên/avatar/banner trên YouTube chưa cần), và spec 3 xong cấu hình render (A), bước đạo diễn (B), mẫu cảnh mới (C) và chỉ số độ khô (E).

Ba ngày liên tiếp: hai ngày đề evergreen (thành kho dự trữ) và một ngày đề nóng thật (thử làn nhanh). Mỗi ngày phải đạt đủ:
1. Từ chọn đề đến duyệt 2 xong trước 15:00.
2. Không can thiệp tay ngoài hai điểm duyệt; mỗi ngoại lệ ghi vào sổ.
3. `tttc.kiem` 0 lỗi, `tttc.chat_luong` 0 lỗi, `check_av` rỗng.
4. Tốc độ đọc trong ngưỡng đã chốt ở H4.
5. Sổ có giờ từng bước (H1).
6. Độ khô: đạt chỉ số `do_kho` và qua giám khảo hình ảnh (spec 3, mục 4.5 và 7).
7. Giọng văn: `python -m tttc.phong_cach` 0 Lỗi, có `phan-bien-giong-1.md` và `-2.md`, không phải sửa kịch bản sau khi đã có giọng vì giọng văn, bạn nghe 60 giây và xác nhận tự nhiên (spec 4, mục 4).

Trượt một ngày thì sửa chỗ vỡ rồi chạy lại đủ ba ngày liên tiếp. Đạt cả ba ngày, kho dự trữ ≥ 3 video (H8), hạn mức YouTube đã kiểm (H9): ngày đó là **G**, bắt đầu chạy thật.

## 8. Hai video đang có

- `goi-ai-dang-tien` (đã qua duyệt 2, chưa đăng, dựng bằng nhận diện cũ): giữ lại, không đăng bằng nhận diện cũ. Muốn dùng thì render lại (~25 phút) sau khi spec 2 xong.
- `nvidia-siet-chip` (sổ ghi đã đăng): bạn đổi thumbnail, tên, avatar, banner trong YouTube Studio sau khi spec 2 xong.

## 9. Đo và luật quyết định

`theo-doi.csv` thêm bốn cột: `trung_de_ho` (họ có video cùng sự kiện trong ±24 giờ không), `chenh_gio` (giờ đăng của mình trừ giờ đăng của họ, âm là sớm hơn), `radar_hang` (đề có trong top 3 radar sáng đó không), `view_ho_24h` (RSS trả view hiện tại nên radar chụp số đúng 24 giờ sau khi họ đăng để so cùng tuổi).

Hai thước: (1) so với trung vị của chính kênh mình; (2) so với họ trên các cặp cùng đề, trung vị tỉ số view 24 giờ của 10 cặp gần nhất.

**Mốc tính từ G (giả thuyết):**
- G+14: ≥ 12 video; ≥ 80% đăng trước 17:00; đã đo được tỉ lệ trùng đề.
- G+30: có một video vượt 10 N view hoặc CTR > 5%; ≥ 5 cặp cùng đề để so. Không đặt mục tiêu ngang họ.

**Luật dừng và đổi hướng (ngưỡng chỉnh sau hai tuần):**
- Video dưới 0,5× trung vị của mình ở 7 ngày: không làm loại đề đó trong 2 tuần. Trên 3×: làm thêm 2 đề cùng họ trong 10 ngày.
- Radar đoán trúng đề họ (top 3 so với đề họ đăng) dưới 30% sau 2 tuần: sửa luật chấm, không tăng số lượng.
- Trượt mốc 17:00 quá 3 ngày trong 7: hạ về 5 video/tuần, không bỏ máy kiểm.
- 20 video mà không video nào vượt 3× trung vị: đổi cách đua (quay lại "cùng sự kiện, khác tầng phân tích"), không đổi chất lượng trước.
- Có số liệu sai bị chỉ ra: ghim đính chính trong 24 giờ và ghi vào sổ. Hai lần trong 30 ngày thì bỏ chế độ "đề 1 chạy thẳng" và kiểm tay.

## 10. Rủi ro

1. **Sai số liệu khi chạy nhanh.** Cổng kiểm nguồn giữ nguyên, không rút gọn để kịp giờ.
2. **Chính sách nội dung lặp/nhái.** Giảm bằng mục 4.1 và nhận diện riêng ở spec 2.
3. **Hạn mức tải lên YouTube** (H9).
4. **Nhiều thứ phải bật cùng lúc:** máy mở lúc 06:30, token OAuth, VieNeu, extension TobyFlow (spec 2). Ngày hỏng dùng kho dự trữ.
5. **Bạn là điểm nghẽn duy nhất:** hai lần duyệt mỗi ngày; giảm bằng ngày chạy từ kho mỗi tuần.
6. **Kênh đứng yên khoảng một tuần** trong lúc làm chắc và chạy khô, trong khi họ vẫn đăng.
7. **Đạo diễn sâu làm chậm đồng hồ ngày** (spec 3, mục 10): đã đặt giới hạn 45 phút và tỉ lệ cảnh trọng điểm để giữ mục tiêu 15:00.
8. **Giọng văn thêm 25–40 phút** (ước tính, spec 4, mục 6) và phụ thuộc agy, một dịch vụ ngoài; có dự phòng subagent và đánh dấu đỏ ở trang duyệt 1.

## 11. Giả định cần bạn xác nhận khi đọc

- **Thẻ phong cách (H0):** tôi suy ra từ việc bạn chọn "giống công thức" và không chọn tầng phán quyết riêng. Nếu bạn muốn giữ "phán quyết túi tiền" làm bắt buộc, nói để tôi sửa H0.
- **Luật chấm đề (4.2):** khác bản bạn duyệt ở phần 3 (câu 3 = 0 không còn loại tự động). Lý do là 3/7 video nổ của họ không có góc Việt Nam rõ. Nếu bạn muốn giữ luật loại cứng, nói để tôi sửa.
- Giờ đăng 15:00–16:30 là giả thuyết, chưa có dữ liệu của kênh mình.

## 12. Ngoài phạm vi

- Nhận diện (tên, màu, nhân vật, thumbnail, giọng): spec 2.
- Chất lượng hình ảnh và bước đạo diễn cảnh: spec 3.
- Giọng văn kịch bản và phản biện với agy: spec 4.
- Đăng nhiều hơn 1 video/ngày; đăng tự động không qua hai điểm duyệt; trả lời bình luận tự động.
- Kiếm tiền, đa nền tảng, đổi phong cách hình isometric.
