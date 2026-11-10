# Giọng văn kịch bản tự nhiên và phản biện chéo với agy

Ngày: 09/11/2026 · Trạng thái: chờ bạn duyệt spec
Spec đi cùng: `2026-11-09-dinh-vi-doi-dau-van-hanh-design.md` (H0 chỉ còn lo công thức và cấu trúc kịch bản, H3 gộp vào đây; cổng chạy khô thêm tiêu chí giọng văn); `2026-11-09-nhan-dien-moi-design.md` (giọng đọc VieNeu, từ đệm phải nghe thử với giọng đã chọn).

## 1. Mục tiêu và phạm vi

Kịch bản nghe như một người thật kể chuyện, đọc to không vấp, không văn máy (sáo rỗng, khuôn mẫu, từ ngữ đao to búa lớn). Sạch **ngay từ bản nháp**, để khỏi làm lại giọng, cảnh và render: cả hai video hiện có đều làm lại V1→V3 sau khi đã có giọng vì "mùi AI".

**Trong phạm vi:** danh sách cấm cứng; vai kể và tình huống cụ thể; mẫu giọng; nhịp và "không hoàn hảo"; quy trình biên tập ba lượt; cổng phản biện 2 vòng với agy; nghe thử 60 giây; kiểm trong code.
**Ngoài phạm vi:** công thức và cấu trúc kịch bản (spec 1, H0); kiểm số liệu và nguồn (`tttc.kiem` và subagent độc lập, giữ nguyên); chọn giọng TTS (spec 2); đổi giọng đọc.

Nguồn ý tưởng: hướng dẫn bạn dán ngày 09/11/2026 (năm kỹ thuật: danh sách cấm, vai kèm tình huống cụ thể, mẫu giọng, bẻ nhịp và chi tiết cụ thể, biên tập hai bước), điều chỉnh cho một kênh tin tức mà mọi con số phải có nguồn.

## 2. Hiện trạng đã đo

- `tttc.phong_cach.kiem` chỉ trả cảnh báo và **chỉ được gọi từ `tttc/duyet.py`** (hiện lên trang duyệt 1), không có lệnh chạy riêng và không chặn gì. Nó kiểm: 90 từ đầu có số có nguồn và dấu "?", 60 từ cuối có "?", độ dài 2.000–2.600 từ; "mùi máy": bộ ba "Một… Hai… Ba…", 8 cụm dịch thô (`DICH_THO`), rào đón quá 3 lần, dưới 10% câu ≤5 từ, kết nhai lại, **thiếu "điều kiện đổi ý"**.
- Lưu ý: tệp `kich-ban.md` của video nvidia (bản V3 đã đọc giọng và đăng) khác `kich-ban-v2.md` đã duyệt ở điểm duyệt 1: 100 câu, trung bình 20,3 từ, 27 câu dài hơn 28 từ; mốc nền dưới đây lấy từ `kich-ban-v2.md` và `kich-ban.md` của goi-ai-dang-tien.
- Hai kịch bản V3 đã duyệt (`nvidia-siet-chip/kich-ban-v2.md`, `goi-ai-dang-tien/kich-ban.md`) không dính cảnh báo nào và không chứa cụm nào trong danh sách cấm của bạn (grep 0 kết quả).
- Nhịp của hai kịch bản (mốc nền): 155 và 154 câu; trung bình 13,5 từ/câu; độ lệch chuẩn/trung bình 0,56; 12% câu ≤5 từ; 5–6 câu dài hơn 28 từ; chuỗi câu liền nhau cùng độ dài (±20% so với câu đầu chuỗi) dài nhất là 4; tính từ cảm thán (rất, vô cùng, cực…) 1 lần mỗi video; từ đệm đúng bốn cụm trong danh sách ở 3.4: 0 lần mỗi video.
- `agy` 1.5.3 chạy được ở chế độ không giao diện: một đoạn 5 câu mất 32 giây, trả `status`, `response`, `conversation_id`. Cờ `--json-schema` **không ép được** định dạng (câu trả lời vẫn là văn xuôi). agy bị từ chối khi muốn chạy lệnh. Chất lượng phản biện không đồng đều (chê "Mỹ bắt chip AI… phải có thêm giấy phép" là văn dịch thô, tôi cho là quá tay).
- Chưa đo agy trên kịch bản đầy đủ (~2.300 từ) và chưa nghe VieNeu đọc từ đệm hay câu lửng.

