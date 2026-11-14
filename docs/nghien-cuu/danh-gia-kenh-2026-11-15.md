# Đánh giá kênh sau 6 video dài: góc nhìn YouTube, đối thủ và dự án

- **Ngày:** 15/11/2026
- **Nguồn số liệu:**
  - Kênh mình: YouTube Data API (view công khai lúc đo) và YouTube Analytics, từ 01/11 đến 15/11. Analytics trễ 2–3 ngày, thực tế chỉ có số đến 11/11. Ba video sau cùng chưa có đường giữ chân.
  - Đối thủ `@MotCongNghe`: vidIQ, đo 14/11, gồm 21 video dài và số kênh theo ngày.
  - CTR: hai số nhập tay từ Studio trong `theo-doi.csv`.
- **Giới hạn:** mẫu rất nhỏ (6 video dài, 6 Shorts). Mọi kết luận dưới đây là hướng nghiêng, chưa phải luật. Lúc đo, vidIQ đã hết credit nên chưa so được CTR và giữ chân của đối thủ.

---

## 1. Tóm tắt

1. **Kênh đang đi xuống theo từng video.** View công khai lúc đo của các video dài: 3.108 → 93 → 120 → 150 → 27 → 0, theo thứ tự đăng. Kênh có 7 sub. Đây là kiểu "YouTube thử rồi ngừng thử": video đầu được phát khá rộng, tín hiệu hài lòng yếu, nên các video sau chỉ được thử trên nhóm rất nhỏ.
2. **Chiến lược "bám đề, đăng sớm hơn" chưa từng được thực hiện đúng**, và về nguyên lý cũng bất lợi. Cả 3 cặp trùng đề, mình đều đăng **muộn hơn** họ: +3,0 giờ, +2,2 giờ, +4,5 giờ. Cùng sự kiện, cùng khuôn, cùng tệp khán giả thì thuật toán đề xuất kênh có lịch sử hài lòng tốt hơn, tức là họ.
3. **Điểm nghẽn đo được nằm ở CTR và giữ chân, không nằm ở số lượng.**
   - CTR dao động từ 6,3% đến 1,3%.
   - Giữ chân trung bình 24–42%. Chỉ số `relativeRetentionPerformance` (so với video cùng độ dài trên YouTube, 0,5 là trung vị) chủ yếu ở 0,05–0,45, tức dưới trung vị.
4. **Shorts là kênh khám phá duy nhất đang chạy đều.** Hai Shorts về điện thoại cũ đạt 940 và 888 view, nhiều hơn mọi video dài trừ video đầu. Shorts gần như không kéo được sub.
5. **Dự án đang đầu tư vào máy nhiều hơn vào vòng học.** 135 commit, 37 module và 8 tài liệu nghiên cứu trong khoảng 7 ngày. Ngưỡng chất lượng hình đã đảo chiều hai lần, mỗi lần dựa trên một nghiên cứu một chiều chứ không dựa trên số liệu của kênh mình. Các nâng cấp P0–P2 ngày 14/11 chưa có trong video nào đã đăng.

---

## 2. Kênh mình: số liệu thật

### 2.1 Từng video dài

| Video | Đăng (VN) | Độ dài | View lúc đo | CTR | Giữ chân TB (AVD) | So với video cùng độ dài |
|---|---|---|---|---|---|---|
| CEO Nvidia xin lỗi (`E17SceQLG9I`) | 09/11 20:45 | 8:10 | 3.108 | **6,3%** | 35,6% (2:54) | 0,28–0,41 |
| Cấm iPhone cũ (`w60qG6ipY1s`) | 10/11 18:50 | 8:11 | 93 | **1,3%** | 42,2% (3:27) | 0,28–0,58 |
| Grab giảm phí (`GXoScbOFOQE`) | 11/11 16:50 | 8:13 | 120 | – | **24,4%** (2:00) | **0,05–0,27** |
| Lá thư Nvidia (`d1jh3GyOdrU`) | 12/11 18:15 | 5:47 | 150 | – | chưa có | – |
| Jensen từ chức (`RX21zw1F8S0`) | 13/11 19:15 | 9:15 | 27 | – | chưa có | – |
| Microsoft sập (`gg4P35JfyXk`) | 14/11 15:30 | **2:21** | 0 | – | chưa có | – |

