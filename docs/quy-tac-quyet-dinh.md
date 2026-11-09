# Quy tắc quyết định (chép từ spec định vị đối đầu, mục 9)

Tra khi xem `theo-doi.csv`. Mọi ngưỡng ghi "đề xuất" chỉnh được sau hai tuần chạy thật.

`theo-doi.csv` thêm bốn cột: `trung_de_ho` (họ có video cùng sự kiện trong ±24 giờ không), `chenh_gio` (giờ đăng của mình trừ giờ đăng của họ, âm là sớm hơn), `radar_hang` (đề có trong top 3 radar sáng đó không), `view_ho_24h` (RSS trả view hiện tại nên radar chụp số đúng 24 giờ sau khi họ đăng để so cùng tuổi).

Hai thước: (1) so với trung vị của chính kênh mình; (2) so với họ trên các cặp cùng đề, trung vị tỉ số view 24 giờ của 10 cặp gần nhất.

**Mốc tính từ G (giả thuyết):**
- G+14: ≥ 12 video; ≥ 80% đăng trước 17:00; đã đo được tỉ lệ trùng đề.
- G+30: có một video vượt 10 N view hoặc CTR > 5%; ≥ 5 cặp cùng đề để so. Không đặt mục tiêu ngang họ.

**Luật dừng và đổi hướng (ngưỡng chỉnh sau hai tuần):**
- Video dưới 0,5× trung vị của mình ở 7 ngày: không làm loại đề đó trong 2 tuần. Trên 3×: làm thêm 2 đề cùng họ trong 10 ngày.
- Radar đoán trúng đề họ (top 3 so với đề họ đăng) dưới 30% sau 2 tuần: sửa luật chấm, không tăng số lượng.
- Trượt mốc 17:00 quá 3 ngày trong 7: hạ về 5 video/tuần, không bỏ máy kiểm.
- 20 video mà không video nào vượt 3× trung vị: đổi cách đua (quay lại "cùng sự kiện, khác tầng phân tích"), không đổi chất lượng trước.
- Có số liệu sai bị chỉ ra: ghim đính chính trong 24 giờ và ghi vào sổ. Hai lần trong 30 ngày thì bỏ chế độ "đề 1 chạy thẳng" và kiểm tay.
