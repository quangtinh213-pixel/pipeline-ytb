# Chất lượng hình ảnh và bước "đạo diễn" cảnh

Ngày: 09/11/2026 · Trạng thái: chờ bạn duyệt spec
Spec đi cùng: `2026-11-09-dinh-vi-doi-dau-van-hanh-design.md` (định vị, vận hành, cổng chạy khô) và `2026-11-09-nhan-dien-moi-design.md` (lớp màu, bộ nhân vật).

## 1. Mục tiêu và phạm vi

Làm cho hình ảnh video **sắc nét hơn về kỹ thuật** và **có ý đồ, chiều sâu, không khô khan** ở từng phân cảnh. Claude đóng vai đạo diễn: chỉ đạo từng cảnh có ý nghĩa trước khi chọn mẫu và hình.

**Trong phạm vi (bạn chọn 09/11/2026):** (A) độ nét kỹ thuật của file; (B) bước đạo diễn; (C) độ phong phú của cảnh minh họa; (D) chữ và bố cục; (E) chỉ số đo "độ khô".
**Ngoài phạm vi:** ảnh/clip đời thật chất lượng hơn, mẫu bản đồ, sơ đồ lớn dần, ảnh minh họa AI (bạn không chọn; để sau); đổi phong cách isometric.

## 2. Hiện trạng đã đo

Nguồn: video `videos/2026-11-15-nvidia-siet-chip/final.mp4` (và `ffprobe` cả video `goi-ai-dang-tien`), 6 khung tĩnh, mẫu `templates/canh/minh-hoa.html`, `tttc/chat_luong.py`. **Chưa xem video ở dạng chuyển động.**

- **Kỹ thuật:** 1920×1080, H.264 High, 30 fps; bitrate video 3,19 Mbps (nvidia) và 3,07 Mbps (goi-ai). Nền gradient có dải màu (banding) thấy được khi tăng tương phản ×3; bằng mắt thường chắc nhẹ, YouTube nén lại có thể làm nặng thêm. `hyperframes render` (0.9.26) có `--video-bitrate`, `--crf`, `--max-bitrate`, `--keyframe-interval`; `render.sh` đang dùng `--quality delivery`.
- **Sân khấu cố định:** `minh-hoa` luôn có tấm nền `nen-dat.svg`, vật chính đặt giữa (600×520 ở toạ độ cố định), tối đa hai đạo cụ ở hai vị trí cố định, nhãn trên đầu. Biến thể có sẵn: hình SVG, 4 kiểu vào cảnh (`vao`), chuyển động lặp (`dong`), thị sai trôi nhẹ. Không có camera, không có phông theo chủ đề. 4/6 khung tôi xem dùng cùng một sân khấu.
- **Bộ đo hiện có** (`tttc.chat_luong`): độ dài cảnh, tỉ lệ nhóm mẫu, số cảnh liền cùng mẫu, sự kiện hình/phút, hiệu ứng âm thanh/phút, tốc độ đọc. Không đo ý nghĩa hay đa dạng sân khấu.
- **Chưa rõ:** một dòng phụ bị mờ ở khoảng giây 290 của video nvidia; có thể là hiệu ứng hiện dần hoặc lỗi (xem mục 6).

## 3. A. Độ nét kỹ thuật của file

**Thử nghiệm:** dựng cùng một video (đoạn 2–3 phút đủ cảnh gradient và chữ nhỏ) bằng bốn cấu hình:

| # | Cấu hình |
|---|---|
| 1 | Hiện tại (`delivery`) |
| 2 | `--video-bitrate 8M --max-bitrate 12M --keyframe-interval 2` |
| 3 | Như 2 + hạt nhiễu mịn (1–2%) phủ nền gradient để chống banding |
| 4 | Như 3, tải lên riêng tư ở 1440p (render lớn hơn) |

Ghi cho mỗi cấu hình: thời gian render, kích thước file, thời gian tải lên. Xem lại **trên YouTube ở 1080p** (không xem file gốc) và so banding, độ rõ chữ nhỏ, độ mịn đường viền.