Cách đọc:
- **Cấm iPhone cũ:** người đã bấm thì xem khá lâu (42%), nhưng gần như không ai bấm (CTR 1,3%). Lỗi nằm ở **thumbnail và tiêu đề**.
- **Grab giảm phí:** có người bấm, nhưng đến giữa video chỉ còn 15% người xem, đến cuối còn 4%. Lỗi nằm ở **nội dung và nhịp**.
- **CEO Nvidia xin lỗi:** CTR tốt và đi theo làn sóng của đối thủ (456 view từ "video đề xuất"). Giữ chân dưới trung vị nên YouTube ngừng đẩy.
- **Microsoft sập:** dài 2:21 nhưng đăng như video dài. Video này 0 view sau khoảng 24 giờ. Bộ đếm công khai có thể trễ, nhưng cũng có thể kênh đã gần như không được thử nữa.

### 2.2 Đường giữ chân (tỉ lệ người còn xem)

| Mốc | CEO Nvidia | iPhone cũ | Grab |
|---|---|---|---|
| 3% (~15 s) | 92% | 85% | 96% |
| 10% (~49 s) | 67% | 68% | 59% |
| 20% | 50% | 54% | 35% |
| 50% | 32% | 34% | **15%** |
| 100% | 14% | 29% | 4% |

Cả ba video mất khoảng một phần ba người xem trong 50 giây đầu. Đây đúng là vùng mà nghiên cứu 14/11 chỉ ra lỗi: bumper, thẻ chương đặt quá sớm, B-roll tối, chụp nguyên trang web chữ nhỏ.

### 2.3 Người xem và nguồn view (01–11/11)

- **Nguồn view:** "Duyệt tìm" (trang chủ) 1.986, video đề xuất 456, Shorts feed 405, tìm kiếm 29. Kênh sống nhờ thuật toán đề xuất, gần như không có tìm kiếm.
- **Người xem:** nam 25–44 tuổi chiếm 78%. Việt Nam 88%.
- **Thiết bị:** máy tính 59%, điện thoại 31%, TV 8%. Tỉ lệ máy tính cao bất thường, phù hợp với dân văn phòng xem trong giờ làm.
- **Sub:** không ai xem từ tệp đã đăng ký. Cả kênh mới có 7 sub, và Shorts kéo được 2 trong số đó.

### 2.4 Shorts

| Shorts | View |
|---|---|
| iPhone 15 Plus cũ 15,89 triệu | 940 |
| Lệnh cấm nhập đã 8 năm tuổi? | 888 |
| Grab phí 7% từ 26/02 | 208 |
| Gói 3.000 tỷ của Grab | 200 |
| Sang năm còn mua máy cũ được không? | 190 |
| Grab giảm 2.000 đồng/cuốc | **1** (cần xem lại Studio, có thể bị hạn chế) |

Chủ đề tiêu dùng trong nước (máy cũ, phí Grab) **thua ở video dài nhưng thắng ở Shorts**. Câu hỏi giá cụ thể hợp với khuôn 30–50 giây hơn là 8 phút.

---

## 3. Đối thủ `@MotCongNghe`: điều gì làm họ thắng

### 3.1 Quy mô

Kênh lập 21/10. Sau 24 ngày có 4.610 sub, 1,28 triệu view và 21 video dài, mỗi ngày thêm khoảng 130–250 sub. Trung vị view của 19 video dài (bỏ 2 video mới nhất) là **17,4 N**. Trung vị của mình khoảng **106**.

### 3.2 Video nào nổ, video nào không

| Nhóm | Video (view, breakout score) | Điểm chung |
|---|---|---|
| **Nổ** | Viettel chip 186 N (×14), DeepSeek 110 N (×9,7), Data center & bầu cử 75 N (×5,6), Jensen từ chức 80 N (×5,3), Bầu cử Mỹ & hàng Việt 205 N (×4,8), Bong bóng AI 277 N (×3,2), Binance hack 138 N | **Sự kiện vĩ mô** (địa chính trị, thị trường sập, hack tỷ đô) **× câu hỏi Việt Nam được/mất gì** |
| **Nhạt** | Tiểu sử Jensen 13 N, CPU/GPU/TPU 17 N, MacBook cảm ứng 10 N, Anthropic IPO 10 N, iPhone Duo 2 N, RAM 14 N | Chân dung, giải thích kiến thức, sản phẩm nước ngoài, không có cú sốc |

