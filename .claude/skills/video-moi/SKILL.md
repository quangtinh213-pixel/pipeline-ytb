---
name: video-moi
description: Chặng 1 của pipeline video kênh Túi Tiền Công Nghệ – chọn đề, đọc nguồn gốc, viết kịch bản gắn nguồn, tự kiểm, rồi dừng ở điểm duyệt 1. Dùng khi người dùng gõ /video-moi [chủ đề], "làm video mới", hoặc nói "duyệt" cho một kịch bản đang chờ duyệt 1.
---

# /video-moi [chủ đề tùy chọn]

Spec: `docs/superpowers/specs/2026-11-08-pipeline-video-tu-dong-design.md` mục 3.
Mọi lệnh Python chạy trong `pipeline/`: `cd pipeline && uv run python -m ...`.
Sổ trạng thái: `tttc.trang_thai` (`load`, `set_step`, `set_field`, `next_step`).

## 0. Mở hoặc tiếp tục

- Nếu người dùng nói "duyệt" cho video đang `duyet-1=cho-duyet`: chạy lại `tttc.kiem` một lần; sạch thì
  `set_step(dir, "duyet-1", "da-duyet")` và báo "Chạy /video-dung để dựng". Còn lỗi thì báo lỗi, không duyệt.
- Nếu người dùng ghi chỗ cần sửa: sửa `kich-ban.md`/`nguon.json`, quay lại bước 4.
- Video mới: tạo `videos/<yyyy-mm-dd-slug>/` (ngày = ngày đăng dự kiến theo `lich-4-tuan-dinh-vi-A.md`
  nếu có, không thì hôm nay; slug ascii không dấu, ≤ 5 từ).
- Video đã có: đọc `next_step`, bỏ qua bước đã `xong`.

Mỗi bước: xong thì `set_step(..., "xong")`; hỏng thì `set_step(..., "loi", "<lý do>")` và dừng, báo người dùng.

## 1. chu-de

- Có chủ đề từ người dùng: vẫn chấm theo 3 câu bên dưới, ghi 1 đề.
- Không có: đọc `pipeline/config.json:nguon_tin`, quét tin 24 giờ qua. Chấm mỗi đề 3 câu, mỗi câu 0–2 điểm:
  1. Đang nóng? 2. Có số lớn? 3. Hệ quả cho túi tiền người Việt? (**0 điểm câu 3 → loại**).
- Chấm câu 1 bằng dữ liệu, không cảm tính: gọi skill `yt-viral` cho ngách (công nghệ / giá cả / túi tiền, tiếng Việt)
  để xem đề tương tự đang vượt kênh của nó bao nhiêu lần; ghi link video mẫu cạnh điểm.
- Ghi `chu-de.md`: 3 đề tốt nhất, mỗi đề gồm tiêu đề tạm, lời hứa một câu, điểm từng câu, link tin.
  Đề 1 là đề được làm tiếp; người dùng đổi ở điểm duyệt.

## 2. nguon

- Đọc **tài liệu gốc** (báo cáo, văn bản chính phủ, trang giá chính thức, hồ sơ công ty), không dừng ở tin thứ cấp.
- Mỗi con số dùng trong video thành một mục trong `nguon.json`:
  `{"id","gia_tri","trich_dan","url","ngay_truy_cap","anh_chup","trang_thai"}`
  - `id` ngắn: `p1`, `g2`...; `gia_tri` ghi đúng như trong nguồn kèm đơn vị.
  - `trich_dan` là câu gốc chứa số, **chép nguyên văn** (≤ 25 từ) – mẫu `trich-bao` chỉ được trích đúng chữ này.
  - `ten`: tên báo/cơ quan để hiện trên màn hình (vd "VnExpress", "Bộ Tài chính"); bỏ trống thì dùng tên miền.
  - `anh_chup`: chụp trang bằng trình duyệt có sẵn, lưu `nguon/<id>.png`.
  - `trang_thai`: `xac-minh` (đọc thấy trong nguồn gốc) | `so-bo` (nguồn tự ghi là sơ bộ/ước tính) |
    `chua-xac-minh` (chỉ thấy ở tin thứ cấp) | `tu-tinh` (số do mình suy ra từ số khác: hiệu năm, tỉ lệ, "gấp N lần").
  - `tu-tinh` bắt buộc thêm `cong_thuc` (vd `"2026 − 2011"`) và `dau_vao` (danh sách id nguồn gốc dùng trong phép tính);
    `gia_tri` là kết quả. Không ghi `xac-minh` cho số tự tính. Câu dùng số này phải nói rõ "mình tự tính" (hoặc
    "tự ướm", "không phải dự báo của ai").
