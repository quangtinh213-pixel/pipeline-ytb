## Đề 1: Sinh viên Việt dùng AI phát hiện lỗ hổng 7-Zip CVE-2026-125742: máy bạn đang dùng bản nào?
- Điểm: 6 (sốc 1, số lớn 1, góc Việt Nam 2×2)
- Tin gốc: https://vnexpress.net/sinh-vien-viet-dung-ai-phat-hien-lo-hong-7-zip-5144449.html
- Họ đã đăng cùng sự kiện: không

## Đề 2: Dell Việt Nam từ chối bảo hành laptop xách tay: rẻ hơn chính hãng nhưng hỏng ai sửa?
- Điểm: 5 (sốc 1, số lớn 0, góc Việt Nam 2×2)
- Tin gốc: https://vnexpress.net/dell-viet-nam-canh-bao-tu-choi-bao-hanh-voi-laptop-hang-nhap-khau-5143539.html
- Họ đã đăng cùng sự kiện: không

## Đề 3: Sàn TMĐT thu thuế kỷ lục 241.000 tỷ: Shopee và TikTok Shop siết thuế, người mua gánh giá đắt?
- Điểm: 5 (sốc 1, số lớn 2, góc Việt Nam 1×2)
- Tin gốc: https://cafef.vn/
- Họ đã đăng cùng sự kiện: không

---

# Ghi chú chọn đề (14/11/2026, đăng dự kiến 15/11)

Không có chủ đề từ người dùng ("video moi"): quét tin công nghệ trong nước và quốc tế 24 giờ qua từ VnExpress, CafeF, TechCrunch.
Video ngày 14/11/2026 ("Sự thật vụ Microsoft nâng cấp mạng") vừa hoàn tất và lên lịch 15:30 hôm nay. Video tiếp theo thuộc lịch đăng 15/11/2026.

## Đề 1 (làm tiếp): Sinh viên Việt dùng AI phát hiện lỗ hổng 7-Zip

**Loại:** `bao-mat` (khung HOOK, MÔ TẢ VẤN ĐỀ, CÁCH XỬ LÝ NGAY, CHÂM BIẾM, KẾT; 400–700 từ lời đọc).
**Tiêu đề tạm:** CẢNH BÁO: Sinh viên Việt dùng AI phát hiện lỗ hổng 7-Zip, người dùng có nguy cơ gì?
**Lời hứa:** Nguyễn Trần Thanh Lâm (sinh viên NTU Singapore) đã dùng mô hình AI Claude Opus 5 phát hiện lỗ hổng nghiêm trọng CVE-2026-125742 trên 7-Zip như thế nào, nó đe dọa hàng triệu máy tính ra sao, và hai bước kiểm tra cập nhật ngay trên máy bạn.

| Câu | Điểm | Dữ liệu |
|---|---|---|
| 1. Cú sốc 48 giờ? | 1/2 | Tin công bố ngày 13/11/2026 trên VnExpress. 7-Zip là phần mềm giải nén quốc dân gần như mọi máy tính Windows đều cài đặt, nay dính lỗi thực thi mã độc từ xa. |
| 2. Số lớn từ nguồn gốc? | 1/2 | Điểm CVSS v4.0 là 8,5/10; CVSS v3.1 là 7,8/10; bản vá phát hành từ 7-Zip 26.06; lỗ hổng ghi ngoài vùng nhớ CWE-787; tạo 2 tệp CAB đặc biệt mở reverse shell. |
| 3. Góc Việt Nam (×2) | 2/2 | Người tìm ra là sinh viên Việt Nam (Nguyễn Trần Thanh Lâm, du học sinh NTU Singapore); hàng triệu người dùng máy tính Việt Nam đang sử dụng 7-Zip hàng ngày. |

- Họ đã đăng cùng sự kiện: không (@MotCongNghe chưa đăng về đề tài này).
- Rủi ro kỹ thuật: Cần giải thích đời thường khái niệm "heap out-of-bounds write" và "reverse shell" để khán giả đại chúng dễ hiểu, không lạm dụng thuật ngữ trừu tượng.