## 3. Thành phần

### 3.1 Danh sách cấm cứng
Tệp dữ liệu `pipeline/phong-cach/tu-cam.json` (đề xuất đường dẫn), bốn nhóm:
- **Từ và cụm:** đột phá, nâng tầm, hãy cùng khám phá, giải pháp hoàn hảo, "không chỉ… mà còn" (trong cùng một câu), bức tranh toàn cảnh, chiếc chìa khóa vàng, bước ngoặt.
- **Mở bài:** "Bạn đã bao giờ tự hỏi…", "Trong kỷ nguyên số ngày nay…" (kiểm ở 40 từ đầu).
- **Kết bài:** "Tóm lại…", "Hãy nhớ rằng…", "Hãy bắt đầu hành trình ngay hôm nay" (kiểm ở 60 từ cuối).
- **Dịch thô:** chuyển 8 cụm `DICH_THO` hiện có vào đây.

Quy tắc: kiểm trong phần "Lời đọc" không phân biệt hoa/thường; vi phạm là **Lỗi** (chặn duyệt 1), không còn chỉ cảnh báo; **ngoại lệ** là chữ nằm trong dấu ngoặc kép trích nguyên văn từ nguồn (`trich_dan`). Thêm mục mới chỉ cần sửa tệp dữ liệu. Có lệnh chạy riêng `python -m tttc.phong_cach <thư mục video>` thoát mã 1 khi có Lỗi.

### 3.2 Vai kể và tình huống cụ thể
Thay "chuyên gia" bằng tình huống: *một người theo dõi công nghệ, sáng nay vừa đọc xong các tài liệu gốc trong `nguon.json`, ngồi quán cà phê kể lại cho một đứa bạn thân chưa đọc. Giọng thẳng, hơi tự giễu khi hợp, từ ngữ hằng ngày, không thuật ngữ nếu không cần.*

**Ràng buộc của kênh tin tức (khác ví dụ bạn dán):**
- Người kể **không được bịa trải nghiệm cá nhân hay giai thoại** ("hồi mình nợ thẻ 50 triệu…", "3 giờ sáng, mắt díp lại…"). Kiểm sơ bộ: cảnh báo khi lời đọc có cụm kiểu "mình từng", "hồi mình", "có lần mình".
- "Show, don't tell" áp dụng lên **chất liệu thật**: số, ngày, câu trích, tên bảng giá, tên nơi chốn lấy từ nguồn. Ví dụ đời thường vẫn được dùng nhưng phải nói rõ là ví dụ ("hình dung thế này", "giả sử").

### 3.3 Mẫu giọng
- Thư mục `pipeline/phong-cach/mau-giong/` chứa 1–2 đoạn mẫu. Hạt giống đề xuất: hai đoạn tự nhiên nhất từ hai kịch bản đã duyệt (bạn chọn), cộng đoạn bạn tự viết hoặc có quyền dùng.
- Claude phân tích **một lần** nhịp câu, độ dài câu, từ đệm, thái độ, ghi `phan-tich-giong.md`; mọi video dùng lại bản này để giọng nhất quán qua 1 video/ngày. Đổi mẫu thì phân tích lại.
- **Không dùng lời của @MotCongNghe làm mẫu** (giữ ranh giới ở spec 1, mục 4.1). Nếu bạn muốn nới, nói rõ.

### 3.4 Nhịp và "không hoàn hảo"
Ngưỡng đặt **dưới mốc nền** của hai kịch bản đã duyệt để không đánh trượt kịch bản tốt; tất cả là cảnh báo, hiệu chỉnh sau chạy khô.

| Quy tắc | Ngưỡng |
|---|---|
| Câu ≤ 5 từ | ≥ 10% số câu (giữ; mốc nền 12%) |
| Độ lệch chuẩn / trung bình độ dài câu | ≥ 0,5 (mốc nền 0,56) |
| Câu liền nhau cùng độ dài (±20% so với câu đầu chuỗi) | không quá 4 câu liền (mốc nền: 4; bản đầu của tôi ghi 3 và sẽ đánh trượt chính hai kịch bản đã duyệt) |
| Câu dài hơn 28 từ | không quá 8 câu (mốc nền 5–6) |
| Tính từ cảm thán (rất, vô cùng, cực kỳ, khổng lồ…) | không quá 5 lần/video (mốc nền 1) |
| Từ đệm đời thường (kiểu như, nói thật là, đoạn này mới cấn, tính ra thì) | chỉ trong danh sách cho phép; không quá 15 lần/video (mốc nền 0) |
| Câu lửng, câu hỏi tu từ ngắn | cho phép, không bắt buộc |

