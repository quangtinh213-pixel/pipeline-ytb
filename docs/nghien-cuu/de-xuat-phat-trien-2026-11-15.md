# Đề xuất phát triển dự án theo số liệu kênh và đối thủ

- **Ngày:** 15/11/2026
- **Dựa trên:** `docs/nghien-cuu/danh-gia-kenh-2026-11-15.md` (số kênh 01–15/11, `@MotCongNghe` đo 14/11, toàn cảnh đề đo 15/11), `theo-doi.csv`, và rà mã `pipeline/tttc/` hôm nay.
- **Trạng thái:** đề xuất, chưa sửa mã. Mỗi mục ghi rõ module sẽ đụng tới.

---

## 0. Nguyên tắc: phát triển "vòng học", không phát triển "máy dựng"

Số liệu nói một điều rõ: kênh không thua vì thiếu tính năng dựng, mà vì **bao bì (CTR 1,3–6,3%)**, **40 giây đầu (mất ~33% trước 0:49)** và **định vị trùng đề, đi sau**. Trong khi đó dự án có 135 commit, 37 module, nhưng chưa có công cụ nào tự trả lời câu "video này mất người xem ở câu nào, vì sao".

Vì vậy, "hoàn thiện chuyên sâu" ở đây nghĩa là:

1. **Gỡ những luật trong mã đang đẩy ngược số liệu** (mục 1). Đây là nợ, phải trả trước video kế tiếp.
2. **Xây vòng học tự động**: mỗi video đăng xong tự sinh bản khám nghiệm, sổ ghi đủ chiều để so sánh (mục 2).
3. **Đưa định vị "tầng thứ hai" và chuỗi vào radar** để máy chọn đề theo cách kênh nhỏ thắng được (mục 3).
4. **Mở rộng dữ liệu đối thủ từ một kênh sang thị trường đề** (mục 4).

Không làm trong 14 ngày (giữ đúng "đóng băng" của bản đánh giá, mục 6.3): hiệu ứng render mới, phong cách hình mới, nhân vật mới, đổi ngưỡng stock/ảnh thật. Danh sách chờ xét lại 29/11.

---

## 1. Ưu tiên 0 – sửa luật đang ngược số liệu (trước duyệt 2 của `nvidia-siet-chip`)

### 1.1 `tieu_de`: đảo chiều luật chấm tiêu đề – **đã làm 15/11**

> Đã làm: lỗi = từ giật gân, nhãn in hoa mở đầu ("CẢNH BÁO:", "NGUY CƠ:"), "!", hai móc, chữ tiếng Việt in hoa cả từ; cảnh báo = thiếu số, thiếu góc Việt Nam/túi tiền (thêm "giá", "phí", "tài xế", "khách"), phần trước ":" thiếu thực thể. Dấu ":" chỉ tính khi theo sau là khoảng trắng ("D:1", "15:30" không tính). Chấm lại 24 phương án cũ: 9 phương án giật gân đều bị lỗi, không bắt nhầm tiêu đề sạch nào. Chưa làm: cảnh báo góc tầng thứ hai (chờ trường `goc` ở mục 3.1). Lưu ý: tiêu đề sạch không đủ để thắng (Grab đạt 10/10 nhưng 80 view/24 giờ); luật này chỉ gỡ cái đang kéo ngược.

**Hiện tại** (`tttc/tieu_de.py`):
- `kiem()` báo **lỗi** nếu tiêu đề *không có* từ trong `TU_CAM_XUC` ("sốc", "cảnh báo", "bất ngờ", "sự thật"…).
- `cham_diem()` trừ điểm nếu không có "?" hoặc "!".
- `duyet.py` hiện các lỗi này trên `duyet-2.html`, nên mỗi lần duyệt, trang duyệt **khuyên thêm "SỐC"**.

**Số liệu:** tiêu đề "SỐC: … bất ngờ từ chức!" đạt 27 view; "Sự thật vụ Microsoft…chịu trận!" 0–2 view; cả 3 tiêu đề 7-Zip đều mở bằng CẢNH BÁO/BẤT NGỜ/SỐC. Tiêu đề thắng của đối thủ có dạng `[sự kiện cụ thể có số]: [một câu hỏi Việt Nam/túi tiền]?`, không dấu chấm than. Thị trường đang ngập kênh tin tự động dùng đúng các từ này.

