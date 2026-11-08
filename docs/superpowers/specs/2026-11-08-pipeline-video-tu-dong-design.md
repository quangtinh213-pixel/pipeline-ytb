# Pipeline video tự động – Túi Tiền Công Nghệ

Ngày: 08/11/2026 · Trạng thái: chờ duyệt spec

## 1. Mục tiêu

Biến một chủ đề (hoặc tin nóng trong ngày) thành video YouTube 10–13 phút + 2–3 Shorts đã hẹn giờ đăng, với người chỉ can thiệp ở **2 điểm duyệt**:

1. Duyệt chủ đề + kịch bản đã gắn nguồn.
2. Duyệt video cuối + chọn tiêu đề/thumbnail.

Thành công khi: một video đi hết pipeline mà bạn bỏ ra ≤ 45 phút, mọi con số trong video đều có nguồn bấm được, và lịch 4 video dài + 3 Shorts/tuần làm được trong 30 giờ/tuần.

### Ràng buộc (bạn đã nêu)
- Không lộ mặt, giọng tổng hợp (ElevenLabs).
- Mọi con số lấy từ nguồn gốc, không bịa. Số sơ bộ phải có cảnh báo.
- Phong cách hình giống kênh mẫu @MotCongNghe (minh họa vector isometric, nhãn chữ đậm, biểu đồ động, phụ đề, ảnh nhân vật có ghi công), nhưng dùng brand riêng: nền #111111, vàng #FFC800, trắng, font SF Pro Heavy.
- Chạy trên Mac của bạn qua Claude Code (hướng A). Tự chạy theo lịch (hướng B) làm ở đợt sau.

### Giả định (chưa được bạn xác nhận)
- Phong cách kênh mẫu chỉ rút ra từ 5 khung hình của 1 video (bầu cử giữa kỳ, 08/11/2026).
- Giá ElevenLabs và hạn mức YouTube API phải kiểm lại khi đăng ký.

## 2. Kiến trúc

```
Youtube/
  pipeline/
    skills/        video-moi, video-dung, video-dang (skill Claude Code)
    scripts/       tts.py, render.sh, upload.py, kiem.py
    templates/     6 mẫu cảnh HyperFrames + mẫu thumbnail
    svg/           thư viện hình isometric (lớn dần theo thời gian)
    config.json    giọng ElevenLabs, tốc độ, nhạc nền, nguồn tin, giờ đăng
  videos/<yyyy-mm-dd-slug>/
    trang-thai.json
    chu-de.md, nguon.json, kich-ban.md
    giong.mp3, giong-timing.json
    canh.json, composition/, final.mp4, shorts/*.mp4, phu-de.srt
    dong-goi.md, thumbnails/
  brand/           (đã có)
```

`trang-thai.json` lưu từng bước: `chua-chay | xong | loi(lý do) | cho-duyet | da-duyet`. Mỗi lệnh đọc file này, bỏ qua bước đã xong và chạy lại bước lỗi.

Phần sáng tạo và kiểm tra (chọn đề, đọc nguồn, viết, chia cảnh, vẽ SVG, soi hình) do Claude làm trong skill. Script chỉ dùng cho việc gọi API và render.

## 3. Chặng 1: `/video-moi [chủ đề]` → điểm duyệt 1

1. **Chọn đề**: nếu bạn không đưa chủ đề, Claude quét tin 24 giờ qua từ danh sách nguồn trong `config.json` và chấm theo 3 câu: nóng? số lớn? hệ quả cho người Việt? Thiếu câu 3 thì loại. Đưa ra 3 đề tốt nhất vào `chu-de.md`.
2. **Đọc nguồn gốc**: mỗi con số là một mục trong `nguon.json`: `{id, gia_tri, trich_dan, url, ngay_truy_cap, anh_chup, trang_thai: xac-minh | so-bo | chua-xac-minh}`. Trang chặn truy cập tự động thì ghi là thiếu nguồn, không thay bằng tin thứ cấp.
3. **Viết kịch bản** bằng `yt-script`. Câu nào có số thì gắn `[#id]` trỏ tới `nguon.json`. Lời đọc viết số thành chữ.
4. **Tự kiểm** (`kiem.py` + một agent độc lập): mọi số có `[#id]`; giá trị khớp `nguon.json`; không còn giữ chỗ `[...]`; số `so-bo` có câu cảnh báo.
5. **Điểm duyệt 1**: trang duyệt gồm 3 đề, kịch bản, và bảng số → nguồn có link. Bạn duyệt thì `trang-thai` chuyển sang `da-duyet`.

## 4. Chặng 2: `/video-dung` → điểm duyệt 2

