# Kiểm — số liệu và nguồn

**Cách kiểm:** không chạy được `tttc.kiem` (không có repo). Thay bằng `kiem-tam.py` (kiểm tạm, KHÔNG phải tttc): trích dẫn nguyên văn có trong trang gốc đã lưu, mọi `[#id]` có trong `nguon.json`, không còn chữ số trong lời đọc, câu dùng số `so-bo` có "sơ bộ", câu dùng số `tu-tinh` có "tính ra"/"tự tính", từ cấm `tu-cam.json`, chữ "mình", 90 từ đầu có `[#]`, 60 từ cuối có "?". Kết quả lần chạy cuối (13/11/2026 chiều, sau sửa duyệt 1): **0 lỗi**, không từ cấm, không chữ "mình", tổng lời đọc 2.285 từ (sau khi viết lại thuần Việt), 18/18 trích dẫn tiếng Anh khớp nguyên văn (trích dẫn báo Chính phủ đối chiếu tay qua bản đọc trang ngày 13/11).
**Subagent kiểm độc lập:** không có → executor tự đối chiếu từng câu (không độc lập, đánh dấu đỏ ở duyệt 1).

## Đối chiếu câu ↔ nguồn (những câu dễ nói quá)
| Câu trong kịch bản | Nguồn nói | Kết luận |
|---|---|---|
| "ba mươi ba năm ... dựng nền móng" | Kress: "foundation Jensen created over the last 33 years" (p9) | Khớp; đã sửa gán cho lời bà Kress |
| "thôi chức giám đốc điều hành, thôi luôn ghế trong hội đồng" | "resigned as President, Chief Executive Officer, and a member of the Board, effective immediately" (p1) | Khớp |
| "ngày 11/11 hội đồng đã chấp nhận đơn từ chức" | 8-K Item 5.02 (s1) | Khớp |
| "Cả hai tờ giấy đều không ghi lý do" | PR và 8-K không có câu lý do | Khớp |
| "đóng cửa gần 174 đô" / "mở cửa gần 151 đô" | 173,73 / 150,99–151,01 (y1, y2) | Khớp, làm tròn < 1% |
| "có lúc giá xuống quanh 149 đô" | thấp nhất trong phiên 148,80, đã chốt phiên (y3) | Khớp, xac-minh |
| "đóng cửa quanh 166 đô, giảm hơn bốn phần trăm" | 166,19 USD, −4,34% (y4, chart API đọc 13/11 ~07:41 VN) | Khớp, xac-minh |
| "Kress 59 tuổi" / "Jones 73 tuổi, trong hội đồng từ 1993" | s2, s3 | Khớp |
| "CFO từ tháng 9/2013, tính ra khoảng 13 năm" | p4, t2 | Khớp |
| "gần 25 năm làm tài chính ở Cisco, Microsoft" | p5 | Khớp |
| "lần đầu tiên Nvidia có chức danh chủ tịch hội đồng" | "first-ever Chair of the Board" (p6) | Khớp |
| "Báo Chính phủ từng gọi ông Huang là 'Chủ tịch Tập đoàn NVIDIA'" | v5 | Khớp |
| "Hội đồng kỳ vọng ... không bị gián đoạn" | p8 (lời ông Jones) | Khớp |
| Viettel DGX B200, 06/02/2026, 1,5 ExaFLOPs, sẵn sàng chia sẻ | v1 | Khớp |
| FPT Cloud từ 2 USD/giờ, "chưa đổi" | f1 (13/11) = lần đọc 09/11 | Khớp |
| Thỏa thuận 05/12/2024, Jay Puri ký, ông Huang chứng kiến | v2 | Khớp |
| "ngôi nhà thứ hai" là cam kết của ông Huang | v3 | Khớp |
| 48 nghìn kỹ sư, gần 100 doanh nghiệp, 36 trường (ông nêu hôm ấy) | v4 | Khớp; đã nói rõ là số năm 2024 |
| Giờ VN 4:20 và 5:00 sáng 18/11 | p11 + t4, t5 (PST = UTC−8 trong tháng 11) | Khớp |
| "chừng hai tuần sau thông cáo 28/10" | t7 = 14 ngày | Khớp |
| bình luận viết sẵn của Kress; hỏi đáp chỉ cho nhà phân tích/nhà đầu tư tổ chức; có bản ghi nghe lại; quý khép sổ 25/10 | c1 | Khớp |

## Không dùng
"hơn 11%" (VTV), câu tự tính "hụt 13% lúc mở cửa" (t6, bỏ theo duyệt 1), 7,5 tỷ USD, "430 tỷ USD", 13% như giá đóng cửa, Quốc hội/Trump/Tim Cook/DOJ, chuyện riêng/Megaspeed. AP/TechCrunch có đưa tin cùng sự kiện nhưng không dùng làm nguồn số.

## Tệp gốc đã lưu
`nguon/nvidia-pr.html`, `nguon/sec-8k.htm` (bản thật lấy qua EDGAR; bản `/tmp/video-huang/sec-8k.htm` cũ là trang chặn của SEC, không phải 8-K), `nguon/nvidia-conference-call.html`, `nguon/yahoo-nvda-chart.json` (trong phiên), `nguon/yahoo-nvda-chart-final.json` (chốt phiên 12/11), `nguon/motcongnghe-rss.xml`; ảnh chụp `nguon/*.png` (ảnh `pr.png` bị banner cookie che một phần, nên chụp lại tay trước khi dựng).

## Viết lại thuần Việt (13/11/2026, 14:06)
- Viết lại lời đọc cả 6 beat theo góp ý của người dùng; bản cũ ở `kich-ban-v1.md`. Không thêm hay bớt sự kiện, không đổi số, giữ đủ thẻ `[#id]`; câu tự tính vẫn có "tính ra".
- Trích tiếng Anh trong lời đọc đổi thành lời kể tiếng Việt có nêu người nói (ông Jones, bà Kress). Bỏ chữ "first-ever" khỏi lời đọc, thay bằng "lần đầu tiên". Màn hình vẫn giữ nguyên văn.
- Rà tìm cụm giọng dịch: "điều này", "một cách", "đối với", "liên quan đến", "trong bối cảnh", "tiến hành", "thực hiện", "mang tính" → không còn cụm nào. Không có cụm `dich_tho` nào của tu-cam.json.
- Một lượt tự soi "nghe có giống dịch không": sửa câu bị động "lời hứa ấy được nhắc lại" thành "ban lãnh đạo nhắc lại lời hứa ấy"; "Thông cáo nhấn mạnh" thành "Thông cáo ghi rõ" (nguồn chỉ ghi "first-ever", không có ý nhấn mạnh). Câu "Hội đồng kỳ vọng..." vẫn dùng đúng chữ "kỳ vọng" vì đoạn sau phân tích chữ này.
- kiem-tam.py sau khi viết lại: 0 lỗi.
