# Nghiên cứu hình ảnh đối thủ – 08/11/2026

Cách làm: lấy storyboard (ảnh thu nhỏ 5 giây/khung) của 1 video top mỗi kênh, xem 50 khung ở giữa và cuối video. Ảnh nằm trong `docs/nghien-cuu/khung-hinh/` (không đưa lên git vì là hình của kênh khác, chỉ dùng tham khảo nội bộ).
Kênh mẫu @MotCongNghe đã xem từ trước (5 khung): minh họa vector isometric, nhãn chữ, biểu đồ động, ảnh nhân vật có ghi công.

Giới hạn: mỗi kênh chỉ 1 video, độ phân giải 160×90, không nghe tiếng nên chưa đánh giá nhạc/âm thanh. Kết luận về "vì sao chạy" là suy đoán từ hình, không có số liệu retention.

## 1. Mỗi kênh làm gì

| Kênh (video xem) | View | Kiểu hình chính | Kỹ thuật đáng học |
|---|---|---|---|
| Kiến Thức Thú Vị (giá RAM tăng gấp 3) | 124 N | Whiteboard: nền trắng, bàn tay vẽ, nhân vật clipart | Cảnh **bồi dần** (thêm vật lên cùng khung thay vì cắt); ẩn dụ trực quan (cái cân cung–cầu); bong bóng suy nghĩ |
| Trạm Tri Thức (vì sao không nước nào tự làm chip AI) | 315 N | Ảnh minh họa AI kiểu truyện tranh, mỗi câu một ảnh | Mật độ chi tiết cao; **số liệu nằm trong cảnh** (màn hình, bảng hiệu); đổi hình ~5 s |
| Spiderum (tất tần tật chip bán dẫn) | 534 N | Phim tài liệu: ảnh lưu trữ, B-roll, collage | Collage biên tập (cờ + chip + bàn tay); bản đồ; biểu đồ trích nguồn; ảnh lịch sử đen trắng |
| Cá Cơm (bong bóng AI) | 20 N | Sơ đồ dark-UI kiểu Notion | Sơ đồ **giữ bố cục và lớn dần** qua nhiều câu; dòng tiền bằng mũi tên + icon; bước 1-2-3; timeline; biểu đồ cổ phiếu có chú thích |
| TS World (vì sao Trung Quốc làm gì cũng rẻ) | 18 N | B-roll thật + thẻ dữ liệu HUD xanh navy | Nhãn chương trên B-roll ("01 / QUY MÔ"); bản đồ luồng hàng; thẻ so sánh đánh số; con số khổng lồ |
| How Money Works (Meta có sống nổi?) | 1,8 Tr | Collage tài liệu: tiêu đề báo in giấy trên thảm cắt xanh | **Mỗi luận điểm có tiêu đề báo làm bằng chứng**, tô vàng câu chính; clip tin truyền hình; linh vật "$?" |
| Economics Explained (AI miễn phí ở Hàn Quốc) | 593 N | B-roll + thẻ báo giấy rách + đồ họa trên nền giấy | Tiêu đề báo giấy rách có nhãn nguồn; biểu đồ chứng khoán có chú thích; sơ đồ đơn giản trên nền giấy |

## 2. Năm điều kênh nào làm tốt cũng có

1. **Hình đổi liên tục.** Trong 50 khung (5 s/khung) gần như không có 2 khung liền nhau giống hệt. Ở mẫu của mình, mỗi cảnh 4–8 s có một chuyển động đầu cảnh rồi đứng yên.
2. **Có hình ảnh thế giới thật.** 5/7 kênh dùng ảnh/B-roll/ảnh tin tức thật. Pipeline của mình chỉ có ảnh nhân vật và ảnh chụp trang nguồn.
3. **Bằng chứng hiện trên màn hình.** HMW, EE, Spiderum cho thấy tiêu đề báo, biểu đồ có nguồn. Đây đúng là lời hứa "số có nguồn" của kênh mình, nhưng mẫu hiện tại chỉ có ảnh chụp trang.
4. **Sơ đồ lớn dần thay vì cắt sang slide mới** (Cá Cơm, Kiến Thức Thú Vị). Người xem theo được mạch vì khung quen.
5. **Một ngôn ngữ hình riêng nhận ra ngay** (giấy cắt dán của HMW, HUD navy của TS World, truyện tranh của Trạm Tri Thức). Kênh mình đã có: isometric đen/vàng/kem. Nên giữ, không đổi theo ai.