Hai điều nổi bật:
- **Họ làm chuỗi.** Có 6 video về Nvidia/Jensen trong 7 ngày: bẫy tình → ngoại tình → tiểu sử → từ chức → Musk ký đơn. Mỗi tập mới kéo người xem về các tập cũ qua đề xuất. Mình cũng làm 3 video Nvidia, nhưng đi sau và không nối với nhau.
- **Họ không cố đăng giờ cố định.** Tin vĩ mô đăng 17:00–18:00, một số video đăng 11:00 (Viettel 186 N, Microsoft). Giờ đăng không quyết định bằng chọn đề.

### 3.3 Thumbnail và tiêu đề

- **Thumbnail của họ dùng một khuôn duy nhất:** viền cam, tia sét chia đôi, mặt người thật bên trái, bối cảnh Việt Nam hoặc bằng chứng bên phải, hai hộp vàng chữ đen, ghi nguồn ảnh ở góc. Người xem nhận ra kênh trong 0,5 giây.
- **Thumbnail của mình qua 6 video dùng 5 phong cách khác nhau:**
  - hai hộp vàng gần giống họ (CEO Nvidia, Jensen từ chức), lại **dùng lại cùng một ảnh Jensen** Wikimedia;
  - hộp cyan kèm giá gạch (iPhone);
  - mặt người do AI tạo kèm app Grab giả (Grab);
  - phong bì tối (Lá thư);
  - nền tối tối giản, thẻ trích nghiêng chữ nhỏ (Microsoft).

  Kết quả là mình không có nhận diện riêng, mà hai cái gần họ nhất lại là hai cái giống họ.
- **Tiêu đề của họ:** `[sự kiện cụ thể có số]: [một câu hỏi Việt Nam/túi tiền]?`, thường 60–90 ký tự.
- **Tiêu đề của mình:** nhiều cái chồng hai móc kèm chữ giật gân, như `SỐC: … bất ngờ từ chức! Lời hứa … có tan thành mây khói?` hay `Sự thật vụ…: Tự tay làm sập 18 giờ, người dùng Việt Nam chịu trận!`. Video có tiêu đề "SỐC" chỉ đạt 27 view.

---

## 4. Đánh giá lại định vị

### 4.1 "Bám đề, đăng sớm hơn" không hợp với vị thế hiện tại

- **Về thực thi:** mục tiêu 15:00–16:30 chưa đạt lần nào trên đề trùng. Giờ đăng thực tế: 20:45, 18:50, 16:50, 18:15, 19:15, 15:30.
- **Về nguyên lý:** khi hai kênh đăng cùng sự kiện, cùng khuôn hình isometric, cùng khung thumbnail, YouTube xếp video của mình như một **bản thay thế** cho video của họ. Kênh mạnh hơn sẽ thắng ở cả trang chủ lẫn đề xuất. View tốt nhất của mình (video CEO Nvidia) có được khi mình đứng **cạnh** video của họ (lưu lượng từ đề xuất), chứ không phải khi thay thế được họ.
- **Rủi ro chính sách:** kênh giọng tổng hợp, dựng theo template, cùng đề và cùng khuôn với một kênh khác dễ bị xếp vào nhóm "nội dung không nguyên bản" (inauthentic/reused) khi xét bật kiếm tiền. Phần phân tích riêng là thứ bảo vệ kênh.

Spec 09/11, mục 9, đặt luật "20 video không có video nào vượt 3× trung vị thì đổi sang *cùng sự kiện, khác tầng phân tích*". Mình đề xuất **đổi sớm, ngay bây giờ**, vì ba lý do:
- (a) trung vị của mình quá nhỏ (khoảng 100 view) nên luật "3× trung vị" không còn ý nghĩa;
- (b) xu hướng giảm đều qua 6 video;
- (c) chi phí đổi rất thấp: radar và kịch bản giữ nguyên, chỉ đổi luật chọn góc.

### 4.2 Định vị đề xuất: "video xem tiếp" của cùng câu chuyện