1. **Giọng**: `tts.py` gọi ElevenLabs có timestamp, gửi theo từng đoạn, rồi ghép thành `giong.mp3` + `giong-timing.json`.
2. **Chia cảnh**: Claude cắt lời đọc theo timestamp từ thành 80–120 cảnh (4–8 giây/cảnh) và ghi vào `canh.json`. Mỗi cảnh thuộc 1 trong 6 mẫu:
   - `minh-hoa`: hình SVG isometric + nhãn chữ
   - `bieu-do`: đường/cột/so sánh, số lấy từ `nguon.json`, góc dưới ghi nguồn
   - `so-lon`: một con số chiếm màn hình
   - `nhan-vat`: ảnh công khai + dòng ghi công
   - `trang-nguon`: ảnh chụp tài liệu gốc, tô vàng chỗ có số
   - `chuong`: thẻ tên chương
3. **Thư viện SVG**: làm sẵn khoảng 30 hình theo brand. Cảnh nào thiếu hình thì Claude vẽ thêm SVG và lưu vào `pipeline/svg/`.
4. **Ảnh nhân vật**: chỉ lấy từ Wikimedia Commons, lọc giấy phép PD / CC BY / CC BY-SA, lưu thông tin ghi công. Không tìm được thì dùng hình minh họa thay thế.
5. **Dựng + render**: HyperFrames dựng từ `canh.json` với chuyển cảnh, nhạc nền miễn phí bản quyền cố định và phụ đề, render ra `final.mp4` 1920×1080 30fps, kèm `phu-de.srt`.
6. **Shorts**: `yt-shorts` chọn 2–3 đoạn trọn ý, render lại khổ 1080×1920 từ cùng dữ liệu cảnh.
7. **Tự kiểm hình**: mỗi cảnh xuất 1 khung, ghép thành bảng xem nhanh. Claude soi bảng để bắt lỗi chữ tràn, hình chồng, cảnh trống. Kiểm thêm độ dài hình bằng độ dài tiếng (±0,5 s).
8. **Đóng gói**:
   - `yt-package` viết 3 cặp tiêu đề + chữ thumbnail.
   - Thumbnail mặc định là mẫu chữ brand (`brand/make_brand.py`).
   - **Thêm 1 phương án dùng ảnh TobyFlow** (nền hoặc hình minh họa gây chú ý). Chữ tiếng Việt được chồng lên bằng code, không để AI viết chữ. Không dùng mặt người thật, không dùng logo hãng.
   - Mọi thumbnail được thử thu nhỏ còn 168 px.
   - `yt-chapters` lấy mốc chương từ timestamp thật. `yt-seo` viết mô tả; mục nguồn sinh từ `nguon.json`, mục ghi công ảnh sinh từ bước 4.
9. **Điểm duyệt 2**: trang duyệt gồm video, Shorts, các phương án tiêu đề/thumbnail để chọn, mô tả, và cảnh báo còn lại.

## 5. Chặng 3: `/video-dang`

`upload.py` (YouTube Data API v3, OAuth bằng tài khoản kênh, token lưu trong Keychain):
- Từ chối chạy nếu `trang-thai` chưa có cả 2 điểm duyệt.
- Upload ở chế độ riêng tư + `publishAt` theo giờ trong lịch; gắn thumbnail đã chọn, mô tả, SRT, danh sách phát; đánh dấu nội dung tổng hợp theo quy định công khai AI của YouTube.
- Shorts hẹn giờ theo lịch.
- Ghi một dòng vào bảng theo dõi: ngày, tiêu đề, giờ đăng, link.

## 6. Xử lý lỗi

- Bước lỗi ghi lý do vào `trang-thai.json`, giữ nguyên file đã xong, lần chạy sau làm lại đúng bước đó.
- ElevenLabs lỗi một đoạn thì chỉ gửi lại đoạn đó.
- Không có đường nào upload được video chưa duyệt.
- Khóa API (ElevenLabs, YouTube, TobyFlow) đọc từ Keychain/biến môi trường, không ghi vào file trong thư mục dự án.

## 7. Kiểm thử

- Tự kiểm trong script: timestamp khớp độ dài audio; mọi `[#id]` tồn tại trong `nguon.json`; mọi cảnh có hình; video và tiếng dài bằng nhau.
- Chạy thử toàn bộ bằng video 1 (so sánh gói AI): kịch bản đã có, chỉ còn điền tỷ giá. Mục tiêu đăng thứ Sáu 13/11/2026 19:00.
- Trước khi viết chặng 2: làm 6 mẫu cảnh + khoảng 10 hình SVG đầu tiên, đưa bạn duyệt hình.

## 8. Ngoài phạm vi đợt này

- Tự chạy theo lịch + thông báo điện thoại (hướng B), làm sau khi pipeline chạy ổn 1–2 tuần.
- Tự trả lời bình luận, đọc retention tự động.
- Render trên cloud.

## 9. Bạn cần làm một lần

1. Đăng ký ElevenLabs, tạo khóa API, chọn giọng.
2. Tạo dự án Google Cloud, bật YouTube Data API, đăng nhập OAuth bằng tài khoản kênh.
3. Duyệt bộ mẫu cảnh + thư viện SVG ban đầu.
4. Nên chuyển token TobyFlow trong `.mcp.json` ra khỏi thư mục đang đồng bộ iCloud.