**Đề xuất:**
| Luật | Mức |
|---|---|
| Có "SỐC", "CHẤN ĐỘNG", "KHẨN CẤP", chữ in hoa cả từ (≥ 3 chữ cái, trừ tên viết tắt như AI, RAM) | lỗi |
| Có "!" | lỗi |
| Hai móc chồng nhau (hai dấu "?"/"!", hoặc hai mệnh đề sau dấu ":") | lỗi |
| Không có con số (từ `nguon.json`) | cảnh báo |
| Không có góc Việt Nam/túi tiền | cảnh báo (giữ `GOC_VIET_NAM`) |
| Phần trước ":" không có thực thể cụ thể | cảnh báo (giữ `THUC_THE`) |
| Tiêu đề góc tầng thứ hai mà không có dấu hiệu phần mới ("48 giờ sau", "con số thật", "bảng giá", "sau khi…") | cảnh báo |

`TU_CAM_XUC` đổi tên thành `TU_GIAT_GAN` và chuyển sang danh sách **cấm**. Sửa `tests/test_tieu_de.py` theo. Ghi luật mới vào skill `yt-package` để phương án sinh ra đúng từ đầu.

### 1.2 Cổng định dạng thật ở chặng đăng

**Hiện tại:** `phong_cach.kiem_thoi_luong_thuc` chỉ ước thời lượng từ số từ kịch bản và chỉ **cảnh báo**. Video Microsoft 2:21 và 7-Zip 2:15 vẫn đi qua như video dài.

**Đề xuất:** trong `dang._guard`, đo `final.mp4` (ffprobe). Video dài < 7:00 thì **từ chối upload** dạng video dài, in lời khuyên "cắt thành Shorts". Chỉ cho qua khi có cờ `--cho-phep-ngan` kèm lý do ghi vào `trang-thai.json`. Cổng này nằm sau điểm duyệt nên không thay quyết định của bạn, chỉ bắt bạn quyết định có chủ ý.

### 1.3 Luật 40 giây đầu thành máy kiểm (`phong_cach`)

Bản đánh giá mục 7.2 tìm ra ba lỗi lặp lại bằng cách khớp tay đường giữ chân với phụ đề. Biến chúng thành hàm `phong_cach.kiem_mo_dau(script_md, wpm)`, chạy trên phần lời ứng với 40 giây đầu:

1. **Lời dẫn nói về việc kể chuyện** → cảnh báo. Mẫu: "mình đọc lại", "chi tiết lạ", "một dòng nhỏ", "ít ai đọc tới", "video trước", "dưới mô tả", "đường dẫn". Thêm vào `phong-cach/tu-cam.json` một nhóm riêng `mo_dau`.
2. **Quá một câu hỏi mở** trong 40 giây đầu → cảnh báo (Grab mở 4 mạch, Jensen hỏi 4 câu).
3. **Thiếu neo cụ thể** (không có mốc giờ/ngày, không có số có `[#id]`, không có người Việt hoặc giá cụ thể) → cảnh báo.
4. **Lệch tiêu đề**: từ khóa chính của tiêu đề đã chọn (thực thể + câu hỏi) không xuất hiện trong 15 giây đầu → cảnh báo. Chạy ở duyệt 2, khi đã có tiêu đề.

Thêm các luật này vào `docs/phong-cach-kich-ban.md` (bản đánh giá mục 7.4 đã soạn sẵn).

### 1.4 `giam_sat`: ngưỡng đo được

**Hiện tại:** "CTR < 4% sau 3 giờ" → báo động, gợi ý xoay bao bì. Nhưng CTR chỉ có từ Reporting API, trễ ~48 giờ, gộp theo ngày PST. Ngưỡng 3 giờ không bao giờ đo được bằng máy; chỉ dùng được khi bạn nhập tay từ Studio.