Không chạy đua làm bản tin đầu tiên. Làm **tầng thứ hai**, tức video mà người vừa xem xong bản tin của họ muốn xem tiếp:

| Họ làm | Mình làm (ví dụ cho chuỗi Nvidia) |
|---|---|
| Jensen từ chức: chuyện gì xảy ra? | 48 giờ sau: ai tạm quyền, cổ phiếu Nvidia và đơn hàng chip cho Việt Nam thay đổi ra sao (số liệu ngày 2) |
| Microsoft 365 sập 13 tiếng | Công ty Việt Nam nên làm gì để không phụ thuộc một nhà cung cấp: chi phí thật của 1 giờ sập |
| Bong bóng AI nổ? | Bảng theo dõi giá RAM/SSD tại Việt Nam qua 4 tuần (có số mình tự thu, ghi rõ "mình tự tính") |

Đi kèm hai việc:
- Tiêu đề và thumbnail **nói rõ phần mới**, ví dụ "48 giờ sau", "con số thật", "bảng giá", để thuật toán xếp video là *bổ sung*, không phải *trùng*.
- **Mỗi chuỗi được 3–5 tập** khi đề còn nóng, và các tập nối nhau bằng màn hình kết thúc và playlist.

### 4.3 Chọn đề

Từ số liệu của cả hai kênh:
- **Ưu tiên:** sự kiện vĩ mô có số lớn kèm cái giá cụ thể cho người Việt (giá, việc làm, xuất khẩu, tiền gửi).
- **Hạ ưu tiên cho video dài:** chân dung, giải thích kiến thức thuần, sản phẩm nước ngoài không có cú sốc, chính sách tiêu dùng trong nước. Nhóm cuối (máy cũ, phí Grab) **chuyển thành Shorts**.

Đề xuất sửa radar (`tttc.radar`):
- thêm câu "Có cái giá cụ thể cho người Việt không?";
- khi `ho_da_dang` đúng và mình trễ hơn 2 giờ, bắt buộc chọn góc "tầng thứ hai" thay vì làm trùng.

---

## 5. Ba đòn bẩy cụ thể, theo thứ tự

### 5.1 CTR: thumbnail và tiêu đề (ảnh hưởng lớn nhất, rẻ nhất)

1. **Chốt một khuôn thumbnail riêng và khóa nó lại**, khác hẳn khuôn tia sét và hộp vàng của họ. Spec nhận diện ngày 09/11 đã cấm cặp đen–vàng, nhưng hai video Nvidia vẫn dùng.
2. **Mỗi video có 3 phương án**, chạy Test & Compare trong Studio (bạn làm), và ghi kết quả vào `theo-doi.csv`.
3. **Tiêu đề một móc:** `[sự kiện + số]: [một câu hỏi Việt Nam]?`. Bỏ "SỐC", bỏ dấu chấm than, bỏ cách chồng hai móc.
4. **Không dùng mặt người do AI tạo theo kiểu ảnh thật** (như thumbnail Grab). Nó làm giảm lòng tin, và nếu trông như thật thì phải khai nội dung tổng hợp.

**Mục tiêu:** CTR 7 ngày ≥ 5% (mốc trong spec cho G+30).

### 5.2 Giữ chân: 60 giây đầu và độ sâu

1. **Các sửa P0–P2 ngày 14/11 đã có trong code nhưng chưa video nào được kiểm.** Video `lo-hong-7zip-ai` sắp đăng là phép thử đầu tiên. So đường giữ chân của nó với ba video ở mục 2.2: mục tiêu còn ≥ 75% ở giây 30 và ≥ 40% ở 50% thời lượng.
2. **Không đăng video "dài" dưới 7 phút** (2:21, 5:47). Tin chỉ đủ 2 phút thì làm Shorts. Tin cần giải thích thì làm 10–13 phút, có cơ chế, có tiền lệ và có bảng Việt Nam, như họ làm.
3. **Thêm đường giữ chân vào sổ.** Analytics đã cho đọc `audienceWatchRatio` theo từng 1%. Nên ghi tỉ lệ còn xem ở giây 30 và ở 50% thời lượng, không chỉ `giu_chan_30s`.

### 5.3 Shorts: tăng lên vì đang là nguồn khám phá duy nhất