**Chọn:** cấu hình rẻ nhất mà banding không còn thấy được trên YouTube; ghi lý do vào `docs/nghien-cuu/`. Con số 8 Mbps lấy từ khuyến nghị YouTube theo hiểu biết của tôi, chưa kiểm lại. Cái giá dự kiến: file khoảng 2,5 lần (video 8 phút từ ~210 MB lên ~500 MB); thời gian render và tải lên tăng, mức tăng chỉ biết sau thử.

**Nghiệm thu:** cấu hình đã chọn được ghi vào `render.sh` làm mặc định; thời gian render và tải lên đo được; `dung.check_av` vẫn rỗng.

## 4. B. Bước "đạo diễn"

### 4.1 Nguyên tắc đạo diễn (ghi vào `video-dung/SKILL.md`)
1. **Hình bổ nghĩa, không chép lời.** Mỗi cảnh phải trả lời: cảnh này giúp người xem hiểu hay cảm thấy điều gì mà lời đọc chưa tự nói ra?
2. **Mỗi beat có một khoảnh khắc nhấn** (đỉnh) và một nhịp thở trước hoặc sau nó.
3. **Ẩn dụ phải kiểm được.** Hình ẩn dụ không được thêm khẳng định không có nguồn (ví dụ không vẽ đám đông giận dữ khi nguồn không nói về phản ứng công chúng). Mọi số trên màn hình vẫn có `nguon_id`.
4. **Đa dạng có chủ đích:** đổi phông, vật chính, bố cục khi ý đổi, không đổi chỉ để đổi.

### 4.2 Vị trí trong quy trình
`/video-dung`: `giong` → `chia` → **`dao-dien`** → `canh` → `hinh` → `render`... Thêm bước `dao-dien` vào `trang-thai.json` (có giờ bắt đầu/kết thúc theo H1 của spec 1). Video cũ không có `dao-dien.json` vẫn chạy như hiện nay (`canh.json` viết tay vẫn hợp lệ).

### 4.3 `dao-dien.json`
Mỗi cảnh (theo `canh-khung.json`, đã có mốc và lời đọc) một mục:

| Trường | Ý nghĩa | Bắt buộc |
|---|---|---|
| `y` | Người xem phải hiểu/cảm thấy gì ở cảnh này | mọi cảnh |
| `nhip_cam_xuc` | `mo`, `leo`, `dinh`, `dao-chieu`, `ha`, `chot` | mọi cảnh |
| `trong_diem` | `true` với cảnh mở bài, số lớn, đảo chiều, kết, đỉnh của beat | mọi cảnh |
| `an_du` | Hình ẩn dụ và vì sao nó đúng với nguồn | cảnh trọng điểm |
| `san_khau` | Phông theo chủ đề (mục 5) | mọi cảnh minh họa |
| `vat_chinh`, `dao_cu` | Tên SVG trong thư viện; thiếu thì ghi vào `hinh-thieu.json` | mọi cảnh minh họa |
| `may_quay` | `dung`, `day-vao`, `keo-ra`, `lia`, `he-lo` | cảnh trọng điểm |
| `am_thanh` | Gợi ý hiệu ứng/nhạc theo khoảnh khắc | tùy chọn |
| `dan` | Biểu cảm và góc nhìn của nhân vật (bộ nhân vật, spec 2) | tùy chọn |

Cảnh không phải trọng điểm: các trường tùy chọn nhận giá trị mặc định theo luật đa dạng (mục 7), `may_quay` mặc định `dung`.

### 4.4 Cách làm và giới hạn thời gian
- Cảnh trọng điểm chiếm khoảng **30%** số cảnh; chỉ cảnh này được chỉ đạo sâu. Phần còn lại theo luật đa dạng.
- Chia theo beat cho nhiều subagent chạy song song; một agent tổng hợp và kiểm nhịp cảm xúc toàn video.
- **Giới hạn khoảng 45 phút.** Vượt trong chạy khô thì giảm tỉ lệ cảnh trọng điểm (xuống ~20%), không bỏ bước.
- `canh.json` được **sinh** từ `dao-dien.json`; phần cơ học (mốc, `nguon_id`, `nhip`, ánh xạ biến mẫu) do script điền. Script sinh cảnh: đề xuất tên `tttc.dao_dien`.