**Đề xuất:** đổi sang luật tuyệt đối của bản đánh giá (mục 6.3), đọc từ sổ:
- CTR 7 ngày < 3% → in "đổi thumbnail (Test & Compare)".
- Còn xem ở giây 30 < 70% → in "xem lại hook trước video kế tiếp".
- AVD < 30% → in "xem lại độ dài/cấu trúc".
- ≥ 1.000 view trong 7 ngày → in "làm thêm 2 tập cùng chuỗi".

Chạy cuối `dong-bo-view.py` mỗi tối, ghi vào log. Đồng thời viết lại `docs/quy-tac-quyet-dinh.md` (luật "0,5×/3× trung vị" vô nghĩa khi trung vị ~100 view).

---

## 2. Ưu tiên 1 – vòng học tự động

### 2.1 Mở rộng sổ `theo-doi.csv`

Hiện sổ có 12 cột, phần lớn trống. Không thể trả lời câu "khuôn thumbnail nào thắng", "tầng thứ hai có hơn trùng đề không", "Shorts nào kéo về video dài". Thêm cột (`theo_doi.EXTRA`, có `migrate`):

| Cột | Điền bằng | Dùng để |
|---|---|---|
| `dang` | `dang` lúc upload (`dai`/`short`) | tách hai loại khi tính trung vị (hiện sổ trộn chung) |
| `thoi_luong` | ffprobe lúc upload | luật 1.2, so giữ chân theo độ dài |
| `chuoi` | `chu-de.md` (mã chuỗi, mục 3.2) | đo hiệu ứng chuỗi |
| `goc` | `chu-de.md` (`tang-1` / `tang-2`) | so hai định vị |
| `khuon_thumb` | `dong-goi.json` (mã khuôn) | so khuôn, chỉ khi đã khóa khuôn |
| `hien_thi_7d` | Reporting API (cùng CSV với CTR) | CTR thấp do ít hiển thị hay do bao bì |
| `con_50pct`, `avd_pct` | Analytics `audienceWatchRatio` / `averageViewPercentage` | luật 1.4 |
| `roi_lon_nhat` | bản khám nghiệm 2.2 (vd `0:19 −11`) | nhìn nhanh trong sổ |
| `nguon_chinh` | Analytics `insightTrafficSourceType` | trang chủ / đề xuất / Shorts / tìm kiếm |

Lưu ý: `giu_chan_tai` đã gọi Analytics; thêm `con_50pct` chỉ là gọi thêm một mốc trên cùng đường.

### 2.2 Bản khám nghiệm tự động cho từng video (`tttc.kham`)

Việc mất nhiều công nhất trong bản đánh giá (mục 7.2) là khớp tay cú rơi giữ chân với câu nói. Tự động hóa:

1. Lấy đường `audienceWatchRatio` 100 điểm (Analytics, 7 ngày đầu, khi video đủ 9 ngày; hoặc sớm hơn với cờ `--som`).
2. Tìm các cú rơi > 5 điểm giữa hai mốc liền kề, bỏ qua điểm 0–2%.
3. Đổi mốc % sang giây, tra `phu-de.srt` và `canh.json` để lấy **câu đang nói** và **loại cảnh đang chiếu** tại đó.
4. Ghi `videos/<slug>/kham-nghiem.md`: bảng cú rơi, ba câu bị rơi mạnh nhất, so với mục tiêu (≥ 75% ở giây 30, ≥ 40% ở 50%), kèm CTR/hiển thị.
5. `dong-bo-view.py` gọi `kham` khi video đủ tuổi, điền `roi_lon_nhat` vào sổ.

Sau 10 video, gom các câu bị rơi vào `phong-cach/tu-cam.json` nhóm `mo_dau` (mục 1.3): luật viết được sinh ra từ số của chính kênh, không phải từ nghiên cứu một chiều.

### 2.3 Báo cáo tuần (`tttc.bao_cao`)

Chủ nhật tối, sau đồng bộ view, sinh `docs/bao-cao/<yyyy-ww>.md`:
- Video dài và Shorts **tách riêng**: trung vị view 7 ngày, CTR, còn xem giây 30, AVD.
- So theo nhóm: `goc` tang-1 vs tang-2, có chuỗi vs không, khuôn thumbnail.
- Danh sách luật 1.4 đã kích hoạt trong tuần và việc đã làm.
- Mẫu nhỏ thì ghi rõ "n = …, chỉ là hướng nghiêng".