- Giữ **2 Shorts/ngày**, chọn đề tiêu dùng có giá cụ thể.
- Mỗi Short gắn **video liên quan** trỏ về video dài cùng chuỗi (bạn làm trong Studio).
- Kiểm tra Short Grab chỉ có 1 view: xem trạng thái hạn chế và bản quyền nhạc trong Studio.

---

## 6. Đánh giá lại dự án (pipeline)

### 6.1 Cái đang tốt

- Kỷ luật nguồn: số nào cũng có `[#id]`, kiểm bằng máy, có phản biện. Đây là lợi thế dài hạn và là thứ phân biệt kênh khi bị xét nội dung nguyên bản.
- Hạ tầng đo đã đủ dùng: đồng bộ view hằng ngày, Analytics, Reporting API cho CTR, cột đối thủ.
- Giọng, âm thanh và nhịp đã được sửa theo đo đạc thật (−14 LUFS, giọng phụ, bồi dần).

### 6.2 Cái đang lệch

| Vấn đề | Bằng chứng | Hệ quả |
|---|---|---|
| **Ngưỡng chất lượng đổi theo nghiên cứu, không theo số của mình** | Ngày 09/11 đặt ảnh đời thật ≤ 15%; ngày 10/11 đổi thành ≥ 45%; ngày 14/11 lại đổi thành stock ≤ 10% | Mỗi đợt video được dựng theo một chuẩn khác, không so được với nhau |
| **Đầu tư máy nhiều hơn vòng học** | 135 commit / 37 module so với 6 video dài và 7 sub | Mỗi nâng cấp chưa kịp được đo trên video thật đã có nâng cấp tiếp |
| **Luật quyết định dựa trên view tương đối** | "0,5× / 3× trung vị" khi trung vị khoảng 100 view | Luật không bao giờ kích hoạt có ý nghĩa |
| **Mục tiêu giờ đăng không khả thi với hai điểm duyệt** | 0/3 lần đăng sớm hơn họ | Chiến lược phụ thuộc vào một điều kiện chưa từng đạt |
| **Phong cách thumbnail không bị khóa** | 5 phong cách trong 6 video | Không tích lũy được nhận diện |

### 6.3 Đề xuất vận hành 14 ngày tới (15/11 → 29/11)

1. **Đóng băng tính năng pipeline**, chỉ sửa lỗi. Mọi ý tưởng nâng cấp ghi vào danh sách chờ, xét lại ngày 29/11 dựa trên số liệu.
2. **Đổi luật quyết định** sang ngưỡng tuyệt đối khi kênh còn nhỏ (sửa `docs/quy-tac-quyet-dinh.md`):
   - CTR 7 ngày < 3%: đổi thumbnail ngay (Test & Compare).
   - Còn xem ở giây 30 < 70%: xem lại hook trước video kế tiếp.
   - AVD < 30%: xem lại độ dài và cấu trúc.
   - Một video ≥ 1.000 view trong 7 ngày: làm thêm 2 tập cùng chuỗi.
3. **Định vị "tầng thứ hai"** (mục 4.2) cho 10 video dài kế tiếp, cộng 2 Shorts/ngày.
4. **Khóa một khuôn thumbnail** trước video kế tiếp.
5. **Ngày 29/11 xem lại:** 10 video dài cùng chuẩn dựng, cùng khuôn thumbnail và cùng định vị là đủ để thấy CTR và giữ chân có nhích lên hay không.

---

## 7. Bổ sung (chiều 15/11): toàn cảnh cạnh tranh và chỗ người xem bỏ đi

### 7.1 Ai khác làm cùng đề

Nguồn: YouTube Data API `search.list`, bộ lọc khu vực VN, tiếng Việt, video đăng từ 01/11, sắp theo view, đo lúc 15/11.