Danh sách từ đệm lấy từ ví dụ bạn dán và **chốt sau khi nghe VieNeu đọc** (giọng máy có thể đọc lạ). Câu lửng phải thử với cách tách câu của `giong_vieneu` (mỗi câu một tệp wav, ngắt `pause_cau`).

### 3.5 Quy trình viết (mở rộng bước 3 của `video-moi`)
1. **Nháp** bằng khung giao việc ở Phụ lục A.
2. **Lượt 1:** "Đọc lại, gạch bỏ mọi câu sáo rỗng không thêm thông tin."
3. **Lượt 2:** "Viết lại sao cho đọc to thành tiếng không vấp, nghe như nói trực tiếp, không như đọc văn bản."
4. `python -m tttc.phong_cach` 0 Lỗi.
5. **Cổng phản biện 2 vòng với agy** (3.6).
6. `tttc.kiem` 0 lỗi và phản biện sự thật bằng subagent độc lập (bước 4 hiện có). Chạy **sau** mọi chỗ sửa giọng văn để số liệu và `[#id]` được kiểm lại.
7. **Nghe thử 60 giây** (3.7).
8. **Điểm duyệt 1.**

Hai lượt biên tập và mọi chỗ sửa theo agy **không được đổi con số, thẻ `[#id]`, câu cảnh báo "sơ bộ"/"mình tự tính"**; `tttc.kiem` ở bước 6 bắt các lỗi này.

### 3.6 Cổng phản biện 2 vòng với agy
**Phạm vi:** chỉ giọng văn tự nhiên. Số liệu và nguồn do `tttc.kiem` và subagent kiểm, vì agy ở chế độ không giao diện không mở được tài liệu gốc.

**Gọi agy:** `agy -p "<prompt tự chứa>" --output-format json --print-timeout 600s` (vòng 2 thêm `--conversation <id>`). Không dùng `--dangerously-skip-permissions`, không dùng `--json-schema`. Gửi phần "Lời đọc" dán nguyên văn (bỏ `[TRÊN MÀN HÌNH]`), kèm danh sách cấm, tình huống kể, `phan-tich-giong.md`. Prompt mẫu ở Phụ lục B.

**Vòng 1 (cuộc hội thoại mới, lưu `conversation_id`):** agy nêu tối đa 12 vấn đề, mỗi vấn đề gồm câu trích nguyên văn, loại (sáo rỗng, văn dịch, nhịp đều, khó đọc to, bịa trải nghiệm, từ cấm, đao to búa lớn), mức (nặng, vừa, nhẹ), gợi ý sửa ngắn; chấm 1–5 bốn tiêu chí (tự nhiên khi đọc to, đúng tình huống kể, nhịp, chi tiết cụ thể). agy không được viết lại cả đoạn, không được đổi con số.
**Triage:** Claude ghi mỗi mục là *nhận* hay *bỏ* kèm lý do (agy đề xuất, Claude quyết), sửa kịch bản, chạy lại `tttc.phong_cach` (phòng gợi ý của agy đưa vào cụm bị cấm).
**Vòng 2 (`--conversation <id>`):** gửi lại bản đã sửa cùng bảng triage; hỏi các vấn đề nặng đã xử lý chưa, có vấn đề mới không, chấm lại bốn điểm.

**Đạt khi:** không còn mục nặng nào đã *nhận* mà chưa sửa, và cả bốn điểm của vòng 2 ≥ 4 (đề xuất). **Đúng 2 vòng**, không có vòng thứ ba tự động. Chưa đạt thì hiện nguyên trạng ở trang duyệt 1 để bạn quyết.