## 3. Đề xuất cho pipeline

Ràng buộc: tự động, không lộ mặt, chi phí thấp, mọi số có nguồn, tránh chính sách "nội dung AI hàng loạt" của YouTube.

### Ưu tiên 1 – làm ngay (tác động lớn, rẻ)

| # | Giải pháp | Học từ | Làm thế nào trong pipeline | Công |
|---|---|---|---|---|
| A | **Nhịp con theo từ khoá**: mỗi cảnh hiện thêm 2–3 phần đúng lúc giọng đọc nói tới | Kiến Thức Thú Vị, Cá Cơm | `canh.json` thêm `nhip: [{"tu": "Plus", "hien": "..."}]`; compose dò thời điểm từ trong `giong-timing.json`. Hình đổi mỗi ~2 s mà không cần thêm cảnh | Vừa |
| B | **Mẫu `trich-bao`**: tiêu đề bài báo/văn bản gốc trên mảnh giấy, tô vàng cụm có số, nhãn tên báo + ngày | HMW, EE | Chữ lấy từ `nguon.json` (trích dẫn ngắn ≤ 25 từ, sắp chữ lại, không chụp nguyên trang báo). Nền giấy kem, đúng màu brand | Nhỏ |
| C | **Mẫu `b-roll`**: video thật miễn phí bản quyền + nhãn chương góc dưới | TS World, Spiderum, EE | Pexels/Pixabay (giấy phép cho dùng trên YouTube, không cần ghi công nhưng vẫn ghi). Cần khoá API Pexels miễn phí. Tối đa ~20% số cảnh | Vừa |
| D | **Nhạc nền + âm thanh hiệu ứng** (vụt khi chuyển cảnh, "tách" khi số đếm xong, giấy sột soạt cho `trich-bao`) | Tất cả | Thư viện SFX miễn phí cố định trong `pipeline/am-thanh/`, compose tự gắn theo sự kiện | Nhỏ |

### Ưu tiên 2 – sau khi video 1 lên

| # | Giải pháp | Học từ | Ghi chú |
|---|---|---|---|
| E | **Mẫu `so-do` lớn dần**: nút + mũi tên dòng tiền giữ nguyên qua 3–5 cảnh liên tiếp, mỗi cảnh thêm một nút | Cá Cơm | Hợp đề "tiền đi đâu" (chip → RAM → laptop → túi tiền người Việt) |
| F | **Mẫu `ban-do`**: Việt Nam ↔ Mỹ/Trung Quốc với luồng hàng, số trên mũi tên | TS World, Spiderum | HyperFrames registry có sẵn khối bản đồ, nên dùng lại thay vì tự vẽ |
| G | **Ảnh minh họa AI cho ẩn dụ** (TobyFlow), khoá một phong cách isometric đen/vàng | Trạm Tri Thức | Chỉ cho ý trừu tượng không vẽ được bằng thư viện SVG; ≤ 15% số cảnh; không mặt người thật, không chữ trong ảnh |

### Không nên làm

- **Mỗi câu một ảnh AI** như Trạm Tri Thức: khoảng 120 ảnh/video, khó giữ đồng bộ, tốn credit, và dễ rơi vào nhóm "nội dung sản xuất hàng loạt" bị YouTube hạn chế kiếm tiền.
- **Whiteboard bàn tay vẽ**: cần bộ nhân vật vẽ tay riêng, trông cũ, và lệch hẳn khỏi nhận diện isometric đã có.
- **Clip tin truyền hình** như HMW: bản quyền của đài, kênh mới rất dễ bị đánh bản quyền.

## 4. Tỉ lệ cảnh gợi ý cho một video 11 phút (~110 cảnh)

| Nhóm | Mẫu | Tỉ lệ |
|---|---|---|
| Minh họa isometric | `minh-hoa` | 25% |
| Số liệu | `so-lon`, `bieu-do`, `so-do` | 25% |
| Thế giới thật | `b-roll` | 20% |
| Bằng chứng | `trich-bao`, `trang-nguon` | 15% |
| Khác | `chuong`, `nhan-vat`, `ban-do`, ảnh AI | 15% |

Không 3 cảnh liền cùng nhóm. Mỗi cảnh có ít nhất 1 nhịp con (A).