| Đề | Ai thắng (view) | Mình | Đọc |
|---|---|---|---|
| Jensen Huang / bê bối Nvidia | BBC Tiếng Việt 208 N, ĐTN 127 N, Bàn Cờ Quân Sự 110 N, VTC 103 N, VTV24 83 N, **Mọt 83 N**, Bàn Cờ Thế Sự 80 N | 3.114 (video xin lỗi), 150, 27 | Cầu rất lớn nhưng đông: đài lớn và các kênh "bàn cờ" địa chính trị đều làm. **Kênh "GIẢI MÃ QUÂN SỰ" (453 sub, lập 01/11) đạt 22,5 N** với góc riêng "vì sao tình báo Mỹ lo hơn chuyện tình cảm?" |
| Cấm nhập điện thoại cũ | **Vật Vờ 249 N, Dương Dê 172 N** (đăng 03–04/11, ngay sau tin) | 93 (đăng 10/11) | Mình đi sau **7 ngày**, khi các kênh công nghệ lớn đã chiếm đề |
| Grab giảm phí | Báo đài 4–38 N; Góc Nhìn Podcast 6 N với góc "Xanh SM ép Grab" | 120 | Đề do báo đài chiếm; kênh nhỏ chỉ sống được nhờ góc so sánh |
| Microsoft 365 sập | VTC 9,1 N, Mọt 7,8 N, còn lại dưới 1,3 N | 2 | Trần nhu cầu thấp, khoảng 10 N cho cả thị trường |
| Lỗ hổng 7-Zip | Cao nhất **860 view** (Shorts của kênh 59 sub), còn lại dưới 400 | sắp đăng | Nhu cầu rất nhỏ, và toàn là Shorts của kênh mới tí hon |

**Phát hiện quan trọng nhất là thị trường đang ngập kênh tin tự động.** Kết quả tìm kiếm cho các đề Microsoft và 7-Zip phần lớn là kênh lập trong tháng 10–11/2026, có 3–300 sub, tên kiểu "Tin tức hôm nay", "Bản tin AI mỗi ngày", "Mạch Tri Thức", "TINTUCNEWS", "Tnews24h", "News Focus VN", đều đăng bản tin 1–2 phút. Trong mắt thuật toán và người xem, một video 2 phút tóm tin với giọng tổng hợp **trông giống hệt nhóm này**. Đây là lý do mạnh nhất để không làm video dài kiểu tóm tin (Microsoft 2:21, 7-Zip 2:15).

Có hai kênh nhỏ thắng được, và chúng giống nhau ở chỗ có **một lăng kính riêng nhất quán**: Mọt (công nghệ × túi tiền Việt Nam) và Giải Mã Quân Sự (mọi tin qua góc tình báo/quân sự). Không kênh nhỏ nào thắng bằng cách đăng nhanh hơn.

### 7.2 Người xem bỏ đi ở đâu

Đây là đường giữ chân đủ 100 điểm của 3 video có số. Các cú rơi lớn nhất được khớp với phụ đề tại đúng giây đó.

| Video | Tiêu đề hứa | 25 giây đầu nói gì | Rơi mạnh nhất |
|---|---|---|---|
| CEO Nvidia xin lỗi | Bê bối, Việt Nam phải xin phép mua chip | "Năm ngoái Mỹ bắt chip AI xuất sang Malaysia và Thái Lan…", "Mình đọc lại văn bản gốc thì thấy không phải vậy…". **Bê bối chỉ được nhắc ở giây 19–24** | −7 điểm ở 0:19; mất 33% trước 0:49 |
| Cấm iPhone cũ | "Dân buôn ôm nợ, người dùng sắp mua máy đắt gấp đôi?" | "Có thật là mới không? Trong chính thông tư đó có một chi tiết lạ… lệnh cấm 8 năm tuổi" | **−7 điểm ở 0:09 và −7 ở 0:14**, ngay câu "chi tiết lạ / văn bản cũ" |
| Grab giảm phí | "Tiền về túi ai?" | 2.000 đồng → 3.000 tỷ → túi ai? → "một dòng nhỏ… bảng phí có hạn dùng" | **−11 điểm ở 0:19 và −9 ở 0:24**, đúng lúc mở mạch thứ tư |

Ba lỗi lặp lại:

1. **Tiêu đề và mở đầu lệch nhau.**
   - Tiêu đề iPhone hứa "đắt gấp đôi", nhưng mở đầu lại bảo "lệnh cấm này chẳng có gì mới". Góc phản bác như vậy rút mất lý do để người xem ở lại.
   - Tiêu đề Nvidia hứa bê bối, nhưng mở đầu nói luật xuất khẩu.