**Dấu vết:** `phan-bien-giong-1.md` và `phan-bien-giong-2.md` giữ phản hồi nguyên văn của agy và bảng triage (cột: #, câu trích, loại, mức, nhận/bỏ, lý do). `trang-thai.json` thêm bước `phan-bien-giong` (có giờ, theo H1) kèm `conversation_id`. Trang duyệt 1 hiện khối tóm tắt: số mục nhận/bỏ, điểm hai vòng, mục còn tồn tại.

**Cổng trong code:** `render_review_1` từ chối nếu `phan-bien-giong` chưa `xong` hoặc `phong_cach` còn Lỗi.

**Khi agy lỗi** (khác `SUCCESS`, quá thời gian, mất lệnh): thử lại một lần. Vẫn lỗi thì dùng một subagent Claude độc lập với cùng prompt và **đánh dấu đỏ** ở trang duyệt 1 là "agy lỗi, đã thay bằng subagent". Không bỏ qua im lặng.

**Công cụ mỏng** (đề xuất `tttc.phan_bien`): dựng prompt từ tệp, gọi `agy` bằng `subprocess`, lưu JSON thô, trả `{status, response, conversation_id}`. Không phân tích nội dung phản biện.

**Dữ liệu rời máy:** phần lời đọc của kịch bản được gửi tới dịch vụ Antigravity trước khi đăng. Không gửi khóa, token hay dữ liệu cá nhân.

### 3.7 Nghe thử 60 giây
Trước duyệt 1, `giong_vieneu` đọc khoảng 200–220 từ đầu bằng giọng đã chọn (spec 2) ra `nghe-thu.mp3` đính kèm `duyet-1.html`. Bạn nghe để xác nhận đọc to tự nhiên. Giọng được lưu theo từng câu (tên theo nội dung và giọng), nên câu nào giữ nguyên thì dùng lại khi tạo giọng đầy đủ, không mất công.

### 3.8 Kiểm trong code (`tttc/phong_cach.py`)
- Thêm: danh sách cấm (Lỗi), nhịp (3.4), cụm kể trải nghiệm cá nhân (cảnh báo), lệnh chạy riêng thoát mã 1 khi có Lỗi.
- Bỏ yêu cầu "điều kiện đổi ý" khỏi `mui_may` (spec 1, H0 đã chuyển phán quyết thành tùy chọn).
- Các thông báo giữ tiền tố "Lỗi:" và "Cảnh báo:" như hiện nay; `duyet.py` tiếp tục hiện cả hai.
- Cập nhật `docs/phong-cach-kich-ban.md` mục 6 (Chống mùi máy) cho khớp, `video-moi/SKILL.md` bước 3–5, và test (`tests/test_phong_cach.py`).

## 4. Nghiệm thu

1. Hai kịch bản đã duyệt qua `python -m tttc.phong_cach`: 0 Lỗi và không cảnh báo mới (ngưỡng dưới mốc nền).
2. Một đoạn thử có đủ ba nhóm vi phạm (từ cấm, mở bài, kết bài) bị chặn với Lỗi đúng chỗ; đoạn nằm trong dấu ngoặc kép trích nguồn không bị chặn.
3. `tttc.phan_bien` có test với `agy` giả (chuỗi lệnh thay thế) cho ba trường hợp: `SUCCESS`, trạng thái khác `SUCCESS`, quá thời gian; không gọi dịch vụ thật trong test.
4. `render_review_1` từ chối khi thiếu `phan-bien-giong` hoặc còn Lỗi giọng văn; test đi kèm.
5. Trong ba ngày chạy khô (spec 1, mục 7): mỗi video có `phan-bien-giong-1.md` và `-2.md`, **không video nào phải sửa kịch bản sau khi đã có giọng vì giọng văn**, bạn nghe 60 giây và xác nhận tự nhiên, và sổ có giờ từng bước để biết cổng này tốn bao lâu.

## 5. Thứ tự làm

1. `tu-cam.json`, chuyển `DICH_THO`, lệnh chạy riêng, test mốc nền (rẻ, độc lập).
2. Mẫu giọng và `phan-tich-giong.md` (cần bạn chọn đoạn mẫu).
3. `tttc.phan_bien` và cổng trong `render_review_1`.
4. Cập nhật `video-moi/SKILL.md`, thẻ phong cách, khung giao việc.
5. Chạy thử trên một chủ đề thật; đo giờ; hiệu chỉnh ngưỡng trong chạy khô.

## 6. Rủi ro

1. **agy là phụ thuộc ngoài** (dịch vụ Google, phiên bản 1.5.3 hiện tại; có thể đổi hành vi, giới hạn hoặc giá). Có dự phòng subagent, nhưng đánh dấu đỏ.
2. **Phản biện chủ quan:** agy có thể sửa theo khẩu vị của nó. Giảm bằng triage có lý do, đúng 2 vòng, và lint tự động sau mỗi lần sửa.
3. **Giọng đọc máy:** từ đệm và câu lửng có thể đọc lạ với VieNeu; xử lý bằng nghe thử và chốt danh sách sau.
4. **Ngưỡng nhịp** có thể đánh trượt một kịch bản tốt khác; đó là lý do chỉ là cảnh báo.
5. **Bịa chi tiết cho "đời":** vai kể có thể kéo mô hình bịa. Giảm bằng ràng buộc 3.2, cảnh báo cụm trải nghiệm cá nhân, và agy có loại "bịa trải nghiệm".
6. **Thời gian:** ba lượt biên tập cộng hai vòng agy ước thêm 25–40 phút vào khối 07:00–10:30 của đồng hồ ngày (spec 1, mục 5). Đây là ước tính; bộ đếm giờ H1 đo thật.
7. **Dữ liệu rời máy** sang Antigravity (3.6).

## 7. Giả định cần bạn xác nhận khi đọc

- Mẫu giọng lấy hai đoạn từ kịch bản đã duyệt cộng đoạn bạn thêm; **không** dùng lời @MotCongNghe (mặc định).
- Danh sách cấm là Lỗi cứng ("cấm tiệt"), trừ chữ trong ngoặc kép trích nguồn.
- Ngưỡng điểm agy ≥ 4, tối đa 12 mục mỗi vòng, và các ngưỡng nhịp ở 3.4 là đề xuất của tôi.
- agy lỗi thì dùng subagent thay và đánh dấu đỏ (không chặn cả ngày).

## Phụ lục A. Khung giao việc cho `yt-script`

```
[BỐI CẢNH & VAI TRÒ]: Bạn là một người theo dõi công nghệ, sáng nay vừa đọc xong các tài liệu gốc
trong nguon.json, đang ngồi quán cà phê kể lại cho một đứa bạn thân chưa đọc.
[CHỦ ĐỀ]: {đề, lời hứa một câu, nguon.json}
[MẪU GIỌNG]: {phan-tich-giong.md + đoạn mẫu}
[QUY TẮC BẮT BUỘC]:
1. Giọng điệu: thẳng thắn, gãy gọn, chân thật, hơi tự giễu khi hợp, như trò chuyện 1-1.
2. Cấm mở bài sáo rỗng và kết bài đúc kết đạo lý; mở bằng sự kiện + cặp số + câu hỏi (theo thẻ phong cách).
3. Cấm tuyệt đối mọi mục trong tu-cam.json.
4. Nhịp: xen câu rất ngắn (3–5 từ) với câu vừa; cho phép câu lửng và câu hỏi tu từ ngắn;
   từ đệm chỉ trong danh sách cho phép.
5. Chi tiết cụ thể lấy từ nguồn (số, ngày, câu trích, tên) thay cho tính từ cảm thán;
   ví dụ đời thường phải nói rõ là ví dụ.
6. Không bịa trải nghiệm cá nhân hay giai thoại.
7. Mọi câu có số gắn [#id], không đổi giá trị so với nguon.json.
8. Đọc to thành tiếng phải nghe tự nhiên, không vấp.
```

## Phụ lục B. Prompt phản biện cho agy (cốt lõi)

```
Bạn là biên tập viên giọng văn tiếng Việt cho lời đọc video. Tình huống kể: một người theo dõi công nghệ
kể lại cho bạn thân nghe ngoài quán cà phê. Dưới đây là lời đọc (bản {1|2}), danh sách từ cấm, và phân tích
mẫu giọng. Hãy PHÊ BÌNH, không viết lại cả đoạn, không đổi con số, không dùng tool, không sửa file.
Nêu tối đa 12 vấn đề: câu trích nguyên văn | loại | mức (nặng/vừa/nhẹ) | gợi ý sửa ngắn.
Cuối cùng chấm 1–5: tự nhiên khi đọc to; đúng tình huống kể; nhịp; chi tiết cụ thể.
{vòng 2: thêm bảng triage vòng 1 và hỏi: vấn đề nặng nào chưa xử lý, có vấn đề mới không, điểm mới}
```