Đây là đầu vào duy nhất cho buổi xem lại 29/11.

---

## 3. Ưu tiên 2 – chọn đề theo cách kênh nhỏ thắng được

### 3.1 Radar trả về **định dạng**, không chỉ điểm

**Hiện tại:** `radar.cham_diem = soc + so_lon + 2 × goc_vn`, ngưỡng 4, trả danh sách đề xếp hạng.

**Số liệu:**
- Đề nổ của đối thủ: sự kiện vĩ mô × "Việt Nam được/mất gì".
- Đề mình đi sau 7 ngày (iPhone cũ) hoặc trần nhu cầu thấp (Microsoft ~10 N cả thị trường, 7-Zip < 1 N) đều chết ở dạng dài nhưng sống ở Shorts.

**Đề xuất:** thêm ba tín hiệu, mỗi đề nhận một **khuyến nghị định dạng**:

| Tín hiệu | Cách đo | Tác động |
|---|---|---|
| `gia_vn` | Có cái giá cụ thể cho người Việt (giá, việc, xuất khẩu, tiền gửi)? 0–2 | thay `goc_vn` chung chung |
| `tre_gio` | Giờ hiện tại trừ giờ tin gốc | > 48 giờ → chỉ Shorts |
| `tran_nhu_cau` | `search.list` (VN, tiếng Việt, 7 ngày, sắp theo view): view video top 1 | < 10 N → chỉ Shorts |
| `ho_da_dang` + mình trễ > 2 giờ | đã có từ RSS | bắt buộc góc `tang-2` |

Đầu ra mỗi đề: `dai-tang-1`, `dai-tang-2`, `shorts`, hoặc `bo`. Ghi vào `chu-de.md` cùng lý do. Chi phí quota: `search.list` 100 đơn vị/lần, 10–15 đề/ngày là ~1.500/10.000.

### 3.2 Chuỗi (series) thành đối tượng hạng nhất

Đối thủ làm 6 video Nvidia trong 7 ngày, nối nhau; mình làm 3 video Nvidia rời rạc.

- Tệp `chuoi.json` ở gốc: mã chuỗi, tên, playlist, danh sách tập, ngày tập cuối.
- Radar cộng điểm cho đề nối được một chuỗi còn nóng (tập cuối ≤ 5 ngày), và gợi ý góc tập kế ("48 giờ sau", "con số thật").
- `dang`: thêm video vào playlist của chuỗi (đã có `playlist_id`, chỉ cần theo chuỗi), mô tả tự gắn "Tập trước/Tập sau".
- Màn hình kết thúc và video liên quan của Shorts vẫn do bạn làm trong Studio; `bao_cao` in danh sách việc tay cần làm.

### 3.3 Shorts: luồng riêng, 2/ngày

Shorts là nguồn khám phá duy nhất chạy đều (940, 888 view). Hiện Shorts chỉ là phần phụ "dựng tối nếu máy rảnh".
- Radar xuất thêm 2 đề `shorts`/ngày từ nhóm tiêu dùng có giá cụ thể, không cần có video dài đi kèm.
- Tiêu đề Shorts dùng cùng luật 1.1.
- Short nào cùng chuỗi với video dài thì mô tả trỏ về video dài.

---

## 4. Ưu tiên 3 – dữ liệu đối thủ và thị trường đề

**Hiện tại:** chỉ theo dõi `@MotCongNghe` qua RSS (15 video gần nhất, view hiện tại); vidIQ hết credit nên không có CTR/giữ chân đối thủ.