### 4.5 Kiểm
1. `tttc.dao_dien` kiểm hợp lệ: mọi cảnh có `y`; cảnh trọng điểm có `an_du` và `may_quay`; `san_khau`, `vat_chinh`, `may_quay` thuộc danh sách có sẵn; mọi số trên màn hình có `nguon_id`.
2. **Giám khảo hình ảnh** (subagent độc lập, không chia sẻ ngữ cảnh) nhận `dao-dien.json` + bảng soi cảnh, chấm mỗi beat 1–5 theo bốn tiêu chí (ý nghĩa, đa dạng, chiều sâu, nhịp cảm xúc), chỉ ra cảnh khô và ẩn dụ vượt nguồn. Claude sửa; tối đa 2 vòng.
3. **Qua khi:** không beat nào dưới 3 ở bất kỳ tiêu chí nào và trung bình từ 4 trở lên. Ngưỡng là đề xuất, hiệu chỉnh sau chạy khô.
4. Bạn xem kết quả qua bảng soi ở điểm duyệt 2; không thêm điểm duyệt.

## 5. C. Mẫu cảnh phong phú hơn

- **`minh-hoa` mới:** thay tấm nền cố định bằng **phông theo chủ đề**, khởi đầu khoảng 6: phòng máy chủ/trung tâm dữ liệu, nhà máy/chip, cảng và chuỗi cung ứng, thành phố/tòa nhà, sàn giao dịch/tài chính, cơ quan nhà nước. Danh sách chốt khi đạo diễn thấy thiếu gì.
- **Bố cục tham số:** 1–4 đạo cụ với vị trí và tỉ lệ khai báo trong `canh.json`, thay cho toạ độ cố định. Giữ nguyên `vao`, `dong`, thị sai.
- **Camera:** `may_quay` áp lên "thế giới" của cảnh (`mh-the-gioi`): đẩy vào, kéo ra, lia, hé lộ. Mẫu khác (`so-lon`, `quy-trinh`, `so-sanh`, `thoi-gian`, `bieu-do`) chỉ nhận camera nếu rẻ; không bắt buộc đợt này.
- **Hàng đợi hình còn thiếu:** bước đạo diễn ghi `hinh-thieu.json`; vẽ thêm trong `svg/ve.py` theo `svg/README.md`; chạy `ap-dung` (spec 2) để sinh lại.
- **Phụ thuộc:** phông và hình mới phải dùng màu từ theme (spec 2, mục A). Làm mục C **sau** khi lớp màu xong để khỏi ghi cứng màu thêm lần nữa.
- Các tệp thay đổi dự kiến: `templates/canh/minh-hoa.html`, `templates/canh/dong.js`, `tttc/dung.py`, `tttc/canh.py`, `svg/ve.py`, test tương ứng.

**Nghiệm thu:** ba cảnh mẫu cho mỗi phông dựng được, không chữ tràn, không đè nhau; camera chạy mượt ở 30 fps trong render thật; `tttc.canh` 0 lỗi; test mới đi kèm.

## 6. D. Chữ và bố cục

1. **Điều tra trước:** dựng lại đoạn quanh giây 290 của video nvidia (cảnh số lớn "2 USD mỗi giờ") và xem chuyển động; xác định dòng phụ mờ là hiệu ứng hiện dần hay lỗi. Là lỗi thì sửa; là hiệu ứng nhưng mờ quá 1 giây trên thông tin chính thì rút ngắn.
2. **Phụ đề:** chia cụm theo nghĩa thay vì cắt giữa câu khi có thể; kiểu và vị trí nhất quán giữa nền tối, kem, vàng.
3. **Nhãn:** ≤ 5 từ, là ý chính, không lặp lời đọc (giữ luật hiện có).
4. **Kiểm tự động** thêm vào `chat_luong` hoặc bước soi hình: chữ không tràn khung; tương phản chữ/nền ≥ 4,5:1 lấy mẫu theo cảnh; cỡ chữ tối thiểu ở 1080p; vùng an toàn của YouTube.

