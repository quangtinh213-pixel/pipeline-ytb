# Các cách trình bày đang hot cho video tin công nghệ–kinh tế – 10/11/2026

Mục đích: tìm cách trình bày chuyên nghiệp hơn, rõ ràng hơn, dễ hình dung hơn cho pipeline `tttc` (isometric, HyperFrames/GSAP, không mặt người, **mọi chữ trên màn hình là tiếng Việt**). Tài liệu này là nghiên cứu, chưa phải quyết định; phần 5 là đề xuất để chọn.

## 1. Nguồn và độ tin cậy (đọc trước)
- **Ba video xem bằng công cụ vidIQ** (`vidiq_video_watch`, một mô hình tự xem video và tả lại; 25 credit mỗi video). Đây là mô tả do máy viết, chưa được mình xem lại từng khung; tỉ lệ phần trăm khung hình là ước lượng của công cụ. Chọn theo "bứt phá" (view so với mức thường của kênh), không phải theo độ đẹp:
  - [If You Don't Understand Bonds, You Don't Understand Money](https://www.youtube.com/watch?v=22qkuMCzN7I) – Money Bureau, kênh 23 N đăng ký, 1,2 triệu view, vượt mức thường của kênh 184 lần (giải thích tài chính).
  - [The One Machine China Can't Buy](https://www.youtube.com/watch?v=kswztV-o47E) – Sam Szuchan, kênh 34 N đăng ký, 211 N view, vượt 8 lần (công nghệ – địa chính trị, đúng mảng của ta).
  - [Most Popular Sneaker Brands (1900–2026)](https://www.youtube.com/watch?v=PzzTU3Wjnm4) – Momoboo, kênh 507 đăng ký, 620 N view, vượt 327 lần (biểu đồ xếp hạng chạy theo năm).
- **Không xem được:** video thứ tư (kênh tin tức công nghệ tiếng Việt lớn, [Hiểu Biết Hơn Mỗi Ngày](https://www.youtube.com/watch?v=vSu2JOWhXQ4)) vì hết credit vidIQ. Vì vậy **chưa có đối chiếu với một kênh Việt thứ hai ngoài @MotCongNghe** (đã phân tích ở `kenh-mau-motcongnghe-2026-11-09.md`).
- **Tìm web:** gần như toàn blog của hãng làm video/công cụ AI, nên chỉ lấy làm định hướng, không lấy số liệu. Ví dụ [Subclip về phụ đề động](https://subclip.app/blogs/animated-captions-2026-best-practices-reels-shorts-x-exporting-srt) và [FluxNote](https://fluxnote.io/blog/ai-captions-that-improve-watch-time) nói phụ đề tô từng từ giữ người xem lâu hơn (con số +34% là thử nghiệm riêng của hãng, không có phương pháp công bố; chủ yếu cho video ngắn). [Hatch Studios](https://hatchstudios.com/top-vi) và [Videobolt](https://blog.videobolt.net/post/top-motion-graphics-trends-2026) nói xu hướng 2026 là lai ghép đồ họa chuyển động với cảnh thật và đề cao sản phẩm "có tay nghề" so với hàng loạt do AI sinh ra (nhận định định tính). Tìm riêng về Bloomberg, Vox, Wendover không ra tài liệu mô tả thiết kế; chỉ có nguyên tắc biểu đồ chung (dùng màu mang nghĩa, ghi nhãn trực tiếp, bỏ chi tiết thừa).
- **Kiến thức của mình** (không có nguồn kiểm được trong phiên này) được đánh dấu "kinh nghiệm".

## 2. Điều ba video giống nhau (đây là phần đáng tin nhất vì lặp lại)
1. **Một ý, một hình lớn.** Hình hoặc đồ họa chiếm khoảng 60–80% khung, chữ không quá khoảng 20%, có nhiều khoảng trống quanh. (Bản thử của ta: ở cảnh quy trình và cảnh chip, hình chỉ chiếm khoảng 1/6 khung, còn lại là nền đen trống.)
2. **Màu có nghĩa và rất ít màu.** Nền tối hoặc nền trắng; một màu nhấn (đỏ, xanh lá, hoặc màu của từng hãng) dành cho đúng chỗ cần nhìn.
3. **Số liệu là nhân vật chính:** số lớn nảy lên hoặc đếm tăng, thanh so sánh chạy, nhãn màu ngay trên vật đang nói.
4. **Nguồn hiện bằng ảnh chụp tài liệu có tô sáng** đoạn quan trọng (gạch chân, ô sáng), không đọc cả đoạn.
5. **Nhịp 2–6 giây một cảnh, chuyển cảnh bằng chuyển động** (zoom, lia mờ, trượt), kèm hiệu ứng âm thanh dày (whoosh, click, pop) khớp từng chuyển động.
6. **Phụ đề chọn lọc, không phải chép toàn bộ lời:** hiện từ khóa hoặc ý lớn đúng lúc người nói nhấn; hai trong ba video không hiện phụ đề kiểu karaoke toàn lời.
7. **Chữ sans-serif đậm, đồng nhất;** một video thêm font đơn cách (monospace) cho thông số kỹ thuật.
8. **Cả ba đều có chỗ "vụng" giống nhau:** tài liệu lướt qua nhanh hơn thời gian đọc; thiếu nguồn trên màn hình (Momoboo); chữ trên ảnh chụp báo nhỏ khi xem điện thoại; ánh sáng cảnh quay thật gắt.

## 3. Các cách trình bày cụ thể và độ hợp với pipeline
| # | Cách trình bày | Thấy ở | Hợp pipeline? | Việc cần làm |
|---|---|---|---|---|
| 1 | Hình lớn chiếm 60–80% khung, chữ ≤ 20% | cả ba | **Rất hợp, đang thiếu** | Phóng to nội dung mẫu `quy-trinh`, `so-sanh`, cảnh `minh-hoa` đơn lẻ; quy tắc kích cỡ tối thiểu |
| 2 | Số lớn đếm tăng (counter) | Sam Szuchan, Momoboo | Hợp (`so-lon` đã có, thiếu đếm tăng) | Thêm hiệu ứng đếm lên giá trị trong `so-lon` |
| 3 | Ảnh chụp tài liệu + ô sáng quét đúng cụm | Money Bureau, Sam Szuchan | Hợp (`trich-bao`, `to_vang` đã có) | **Hiện bản dịch tiếng Việt** thay vì nguyên văn Anh; ô sáng quét vào cụm đã dịch |
| 4 | Ẩn dụ vật lý đặt cạnh số: bập bênh, domino, đồng hồ đo, cánh cửa hẹp | Money Bureau | **Rất hợp** (bước đạo diễn đã có `an_du`) | Vẽ thêm vào thư viện SVG: `bap-benh`, `domino`, `dong-ho-do` |
| 5 | Bản đồ vector phẳng tối giản, chấm toạ độ phát sáng, vòng khoanh quốc gia | Sam Szuchan; Johnny Harris/Vox (kinh nghiệm) | **Rất hợp với đề xuất khẩu chip** (Mỹ, Việt Nam, Malaysia, Thái Lan) | Mẫu cảnh mới `ban-do`; cần nguồn bản đồ không bản quyền |
| 6 | Biểu đồ thanh xếp hạng chạy theo năm, số năm khổng lồ, logo gắn thanh | Momoboo | Hợp cho thị phần, giá, chi tiêu qua năm | Mở rộng `bieu-do` thành kiểu `xep-hang` (không dùng logo hãng thật nếu chưa chắc về bản quyền) |
| 7 | Chia đôi màn hình: một bên số liệu động, một bên hình tiêu điểm | Momoboo, Sam Szuchan | Hợp (`so-sanh` gần giống) | Bố cục `chia-doi` cho số liệu + vật chính |
| 8 | Nền lưới/chấm tạo cảm giác phân tích | Money Bureau | **Đã có** (lưới chấm nền tối) | Không cần làm |
| 9 | Tô màu chọn lọc: cảnh xám, chỉ một chi tiết có màu | Sam Szuchan | Hợp (quy tắc "một điểm nhấn vàng mỗi hình" đã cùng ý) | Giữ và nhấn mạnh trong bước đạo diễn |
| 10 | Phụ đề từ khóa (kinetic) thay cho phụ đề đủ câu dưới đáy | Money Bureau, Sam Szuchan | **Cân nhắc:** phụ đề đủ câu có ích khi xem tắt tiếng; blog web nói tô từng từ tốt cho video ngắn, chưa rõ với video dài | Thử A/B trên hai video sau khi đăng, chưa đổi ngay |
| 11 | SFX dày, khớp từng chuyển động | cả ba | **Đã có** (27 hiệu ứng/phút ở bản thử, chuẩn ≥ 15) | Giữ |
| 12 | Giữ tài liệu đủ thời gian đọc | điểm vụng của cả ba | Hợp | Quy tắc: cảnh có chữ phải ≥ (số từ ÷ 3) giây, kiểm trong `tttc.canh` (cảnh báo) |
| 13 | Màu theo hãng/quốc gia nhất quán (Nike cam, Puma đỏ…) | Momoboo | Hợp, cẩn trọng bản quyền logo | Bảng màu theo quốc gia/hãng trong `theme.json` (không logo) |
| 14 | Người dẫn xuất hiện thành ô góc bo tròn (PiP) | Money Bureau, Sam Szuchan | Không hợp (kênh không mặt người); nhân vật "Túi" đã đóng vai tương tự | Không làm |

## 4. Lỗi trình bày nhìn thấy ở bản thử hiện tại (xem trực tiếp khung hình)
1. **Còn chữ tiếng Anh trên màn hình:** thẻ trích báo hiện nguyên văn Anh ("Vietnam: [D:1] National Security X…", "I was unfaithful to my wife…"); nhãn "VS" ở `so-sanh`.
2. Dòng nguồn trên thẻ trích báo dài, xuống dòng và đè lên đường kẻ ("PHỤ LỤC NHÓM NƯỚC").
3. Cảnh quy trình: ba biểu tượng nhỏ nằm một góc, nhãn nhỏ, nền đen trống; mũi tên cuối chỉ ra khoảng không.
4. Cảnh `so-sanh` đang chạy có một bên mờ nhạt ở giữa cảnh, người xem không biết bên đó là gì.
5. Cảnh chip: một vật nhỏ giữa khung rộng, nhãn đang mờ vì hiệu ứng vào.
6. Sáu phông theo chủ đề gần như không phân biệt được bằng mắt (chỉ vài khối thấp ở rìa sàn).
7. Hình `thuoc-do` ("giữ đúng mức") trông như phím đàn.
8. Nhãn còn dài hơn 5 từ ở 13 cảnh (kế thừa từ video đã đăng).

## 5. Đề xuất (xếp theo giá trị trên công sức; chưa làm trừ mục 1–2)
1. **Mọi chữ trên màn hình bằng tiếng Việt.** Trích báo hiện bản dịch của kênh (nhãn nhỏ "dịch từ bản gốc tiếng Anh"), nguyên văn giữ trong `canh.json` để kiểm chứng; `tttc.canh` báo Lỗi khi một ô chữ trông như tiếng Anh; "VS" đổi thành chữ Việt. *(Yêu cầu của bạn, đang làm.)*
2. **Phóng to và dọn bố cục** ở `quy-trinh`, `so-sanh`, `minh-hoa` đơn lẻ, dòng nguồn một dòng, nhãn lớn hơn, đo "tỉ lệ khung hình được dùng" (mục 3, số 1 và 12). *(Đang làm.)*
3. **Vẽ lại sáu phông** thành môi trường nhận ra được (cảng có cần cẩu và chồng container, trung tâm dữ liệu có hàng tủ máy, thành phố có đường chân trời…), sàn khác nhau theo chủ đề.
4. **Thêm ẩn dụ vật lý vào thư viện** (bập bênh, domino, đồng hồ đo, bản đồ) và **mẫu `ban-do`** cho các đề xuất khẩu, thuế, chuỗi cung ứng.
5. **Số lớn đếm tăng** và **biểu đồ thanh xếp hạng** cho đề về giá, thị phần, chi tiêu.
6. **Thử A/B phụ đề** đủ câu và từ khóa động sau khi đăng (cần retention thật).

## 6. Rủi ro và điều chưa biết
- Chính sách YouTube về nội dung sản xuất hàng loạt/khuôn mẫu: một tóm tắt thứ cấp (TubeBuddy, qua bài web) nói YouTube đang siết loại video lặp lại, ít giá trị gốc. Bước đạo diễn (mỗi video có ẩn dụ và góc nhìn riêng, chữ viết riêng) là phòng vệ tự nhiên; mình **chưa kiểm** nguồn chính thống của chính sách này.
- Chưa có số đo thật về việc cách trình bày nào giữ người xem tốt hơn cho khán giả Việt; phép thử thật là retention sau khi đăng.
- Bản đồ và logo hãng có thể vướng bản quyền; cần kiểm nguồn trước khi làm (mục 3, số 5, 6, 13).
- Công cụ vidIQ mô tả ba video bằng mô hình; chi tiết nhỏ (cỡ chữ, phần trăm khung) là ước lượng.
