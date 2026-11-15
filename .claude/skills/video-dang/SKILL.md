---
name: video-dang
description: Chặng 3 của pipeline video của kênh – upload video và Shorts đã qua 2 điểm duyệt lên YouTube ở chế độ riêng tư + hẹn giờ. Dùng khi người dùng gõ /video-dang, "đăng video", "lên lịch đăng".
---

# /video-dang [thư mục video]

Spec mục 5. Code: `pipeline/tttc/dang.py`. Chạy trong `pipeline/` bằng `uv run`.
Chạy trong phiên mới (`/clear` nếu phiên đang mang lịch sử chặng dựng): chặng này chỉ cần `trang-thai.json` và `dong-goi.json`.

## Lần đầu (một lần cho kênh)
Hướng dẫn người dùng tự làm (Claude không bấm hộ, không nhập mật khẩu):
1. console.cloud.google.com → tạo dự án → bật "YouTube Data API v3".
2. Màn hình đồng ý OAuth: loại External, thêm email kênh vào Test users.
3. Credentials → OAuth client ID → Desktop app → tải JSON.
4. Người dùng chạy: `cd pipeline && uv run python -m tttc.dang login ~/Downloads/client_secret_*.json`
   (mở trình duyệt, đăng nhập đúng tài khoản kênh). Token lưu trong Keychain, không có file nào trong dự án.
5. Xoá file client_secret JSON khỏi Downloads sau khi đăng nhập xong.

## Mỗi video
1. Chọn video: thư mục do người dùng nêu, hoặc thư mục duy nhất có `duyet-2=da-duyet` và `dang` chưa xong.
   Có nhiều thư mục như vậy (2 video/ngày) thì liệt kê kèm `gio_dang` của từng thư mục và hỏi người dùng, không tự chọn.
2. `tt.review_current(V, "duyet-2")` phải đúng. Khi hồ sơ cũ thiếu biên nhận hoặc tệp đã thay đổi, quay về bước duyệt tương ứng.
3. Ngày/giờ: ngày theo tên thư mục; giờ lấy `trang-thai.json:gio_dang` (lịch tự chạy `/video-moi` ghi sẵn một ô trong
   `config.json:khung_dang`, 11:30 hoặc 15:30), không có thì `config.json:gio_dang_mac_dinh` (15:30). Cả hai giờ đều trước
   khung 17:00–20:00 của đối thủ. Hai video cùng ngày không được trùng giờ.
4. **Xác nhận với người dùng trước khi upload** (một câu): tiêu đề đã chọn, ngày giờ đăng (giờ Việt Nam),
   số Shorts và giờ từng Short. Đợi "ok".
5. `uv run python -m tttc.dang ../videos/<slug> <dd/mm/yyyy> <HH:MM>` → in video id.
   Lệnh đo `final.mp4` và **từ chối** nếu video dài dưới 7:00 (`dang.DAI_TOI_THIEU`): báo người dùng, đề xuất cắt thành Shorts.
   Chỉ khi chính người dùng nói vẫn đăng dạng video dài và nêu lý do, mới chạy lại với `--cho-phep-ngan "<lý do của người dùng>"`
   (lý do ghi vào `trang-thai.json:cho_phep_ngan`). Không tự đặt lý do.
6. Shorts đăng **sau** video dài: buổi tối dựng Shorts (`video-dung` mục 7, thêm vào `dong-goi.json:shorts`), sáng hôm sau đăng từng Short: `uv run python -m tttc.dang short ../videos/<slug> <i>` (giờ lấy từ `dong-goi.json:shorts[i]`). Lệnh từ chối nếu Short chưa có biên nhận `duyet-short` hoặc tệp/tiêu đề/giờ đã đổi sau khi duyệt: quay lại cho người dùng xem, không tự chạy `duyet-short`.
7. Đăng bình luận mở đầu (để ghim) điều hướng người xem nếu cần bằng:
   `uv run python -m tttc.dang comment <video_id> "<nội dung bình luận>"`
   (Video dài: câu hỏi tranh luận cuối kịch bản; Shorts: link về video dài đầy đủ).
8. Báo link YouTube Studio: `https://studio.youtube.com/video/<id>/edit` cho mỗi video; nhắc người dùng mở kiểm:
   - Thumbnail, phụ đề, giờ hẹn, nhãn "nội dung thay đổi/tổng hợp".
   - **Với Video dài**: bật **Test & Compare (Thử nghiệm & So sánh)** nạp cả 3 mẫu `thumbnails/1.png`, `2.png`, `3.png` để đo CTR thực tế, và ghim bình luận mở đầu.
   - **Với mỗi Short**: bắt buộc gắn trường **Related Video (Video liên quan)** trỏ về video dài tương ứng, và ghim bình luận chứa link video dài.

## Lỗi thường gặp
- `quotaExceeded`: hạn mức API trong ngày đã hết; thử lại sau 0 giờ giờ Thái Bình Dương (14:00–15:00 giờ VN).
- `thumbnails.set` 403: kênh chưa xác minh số điện thoại → người dùng xác minh ở youtube.com/verify.
- Nếu `upload_dang_cho_id` có giá trị, đối chiếu Studio trước khi thử lại. Nếu Studio đã có video, ghi ID và giờ hẹn vào
  `video_id` / `lich_dang` (video dài) hoặc `short_ids` / `short_lich` (Short). Chỉ xóa cờ sau khi đối chiếu và lưu kết quả.
- `video_id` + `lich_dang` hoặc `short_ids` + `short_lich` ghi nhận upload và giờ hẹn. Chỉ ghi giờ công khai thật vào sổ sau khi đối chiếu Studio.