**Nghiệm thu:** hai video hiện có chạy qua kiểm tự động và các lỗi phát hiện được xử lý hoặc ghi lý do giữ.

## 7. E. Chỉ số "độ khô" trong `chat_luong`

Thêm nhóm `do_kho` vào `MUC_TIEU`. Ngưỡng là đề xuất; **đo trước trên hai video hiện có để lấy mốc nền**, rồi hiệu chỉnh sau chạy khô. Bắt đầu ở mức cảnh báo; chuyển thành lỗi cho các chỉ số được xác nhận là hợp lý.

| Chỉ số | Đề xuất |
|---|---|
| Số phông khác nhau trong một video | ≥ 5 |
| Cảnh liền cùng phông | ≤ 2 |
| Cùng một vật chính lặp lại trong cửa sổ 8 cảnh | 0 |
| Cảnh trọng điểm có `an_du` và `may_quay` | 100% |
| Cảnh có chuyển động camera | ≥ 20% số cảnh |
| Bản đồ nhịp cảm xúc có đủ mở, đỉnh, đảo chiều, chốt | có |
| Điểm giám khảo hình ảnh | theo mục 4.5 |

Các chỉ số đọc từ `dao-dien.json`; video cũ không có tệp này thì chỉ chạy các chỉ số tính được từ `canh.json` (số phông, vật chính lặp).

## 8. Tích hợp với hai spec kia

- **Spec 1:** bước `dao-dien` nằm trong khối 11:00–13:30 của đồng hồ ngày; H2 thu hẹp còn phần cơ học; cổng chạy khô thêm tiêu chí độ khô và giám khảo.
- **Spec 2:** màu của phông và hình mới lấy từ theme; bước đạo diễn chọn biểu cảm/góc nhân vật từ `nhan-vat/kit.json`.

## 9. Thứ tự làm

1. **Đo nền:** chạy E trên hai video hiện có; điều tra dòng mờ (mục 6.1); thử nghiệm bốn cấu hình render (mục 3).
2. **Sau khi spec 2 xong lớp màu:** mẫu cảnh phong phú (C) và hàng đợi hình còn thiếu.
3. **Bước đạo diễn (B)** nối vào `/video-dung`, chạy thử trên một video hiện có.
4. **Hiệu chỉnh trong ba ngày chạy khô:** ngưỡng độ khô, tỉ lệ cảnh trọng điểm, giới hạn thời gian.

## 10. Rủi ro

1. **Thời gian so với chiều sâu:** đạo diễn sâu hơn thì lâu hơn, trong khi đồng hồ ngày chật (spec 1, mục 5). Giảm bằng cảnh trọng điểm ~30%, chạy song song theo beat, giới hạn 45 phút.
2. **Ẩn dụ chung chung hoặc vượt nguồn:** giảm bằng nguyên tắc 4.1 mục 3 và giám khảo độc lập. Giám khảo là một agent Claude độc lập chứ không phải người xem thật; ngưỡng điểm chỉ là mốc, phép thử thật là retention sau khi đăng.
3. **Thư viện SVG thiếu hình:** mỗi hình mới phải vẽ trong `ve.py`; hàng đợi `hinh-thieu.json` có thể dài trong những video đầu.
4. **File lớn hơn, tải lên lâu hơn** (mục 3), và có thể thêm thời gian render từ camera/phông; chưa đo.
5. **Kết luận hình dựa trên khung tĩnh:** chưa xem video ở dạng chuyển động; mục 9.1 là để thay giả định bằng số đo.

## 11. Giả định cần bạn xác nhận khi đọc

- Cảnh trọng điểm ~30% và giới hạn 45 phút là đề xuất của tôi, chưa có số đo thật.
- Ngưỡng điểm giám khảo (không beat dưới 3, trung bình từ 4) và các ngưỡng ở mục 7 là đề xuất.
- Mục 6.1: tôi chưa biết dòng mờ ở giây 290 là chủ ý hay lỗi.
