# Danh sách áp nhận diện Nhịp Công Nghệ lên kênh YouTube (việc của bạn trong YouTube Studio)

Tôi không đổi được cài đặt tài khoản YouTube; các bước dưới đây do bạn làm. Tệp đã sẵn ở `brand/`.

| # | Việc | Tệp / giá trị | Ghi chú |
|---|---|---|---|
| 1 ✅ | Đổi tên kênh | **Nhịp Công Nghệ** | Trang trợ giúp chính thức của YouTube nói đổi tên **hai lần trong 14 ngày** và đổi tên làm mất huy hiệu xác minh nếu có ([support.google.com/youtube/answer/2657964](https://support.google.com/youtube/answer/2657964)) |
| 2 ✅ | Đổi handle | **@nhipcongnghe** | Hạn mức đổi handle chỉ lấy từ trang thứ cấp (hai lần mỗi 14 ngày, chưa xác nhận trên trang chính thức): kiểm trong Studio trước khi bấm; handle có thể đã bị người khác lấy từ 10/11 |
| 3 | Ảnh hồ sơ | `brand/avatar-800.png` (800×800, tự cắt tròn) | Studio ghi: ít nhất 98×98 px, tối đa 4 MB, PNG hoặc GIF không động; (nguồn thứ cấp nói tối đa 6 MB: theo Studio) |
| 4 | Ảnh bìa (banner) | `brand/banner-2560x1440.png` (2560×1440; vùng an toàn 1546×423 ở giữa) | ≤ 6 MB; kiểm xem trên điện thoại, máy tính và TV |
| 5 ✅ | Mô tả kênh | "Tin nóng công nghệ – kinh tế, góc nhìn Việt Nam. Mọi con số đều dẫn nguồn gốc." | Câu định vị đã dùng trên banner |
| 6 | Thumbnail video nvidia đã đăng | tạo bằng `tttc.thumb.khung` | Ghi chú: video đã đăng dùng nhận diện cũ |

Kích thước banner và avatar lấy từ các trang hướng dẫn kích thước (veed.io, async.com, havecamerawilltravel.com), chưa đối chiếu trang trợ giúp chính thức.
Trong repo: tên dịch vụ Keychain `tui-tien-cong-nghe` giữ nguyên (đổi sẽ làm mất token OAuth đã cấp).

**Đã làm ngày 10/11/2026 (qua trình duyệt tích hợp, đăng nhập đúng tài khoản):** tên, handle, mô tả. **Còn lại cho bạn:** avatar (#3), banner (#4), thumbnail video đã đăng (#6): khung trình duyệt tích hợp không mở được hộp chọn tệp và Chrome của bạn đang đăng nhập tài khoản khác. Studio ghi ảnh bìa tối thiểu 2048×1152 px.
