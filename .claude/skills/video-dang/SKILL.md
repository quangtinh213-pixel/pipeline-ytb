---
name: video-dang
description: Chặng 3 của pipeline video kênh Túi Tiền Công Nghệ – upload video và Shorts đã qua 2 điểm duyệt lên YouTube ở chế độ riêng tư + hẹn giờ. Dùng khi người dùng gõ /video-dang, "đăng video", "lên lịch đăng".
---

# /video-dang [thư mục video]

Spec mục 5. Code: `pipeline/tttc/dang.py`. Chạy trong `pipeline/` bằng `uv run`.

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
2. `tt.is_approved` phải đúng; không thì dừng và nói bước nào chưa duyệt. Không có ngoại lệ.
3. Ngày/giờ: lấy từ `lich-4-tuan-dinh-vi-A.md` theo ngày trong tên thư mục; không có thì `config.json:gio_dang_mac_dinh`.
4. **Xác nhận với người dùng trước khi upload** (một câu): tiêu đề đã chọn, ngày giờ đăng (giờ Việt Nam),
   số Shorts và giờ từng Short. Đợi "ok".
5. `uv run python -m tttc.dang ../videos/<slug> <dd/mm/yyyy> <HH:MM>` → in video id.
6. Từng Short: `uv run python -m tttc.dang short ../videos/<slug> <i>` (giờ lấy từ `dong-goi.json:shorts[i]`).
7. Báo link YouTube Studio: `https://studio.youtube.com/video/<id>/edit` cho mỗi video; nhắc người dùng mở
   kiểm thumbnail, phụ đề, giờ hẹn, nhãn "nội dung thay đổi/tổng hợp".

## Lỗi thường gặp
- `quotaExceeded`: hạn mức API trong ngày đã hết; thử lại sau 0 giờ giờ Thái Bình Dương (14:00–15:00 giờ VN).
- `thumbnails.set` 403: kênh chưa xác minh số điện thoại → người dùng xác minh ở youtube.com/verify.
- Upload hỏng giữa chừng: video có thể đã tạo dạng riêng tư; kiểm Studio trước khi chạy lại để tránh trùng.
