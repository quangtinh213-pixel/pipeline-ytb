# Quy tắc quyết định

Đọc khi xem `theo-doi.csv`. Viết lại ngày 15/11/2026: bỏ luật "0,5× / 3× trung vị của kênh", vì trung vị chỉ khoảng 100 view nên tỉ lệ so với nó không mang thông tin. Thay bằng ngưỡng tuyệt đối đo được bằng máy. Các ngưỡng sẽ xem lại ngày 29/11, cùng báo cáo tuần.

## 1. Luật đọc sổ (máy in mỗi tối)

`dong-bo-view.py` chạy lúc 21:30 và in các dòng `Luật:` vào `pipeline/dong-bo-view.log`. Muốn xem lại bất kỳ lúc nào thì chạy `uv run python -m tttc.giam_sat luat`. Luật chỉ áp cho video dài đăng trong 30 ngày gần nhất. Shorts chưa có số đo riêng nên chưa áp. Ô trống thì không kết luận.

| Cột sổ | Ngưỡng | Việc cần làm | Ai làm |
|---|---|---|---|
| `ctr` (gộp 7 ngày đầu, Reporting API) | < 3% | Đổi thumbnail bằng Test & Compare trong Studio | Bạn |
| `giu_chan_30s` (7 ngày đầu) | < 70% | Xem lại hook trước video kế tiếp (luật 40 giây đầu, `phong_cach.kiem_mo_dau`) | Claude đề xuất, bạn duyệt |
| `avd_pct` (averageViewPercentage, 7 ngày đầu) | < 30% | Xem lại độ dài và cấu trúc: cắt đoạn giữa, hoặc tách thành Shorts | Claude đề xuất, bạn duyệt |
| `view_7d` | ≥ 1.000 | Làm thêm 2 tập cùng chuỗi trong 10 ngày | Claude đề xuất đề ở radar |

Thời điểm có số:
- `giu_chan_30s`, `avd_pct`, `con_50pct`: khi video đủ 9 ngày (7 ngày đo, cộng khoảng 2 ngày Analytics trễ).
- `ctr`: khi đủ 7 báo cáo ngày (ngày PST).
- `view_7d`: trong cửa sổ 7–8 ngày. Lỡ cửa sổ thì ô để trống.

**CTR trong vài giờ đầu** chỉ có trên Studio. Nếu bạn đọc thấy CTR < 4% sau 3 giờ, chạy `python -m tttc.giam_sat ../videos/<slug> --ctr <số>`. Thêm `--auto-pivot` thì máy xoay sang phương án dự phòng trong `dong-goi.json`. Máy không tự đo được mốc này.

## 2. Luật theo lứa (đọc trong báo cáo tuần)

Hai luật đầu là đề xuất mới ngày 15/11, chưa được bạn xác nhận.

- Ba video dài liên tiếp có `giu_chan_30s` < 70%: dừng làm đề mới một ngày, viết lại khuôn mở đầu trong `docs/phong-cach-kich-ban.md` rồi mới làm tiếp.
- Ba video liên tiếp có CTR < 3% cùng khuôn thumbnail: xem lại khuôn (mục 5 của đề xuất 15/11) trước khi xem lại đề.
- 10 video dài theo chuẩn mới mà không video nào ≥ 1.000 view 7 ngày (ngoài video đầu): xem lại cách chọn đề (radar, định dạng, chuỗi) trước khi đụng tới khâu dựng.
- Video dưới 7:00 không đăng dạng video dài. Cổng ở `dang.kiem_thoi_luong` chặn việc này; chỉ đăng khi bạn ghi lý do bằng `--cho-phep-ngan`.

## 3. So với đối thủ

Bốn cột của sổ:
- `trung_de_ho`: họ có video cùng sự kiện trong ±24 giờ không.
- `chenh_gio`: giờ mình đăng trừ giờ họ đăng; âm là mình sớm hơn.
- `radar_hang`: đề có nằm trong top 3 radar sáng đó không.
- `view_ho_24h`: view của video họ đúng 24 giờ sau khi họ đăng.

Thước so là trung vị tỉ số view 24 giờ của mình trên của họ, tính trên 10 cặp cùng đề gần nhất (`theo_doi.ty_so_trung_vi`). Chỉ dùng để theo dõi xu hướng. Không đặt mục tiêu ngang họ.

- Radar đoán trúng đề họ (top 3 so với đề họ đăng) dưới 30% sau 2 tuần: sửa luật chấm, không tăng số lượng.
- Trượt mốc 17:00 quá 3 ngày trong 7: hạ xuống 5 video/tuần, không bỏ máy kiểm.

## 4. Sai số liệu

Có số liệu sai bị chỉ ra:
- Ghim đính chính trong 24 giờ và ghi vào sổ. Việc ghim do bạn làm trên Studio.
- Hai lần trong 30 ngày: bỏ chế độ "đề 1 chạy thẳng" và kiểm tay.

## 5. Tiêu chí xem lại ngày 29/11

Áp cho 10 video dài cùng chuẩn mới:
- CTR 7 ngày trung vị ≥ 4%.
- Còn xem ở giây 30 trung vị ≥ 75%.
- `con_50pct` trung vị ≥ 35%.
- Ít nhất một video ≥ 1.000 view 7 ngày, ngoài video đầu.

Kết luận:
- Đạt ≥ 3/4: giữ hướng.
- Đạt ≤ 1/4: xem lại cách chọn đề trước.