**Đề xuất:**
1. **Tệp `doi-thu.csv`**: mỗi tối chụp view của video đối thủ bằng `videos.list` (1 đơn vị/50 video, gần như miễn phí) ở mốc 24 giờ và 7 ngày. Tính breakout = view 7 ngày / trung vị kênh. Bỏ phụ thuộc vidIQ cho số view.
2. **Mở danh sách kênh**: thêm các kênh có lăng kính riêng thắng được (bản đánh giá mục 7.1: Giải Mã Quân Sự, các kênh công nghệ lớn khi trùng đề tiêu dùng). `config.json:doi_thu` thành danh sách.
3. **Phân loại đề nổ**: gắn nhãn tay một lần cho video đối thủ (vĩ mô × VN / chân dung / kiến thức / sản phẩm nước ngoài / tiêu dùng trong nước), `bao_cao` tính breakout trung vị theo nhãn. Radar dùng bảng này làm trọng số loại đề, thay vì đoán.
4. **Đếm "kênh tin tự động" trên mỗi đề** (kênh lập < 60 ngày, < 500 sub trong top 20 `search.list`). Đề có > 50% là kênh loại này thì không làm dạng tóm tin.

Chỉ đọc tiêu đề, giờ đăng, số công khai; không lấy lời, hình của họ (giữ nguyên luật trong `radar`).

---

## 5. Thumbnail: khóa một khuôn – **đã chốt 15/11: khuôn `ho-so`**

6 video có 5 phong cách. Ba khuôn ứng viên được dựng thử trên cùng hai đề (Nvidia lá thư, Grab giảm phí): A khung Nhịp, B số lớn + đường nhịp, C hồ sơ nền kem. Bạn chọn **C**.

- Hàm: `tttc.thumb.ho_so(anh, nhan, so, hoi, out, ghi_cong, tam)`, hằng `thumb.KHUON = "ho-so"`.
  - Nền giấy kem kẻ dòng (màu `theme.kem`).
  - Bên trái ba tầng chữ mực: chủ thể ≤ 3 từ, con số làm chính có gạch đỏ (`sac.do`), một câu hỏi ≤ 3 từ.
  - Bên phải ảnh dán viền trắng, xoay nhẹ, có băng keo; nhân vật Nhịp ở góc dưới trái của ảnh.
  - Ghi công ảnh không đè lên chỗ badge thời lượng.
- Ba phương án chỉ khác chữ hoặc ảnh, mỗi lần đổi một biến để Test & Compare đọc được.
- `duyet.py` báo **lỗi** nếu một phương án trong `dong-goi.json` không ghi `"khuon": "ho-so"`.
- Skill `video-dung` bước 5.2 đã viết lại: bỏ `thumb.make`, `thumb.khung`, CoDesign và nền TobyFlow cho video dài; cấm mặt người do AI tạo trông như ảnh thật.

**Lưu ý số liệu:** thumbnail có CTR tốt nhất đến nay (6,3%, video CEO Nvidia xin lỗi) dùng khuôn gần giống đối thủ (viền vàng, hộp vàng, mặt Jensen). Nhưng video đó cũng ăn theo làn sóng đề xuất từ video của họ, nên chưa tách được phần nào nhờ khuôn. Chọn C là chọn nhận diện riêng (theo bản đánh giá mục 3.3 và 4.1), không phải vì số liệu đã chứng minh C hơn. Cần đo CTR 7 ngày của 5 video đầu dùng C; nếu trung vị < 3% thì xem lại khuôn ngày 29/11.

---

## 6. Lịch và cách đo

| Ngày | Việc | Module |
|---|---|---|
| 15–16/11 | 1.1 tiêu đề, 1.2 cổng thời lượng, 5 khóa khuôn (chờ bạn chốt khuôn) | `tieu_de`, `dang`, `duyet`, `thumb`, skill `yt-package`, `video-dung` |
| 16–18/11 | **8.2 Shorts dọc gốc** (trước lứa Shorts kế tiếp) | `dung.compose` nhánh Shorts, skill `video-dung` mục 7 |
| 17–18/11 | 1.3 kiểm 40 giây đầu, 1.4 giám sát + viết lại quy tắc quyết định | `phong_cach`, `giam_sat`, `docs/` |
| 18–21/11 | 2.1 cột sổ, 2.2 khám nghiệm (đường giữ chân 3 video mới có từ ~17–18/11) | `theo_doi`, `dong-bo-view.py`, `kham` mới |
| 22–24/11 | 3.1 radar định dạng, 3.2 chuỗi | `radar`, `dang`, `chuoi.json` |
| 25–27/11 | 2.3 báo cáo tuần, 4.1–4.2 `doi-thu.csv` | `bao_cao` mới, `radar` |
| 29/11 | Xem lại bằng báo cáo tuần | – |