- Trang chặn truy cập tự động (Bloomberg, báo trả phí...): **không** thay bằng tin thứ cấp. Ghi `chua-xac-minh`
  và nêu trong `chu-de.md`.
- Không bao giờ bịa số. Không tìm được thì không dùng số đó.

## 3. kich-ban

- Gọi skill `yt-script` với đề, lời hứa, `nguon.json` và **thẻ phong cách `docs/phong-cach-kich-ban.md`**. Khung 6 đoạn của kênh:
  móc 15 giây → bối cảnh/số → chuyện thật sự đổi gì → hệ quả cho người Việt → hai việc cần ngóng → kết trả lời câu hỏi tiêu đề.
- Định dạng `kich-ban.md`:
  - Mỗi beat: `#### Beat N: <tên>`, dòng `[TRÊN MÀN HÌNH]: ...`, rồi `**Lời đọc:**` và các đoạn lời đọc ngay dưới.
  - Câu nào có số (cả trên màn hình lẫn lời đọc) gắn `[#id]` ngay sau dấu chấm câu.
  - Trong **lời đọc**, số viết thành chữ để TTS đọc đúng ("năm trăm hai mươi hai nghìn năm trăm đồng"); trên màn hình giữ chữ số.
  - Số từ nguồn `so-bo` phải có chữ "sơ bộ" hoặc "chưa chính thức" trong câu.
  - 10–13 phút ≈ 2.000–2.600 từ lời đọc (~200 từ/phút; từ = âm tiết; `tttc.phong_cach` kiểm).

- **Khung giao việc cho `yt-script`** (điền `{...}`; spec giọng văn `docs/superpowers/specs/2026-11-09-giong-van-kich-ban-design.md`, Phụ lục A):

```
[BỐI CẢNH & VAI TRÒ]: Bạn là một người theo dõi công nghệ, sáng nay vừa đọc xong các tài liệu gốc
trong nguon.json, đang ngồi quán cà phê kể lại cho một đứa bạn thân chưa đọc.
[CHỦ ĐỀ]: {đề, lời hứa một câu, nguon.json}
[MẪU GIỌNG]: {pipeline/phong-cach/phan-tich-giong.md + các đoạn trong pipeline/phong-cach/mau-giong/}
[QUY TẮC BẮT BUỘC]:
1. Giọng điệu: thẳng thắn, gãy gọn, chân thật, hơi tự giễu khi hợp, như trò chuyện 1-1.
2. Cấm mở bài sáo rỗng và kết bài đúc kết đạo lý; mở bằng sự kiện + cặp số + câu hỏi (theo thẻ phong cách).
3. Cấm tuyệt đối mọi mục trong pipeline/phong-cach/tu-cam.json.
4. Nhịp: xen câu rất ngắn (3–5 từ) với câu vừa; cho phép câu lửng và câu hỏi tu từ ngắn;
   từ đệm chỉ trong danh sách cho phép.
5. Chi tiết cụ thể lấy từ nguồn (số, ngày, câu trích, tên) thay cho tính từ cảm thán;
   ví dụ đời thường phải nói rõ là ví dụ.
6. Không bịa trải nghiệm cá nhân hay giai thoại.
7. Mọi câu có số gắn [#id], không đổi giá trị so với nguon.json.
8. Đọc to thành tiếng phải nghe tự nhiên, không vấp.
```
- **Biên tập hai lượt** trên bản nháp (đừng viết lại từ đầu): lượt 1 "Đọc lại, gạch bỏ mọi câu sáo rỗng không thêm thông tin."; lượt 2 "Viết lại sao cho đọc to thành tiếng không vấp, nghe như nói trực tiếp, không như đọc văn bản." Hai lượt không được đổi con số, thẻ `[#id]`, câu "sơ bộ" hoặc "mình tự tính".
- `cd pipeline && uv run python -m tttc.phong_cach ../videos/<slug>` tới `0 Lỗi` (Lỗi là từ cấm, mở/kết bài sáo rỗng, dịch thô; chặn duyệt 1). Đọc từng cảnh báo nhịp và sửa hoặc ghi lý do giữ. Rồi `set_step(dir, "kich-ban", "xong")`.

