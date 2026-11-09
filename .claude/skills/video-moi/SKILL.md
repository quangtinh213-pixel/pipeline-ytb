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
    `chua-xac-minh` (chỉ thấy ở tin thứ cấp).
- Trang chặn truy cập tự động (Bloomberg, báo trả phí...): **không** thay bằng tin thứ cấp. Ghi `chua-xac-minh`
  và nêu trong `chu-de.md`.
- Không bao giờ bịa số. Không tìm được thì không dùng số đó.

## 3. kich-ban

- Gọi skill `yt-script` với đề, lời hứa và `nguon.json`. Khung 6 đoạn của kênh:
  móc 15 giây → bối cảnh/số → chuyện thật sự đổi gì → hệ quả cho người Việt → hai việc cần ngóng → kết trả lời câu hỏi tiêu đề.
- Định dạng `kich-ban.md`:
  - Mỗi beat: `#### Beat N: <tên>`, dòng `[TRÊN MÀN HÌNH]: ...`, rồi `**Lời đọc:**` và các đoạn lời đọc ngay dưới.
  - Câu nào có số (cả trên màn hình lẫn lời đọc) gắn `[#id]` ngay sau dấu chấm câu.
  - Trong **lời đọc**, số viết thành chữ để TTS đọc đúng ("năm trăm hai mươi hai nghìn năm trăm đồng"); trên màn hình giữ chữ số.
  - Số từ nguồn `so-bo` phải có chữ "sơ bộ" hoặc "chưa chính thức" trong câu.
  - 10–13 phút ≈ 1.500–1.900 từ lời đọc.

## 4. kiem

1. `uv run python -m tttc.kiem ../videos/<slug>`; sửa tới khi `0 lỗi`.
2. Dispatch một subagent độc lập (không chia sẻ ngữ cảnh) với `kich-ban.md` + `nguon.json` + ảnh chụp: nhiệm vụ là
   tìm câu nói quá nguồn (nguồn nói X, kịch bản nói hơn X), số lấy sai mục, thiếu cảnh báo sơ bộ. Sửa những gì nó tìm ra.
3. `set_step(dir, "kiem", "xong")`.

## 5. duyet-1

- `uv run python -c "from tttc.duyet import render_review_1; print(render_review_1('../videos/<slug>'))"`
- `set_step(dir, "duyet-1", "cho-duyet")`
- Gửi `duyet-1.html` cho người dùng (SendUserFile, display render). Tóm tắt 3 dòng: đề, số nguồn, cảnh báo còn lại.
- **Dừng.** Không tự duyệt thay người dùng.