**Tiêu chí 29/11** (10 video dài cùng chuẩn mới):
- CTR 7 ngày trung vị ≥ 4% (hiện: 1,3–6,3%, n = 2).
- Còn xem ở giây 30 trung vị ≥ 75% (hiện: ~85–96% ở 15 giây, rơi mạnh 0:09–0:24).
- Còn xem ở 50% thời lượng ≥ 35% (hiện: 15–34%).
- Ít nhất một video ≥ 1.000 view 7 ngày ngoài video đầu.
- Đạt ≥ 3/4: giữ hướng, mở lại danh sách chờ tính năng. Đạt ≤ 1/4: xem lại chọn đề (mục 3) trước khi đụng tới khâu dựng.

---

## 7. Việc cần bạn quyết

1. ~~Chốt một khuôn thumbnail~~ – đã chốt `ho-so` ngày 15/11.
2. Đồng ý **đổi định vị sang "tầng thứ hai" + chuỗi** cho 10 video dài kế tiếp.
3. Video `2026-11-15-lo-hong-7zip-ai` (2:15): bản đánh giá khuyên chỉ đăng Shorts; `dong-goi.json` đã có 2 Shorts. Bạn quyết ở điểm duyệt.
4. Thứ tự làm: đề xuất bắt đầu từ mục 1.1 + 1.2 vì rẻ nhất và đang gây hại trực tiếp.
5. Shorts 7-Zip đã duyệt (hẹn 16/11 và 17/11) vẫn dựng theo kiểu cũ (mục 8.2): đăng như đã duyệt để có thêm một điểm số so sánh, hay dừng lại chờ dựng dọc gốc.

---

## 8. Bổ sung tối 15/11: số liệu YouTube Studio

Nguồn: bản phân tích bạn dán từ YouTube Studio (số Studio, mình chưa tự truy vấn được). Bốn điểm, đối chiếu với số đã có và với mã:

### 8.1 Giữ chân đầu video dài: khớp, giữ hướng mục 1.3

- `E17SceQLG9I`: 97% → **72% ở giây 30** → 60% ở phút 1. Khớp đường giữ chân ở bản đánh giá mục 2.2 (67% ở 49 giây).
- Đồng ý với lời khuyên "đưa mâu thuẫn chính lên 10 giây đầu" và "báo trước câu trả lời nằm ở đâu". Hai chỗ cần chỉnh cho khớp số của kênh:
  - **Chỉ một vòng mở.** Câu trả lời được hứa chính là câu hỏi duy nhất của 40 giây đầu. Video Grab và Jensen mở 4 câu hỏi thì rơi mạnh nhất.
  - Câu mở mẫu "Tại sao một tập đoàn ngàn tỷ USD lại phải xin lỗi…" thiếu neo cụ thể. Theo luật 1.3, câu mở cần mốc thời gian, con số có nguồn, người Việt hoặc giá cụ thể.
- Mục tiêu giữ nguyên: còn ≥ 75% ở giây 30.

### 8.2 Shorts: chỉ 9,6–18,9% người xem ở lại. Đây là phát hiện mới và quan trọng nhất

**Đổi kết luận cũ.** Bản đánh giá mục 2.4 và 5.3 coi Shorts là "kênh khám phá duy nhất đang chạy đều" vì có 940 và 888 view. Số Studio cho thấy view đó đến từ việc YouTube đẩy Shorts lên feed, còn **81–90% người lướt qua ngay**. Short iPhone 15 Plus gần 1.000 view chỉ giữ được 9,64%. Tăng số lượng Shorts lúc này chỉ nhân thêm số lần bị lướt qua.