## 4. phan-bien-giong (agy, đúng 2 vòng)

Chỉ phản biện giọng văn tự nhiên; số liệu và nguồn do bước `kiem` lo. Lời đọc được gửi tới dịch vụ Antigravity trước khi đăng (không gửi khóa, token, dữ liệu cá nhân). Không dùng `--dangerously-skip-permissions`.

1. **Vòng 1:** `cd pipeline && uv run python -m tttc.phan_bien vong 1 ../videos/<slug>`. In `conversation_id` và phản hồi; ghi `phan-bien-giong-1.md` (+ `.raw.json`).
2. **Triage** (agy đề xuất, bạn quyết): điền mục `## Bảng triage` của `phan-bien-giong-1.md` thành bảng cột `#, câu trích, loại, mức, nhận/bỏ, lý do`. Mục nào nhận thì sửa `kich-ban.md` (không đổi số, `[#id]`, câu cảnh báo), rồi chạy lại `tttc.phong_cach` (phòng gợi ý đưa vào cụm bị cấm).
3. **Vòng 2:** `uv run python -m tttc.phan_bien vong 2 ../videos/<slug> --conversation <id> --triage ../videos/<slug>/phan-bien-giong-1.md`; triage và sửa tiếp, điền `phan-bien-giong-2.md`.
4. **Đạt khi** không còn mục nặng đã nhận mà chưa sửa và bốn điểm vòng 2 đều ≥ 4. Đúng 2 vòng, không có vòng 3 tự động; chưa đạt thì ghi rõ trong note để bạn quyết ở duyệt 1.
5. `set_step(dir, "phan-bien-giong", "xong", "vòng 1: N mục (nhận a, bỏ b), điểm x/x/x/x; vòng 2: M mục (nhận c, bỏ d), điểm y/y/y/y")`.
6. **agy lỗi** (khác SUCCESS, quá thời gian, mất lệnh): thử lại một lần. Vẫn lỗi thì chạy một subagent Claude độc lập với đúng prompt của `tttc.phan_bien.dung_prompt`, và ghi note `agy lỗi, dùng subagent` (trang duyệt 1 sẽ đánh dấu đỏ). Không bỏ qua im lặng.

## 5. kiem

1. (chạy sau mọi chỗ sửa giọng văn) `uv run python -m tttc.kiem ../videos/<slug>`; sửa tới khi `0 lỗi`.
2. Dispatch một subagent độc lập (không chia sẻ ngữ cảnh) với `kich-ban.md` + `nguon.json` + ảnh chụp: nhiệm vụ là
   tìm câu nói quá nguồn (nguồn nói X, kịch bản nói hơn X), số lấy sai mục, thiếu cảnh báo sơ bộ. Sửa những gì nó tìm ra.
3. `set_step(dir, "kiem", "xong")`.

## 6. nghe thử và duyet-1

- Tạo bản nghe thử: `uv run python -m tttc.giong_vieneu thu-60s ../videos/<slug>` (nghe-thu.mp3, đính kèm trang duyệt).
- `uv run python -c "from tttc.duyet import render_review_1; print(render_review_1('../videos/<slug>'))"`
- `set_step(dir, "duyet-1", "cho-duyet")`
- Gửi `duyet-1.html` cho người dùng (SendUserFile, display render). Tóm tắt 3 dòng: đề, số nguồn, cảnh báo còn lại.
- **Dừng.** Không tự duyệt thay người dùng.
