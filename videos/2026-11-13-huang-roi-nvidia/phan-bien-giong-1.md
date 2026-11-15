# Phản biện giọng — vòng 1

**⚠ agy lỗi/không chạy được, dùng phản biện nội bộ.** Không có repo `pipeline-ytb` trên máy (không clone theo chỉ đạo) nên không chạy được `tttc.phan_bien` (Antigravity), cũng không lấy được prompt `tttc.phan_bien.dung_prompt`. Không có subagent độc lập. Hai vòng dưới đây do chính executor viết kịch bản tự soi → **không độc lập**, trang duyệt 1 phải đánh dấu đỏ. Đề xuất: khi có repo, chạy lại đúng 2 vòng agy trước khi duyệt.

Phạm vi: chỉ giọng văn tự nhiên (số liệu/nguồn để bước kiem).

## Điểm vòng 1 (thang 1–5)
Tự nhiên khi đọc to 3 · Không mùi máy 4 · Nhịp câu 3 · Nói với "bạn"/đời thường 4

## Bảng triage
| # | câu trích | loại | mức | nhận/bỏ | lý do |
|---|---|---|---|---|---|
| 1 | "Và rạng sáng mười tám tháng mười một, tính ra theo giờ Việt Nam là lúc Nvidia báo cáo, nên nghe câu gì?" | câu vấp | nặng | nhận | Đảo lại: "Và khi Nvidia báo cáo, tính ra là rạng sáng 18/11 giờ VN, nên nghe câu gì?" |
| 2 | "không một tính từ" (8-K) | nói quá | vừa | nhận | 8-K vẫn có vài tính từ → "gần như không có tính từ" |
| 3 | "lệch nhau đúng một ngày" / "chỉ một ngày từ lúc..." | số tự suy không nhãn | vừa | nhận | Đổi thành "hai ngày liền nhau", "từ hôm... tới hôm sau" để khỏi cần nhãn tự tính |
| 4 | "Báo chí trong nước từng gọi..." | khái quát quá nguồn | vừa | nhận | Nguồn chỉ có Báo Chính phủ → nói đúng tên |
| 5 | "chưa từng có người chính thức ngồi ghế trưởng đoàn" | ẩn dụ lệch | nhẹ | nhận | Ẩn dụ xe/tài xế lẫn với "trưởng đoàn" → nói thẳng "chưa từng có ai mang chức chủ tịch hội đồng" |
| 6 | "Vậy ai cầm lái? Bà Kress cầm vô lăng. Ông Jones..." | hai câu cụt một đoạn | nhẹ | nhận | Gộp câu |
| 7 | "Câu đó có thể đúng. Nhưng phải ăn bát đầu tiên mới biết." | câu cụt đôi | nhẹ | nhận | Gộp bằng dấu phẩy |
| 8 | Câu "người dùng phổ thông... chiếc điện thoại" ở Beat 4 lặp ở Beat 6 | nhai lại | vừa | nhận | Bỏ ở Beat 4, giữ ở kết |
| 9 | "chính người viết bản bình luận" / "Bản viết vẫn mang chữ ký giám đốc tài chính" | nói quá | vừa | nhận | Nguồn chỉ nói "commentary from Colette Kress" → "người đứng tên", "được hẹn từ trước với tư cách giám đốc tài chính" |
| 10 | "phần lớn con số doanh thu thuộc về giai đoạn trước..." | câu mơ hồ | vừa | nhận | Cả quý khép sổ 25/10 → "đã chốt trước khi có chuỗi tin của tuần này" |
| 11 | "thức dậy lúc bốn giờ sáng" | số không thẻ | vừa | nhận | → "từ tờ mờ sáng" |
| 12 | "lộ trình sản phẩm mà ông Jones vừa hứa giữ nguyên" | lệch chữ nguồn | vừa | nhận | Thống nhất với ý "kỳ vọng" → "vừa nói sẽ không gián đoạn" |
| 13 | Hai câu đùa ở Beat 2 (tổ dân phố, thông báo cắt nước) | châm biếm dày | nhẹ | bỏ | Đúng hạn mức 1–2 câu/beat; đều nhắm vào văn bản, không vào người |
| 14 | "chẳng ai dám ghi 'lương thỏa thuận'" | châm biếm | nhẹ | bỏ | Nhắm vào tình huống tuyển dụng, không mang số, không nhắm cá nhân |

Kết quả: 14 mục (nhận 12, bỏ 2). Đã sửa `kich-ban.md`, kiểm tạm lại: 0 lỗi từ cấm.