2. **Lời dẫn nói về chính việc kể chuyện**, như "mình đọc lại văn bản gốc", "có một chi tiết lạ", "một dòng nhỏ ít ai đọc tới", "kênh đã kể ở hai video trước, đường dẫn dưới mô tả" (video Jensen). Đối thủ không dùng câu nào kiểu này. Họ **kể thẳng chuyện**:
   - mốc giờ cụ thể (giờ Mỹ đổi sang giờ Việt Nam);
   - sự kiện, rồi số leo thang;
   - một người Việt cụ thể (nhân viên kinh doanh ở TP.HCM, lập trình viên ở Huế);
   - một giá cụ thể (thanh RAM 7,49 triệu ở CellphoneS);
   - một câu của giọng phụ.

   Tất cả trong 40 giây.
3. **Quá nhiều câu hỏi mở cùng lúc.**
   - Video Grab mở 4 mạch trong 25 giây.
   - Video Jensen hỏi 4 câu trong 30 giây đầu ("ai nắm quyền? ai đã đặt chip? có phải bỏ giữa chừng? nên nghe câu gì?").
   - Đối thủ chỉ treo **một** câu hỏi, rồi kể chuyện để dẫn tới câu đó.

Điểm sáng: đường của video iPhone **nằm phẳng ở 34% từ phút 3:40 đến phút 7:00**. Người đã qua được 40 giây đầu thì xem gần hết. Phần thân bài không phải vấn đề chính; vấn đề nằm ở 40 giây đầu.

Lưu ý thêm: video Jensen từ chức (27 view) **đã chọn góc "tầng thứ hai"** ("video này chỉ nói chuyện sau khi ông đi"), nhưng tiêu đề lại đóng gói như tin nóng ("SỐC: … bất ngờ từ chức!") và video ra sau khi BBC, VTC, Mọt đã phủ đề. Nghĩa là góc tầng thứ hai **phải được nói rõ ngay trong tiêu đề và thumbnail** thì mới có tác dụng.

### 7.3 Cảnh báo trước khi đăng `2026-11-15-lo-hong-7zip-ai`

- Video dài 2:15, đăng dạng video dài, và cả 3 tiêu đề đều mở bằng "CẢNH BÁO / BẤT NGỜ / SỐC".
- Trên toàn YouTube Việt Nam, đề này chưa video nào vượt 860 view, và gần như toàn là Shorts của kênh tin tự động.
- Mở đầu kịch bản kết thúc bằng câu "Rất bất ngờ." Đây đúng loại câu bình luận rỗng mà thẻ phong cách cấm.
- **Đề xuất:** không đăng dạng video dài. Cắt thành 1–2 Shorts (đề có tính hướng dẫn: "máy bạn có dính không, vá thế nào") rồi đăng sáng mai. Đây là quyết định của bạn ở điểm duyệt, mình chưa đổi gì.

### 7.4 Cập nhật luật cho kịch bản (đề xuất, chưa sửa `docs/phong-cach-kich-ban.md`)

1. **40 giây đầu phải kể chuyện:** mốc thời gian, sự kiện, số, một người Việt hoặc một giá cụ thể, rồi **một** câu hỏi. Không dùng câu nói về việc mình đọc tài liệu hay tìm thấy chi tiết.
2. **Câu hỏi trong tiêu đề phải được khẳng định trong 15 giây đầu**, không được phản bác. Nếu góc là "tin này phóng đại" thì tiêu đề phải nói thẳng điều đó.
3. **Không trỏ người xem đi chỗ khác** (video trước, mô tả) trong 60 giây đầu.
4. **Đề có trần nhu cầu dưới 10 N, hoặc đã chậm hơn 48 giờ**, thì làm Shorts, không làm video dài.

---

## 8. Việc còn thiếu dữ liệu

- CTR và lượt hiển thị của 4 video không có số tay. Reporting API sẽ tự điền từ 16/11; xem `memory/ctr-reporting-api-kiem-don-vi.md` để đối chiếu đơn vị.
- Đường giữ chân của 3 video gần nhất: chờ Analytics cập nhật (khoảng 17–18/11).
- Giữ chân và CTR của đối thủ: không đo được vì vidIQ hết credit. Số view và breakout ở mục 3 là số công khai đo ngày 14/11.
- View 0 của video Microsoft: cần kiểm trong Studio xem có bị hạn chế không hay chỉ do bộ đếm trễ.