**Nguyên nhân tìm thấy trong mã** (`dung.compose`, nhánh Shorts; khung giây 0,5 và giây 3 của Short Microsoft và 7-Zip):
1. **Khung ngang thu nhỏ đặt giữa khung dọc.** Sân khấu 16:9 thu còn 0,5625 nên chỉ chiếm khoảng 1/3 chiều cao màn hình, phần còn lại là nền tối trống. Trên feed Shorts, hình như vậy trông như video quay ngang đăng nhầm.
2. **Cắt từ giữa video dài.** Skill `video-dung` mục 7 chọn đoạn "trọn ý" trùng ranh giới cảnh, nên Short 7-Zip mở bằng câu "Thứ nhất," và một cảnh gần trống. Short Microsoft không có dòng hook ở khung đầu.
3. Dòng `short_hook` chỉ là một băng chữ nhỏ ở trên, không phải câu nói đầu tiên.

**Đề xuất (mức ưu tiên 0 cho Shorts, làm trước lứa Shorts kế tiếp):**
- **Dựng dọc gốc:** cảnh đồ họa và số lớn bố trí lại cho khung 1080×1920 phủ kín. Ảnh và b-roll cắt dọc theo điểm giữ, không thu nhỏ cả sân khấu ngang.
- **Giây đầu:** chữ lớn nêu vấn đề sát sườn kèm số (vd "Cấm nhập máy cũ: iPhone 15 Plus 15,89 triệu?") nằm ngay khung 0, và câu nói đầu tiên là câu hook. Không mở bằng câu nối ("Thứ nhất", "Còn", "Vậy").
- **Kịch bản Short viết riêng** theo template Shorts (`docs/template-kich-ban.md`, hook 5–6 giây), dùng lại giọng và cảnh của video dài, không chỉ cắt một đoạn có sẵn.
- **Cắt khoảng lặng:** nghỉ giữa câu trong Shorts ≤ 0,1 giây (video dài đang 0,14/0,32 giây).
- **Đo:** thêm cột `o_lai_short` (tỉ lệ "ở lại xem") vào sổ. Chưa rõ Analytics API có trả số này không; trước mắt nhập tay từ Studio như CTR lúc đầu. Mục tiêu: trung vị ≥ 40% sau 10 Shorts dựng dọc gốc. Ngưỡng này là giả định, chỉnh sau khi có số.

Việc này là sửa khâu dựng, nhưng không trái với "đóng băng tính năng" ở mục 0: đây là điểm nghẽn đã đo được, không phải nâng cấp theo nghiên cứu một chiều.

### 8.3 Chuyển đổi đăng ký: 7 sub trên khoảng 2.000 người xem riêng biệt (~0,35%)

- Đồng ý không kêu gọi chung chung. Lời mời đăng ký gắn với **tập kế tiếp của chuỗi** (mục 3.2): "Tập sau: … – bấm đăng ký để xem khi ra".
- Chỉ hứa tập sau khi `chuoi.json` đã có tập đó trong kế hoạch, không hứa nội dung chưa chắc làm.
- Đặt ở phần kết, sau câu trả lời tiêu đề và trước câu mời đoán số. Không đặt trong 60 giây đầu (luật 1.3).
- Thêm vào `docs/phong-cach-kich-ban.md` mục kết và cho `phong_cach.kiem` kiểm: video thuộc chuỗi thì 80 từ cuối phải có câu nhắc tập sau.
- "Chuyên mục cố định" là cùng ý với "lăng kính riêng nhất quán" (bản đánh giá mục 7.1). Chốt tên chuyên mục khi chốt định vị (mục 7, việc 2).

### 8.4 Cầu nối Shorts → video dài: đồng ý, nhưng làm sau 8.2

- Đã có trong mục 3.2–3.3: chuỗi, Short cùng chuỗi trỏ về video dài. "Video liên quan" vẫn do bạn gắn trong Studio (`bao_cao` sẽ in danh sách việc cần gắn).
- Với 81–90% người lướt qua, cầu nối chưa có gì để chở. Thứ tự: sửa 8.2, rồi mới đo cầu nối.
- "Cắt 2–3 góc gây tranh cãi làm mồi": làm theo 8.2 (Short viết riêng, mở bằng hook), không cắt nguyên đoạn từ video dài.
