---
name: video-dung
description: Chặng 2 của pipeline video kênh Túi Tiền Công Nghệ – giọng ElevenLabs, chia cảnh, hình minh họa, render HyperFrames, Shorts, đóng gói tiêu đề/thumbnail/mô tả, rồi dừng ở điểm duyệt 2. Dùng khi người dùng gõ /video-dung, "dựng video", hoặc nói "duyệt phương án N" cho video đang chờ duyệt 2.
---

# /video-dung [thư mục video]

Spec mục 4. Chạy Python trong `pipeline/` bằng `uv run`. V = `../videos/<slug>`.
Mỗi bước: `set_step(V, <bước>, "xong")`; lỗi thì `set_step(V, <bước>, "loi", "<lý do>")`, dừng và báo.

## 0. Điều kiện
- `duyet-1` phải `da-duyet`. Không thì dừng: "Chạy /video-moi và duyệt kịch bản trước."
- Người dùng nói "duyệt phương án N" cho video `duyet-2=cho-duyet`: `set_field(V, "chon", N)`,
  `set_step(V, "duyet-2", "da-duyet")`, báo "Chạy /video-dang". Hết.
- Người dùng ghi chỗ cần sửa ở duyệt 2: sửa đúng bước liên quan (cảnh → bước 2–4, tiêu đề → bước 6), chạy lại từ đó.
- Đọc `next_step(V)`, bắt đầu từ bước chưa xong.

## 1. giong
`uv run python -m tttc.tts V` (khoá ElevenLabs trong Keychain). Đoạn đã có thì không gọi lại (không mất tiền).
Kiểm `giong-timing.json`: `words[-1].end ≤ duration`.

## 2. canh
Viết `V/canh.json` theo docstring đầu `tttc/dung.py` (6 mẫu, trường từng mẫu):
- Cắt cảnh **đúng ranh giới từ** trong `giong-timing.json`; cảnh liền nhau, cảnh đầu 0, cảnh cuối = `duration`.
- 4–8 s/cảnh, 80–120 cảnh/11 phút. Đổi mẫu liên tục, không 3 cảnh liền cùng mẫu.
- Mỗi số hiện trên màn hình phải có `nguon_id` (hoặc `bieu_do.nguon_id`) trỏ vào `nguon.json`; giá trị lấy từ nguồn, không gõ tay khác đi.
- Đầu mỗi beat của kịch bản là một cảnh `chuong`.
- Nhãn `minh-hoa` ≤ 5 từ; nhãn là ý chính, không lặp nguyên lời đọc.
- Cho sân khấu có chuyện xảy ra: `minh-hoa` thêm `phu` (1–2 đạo cụ: cay, dong-xu, container, nguoi, mui-ten-len/xuong…);
  `so-lon` thêm `huong` khi số tăng/giảm và `svg` hình nền hợp nghĩa; `bieu-do` thêm `chu_thich` ≤ 2 từ cho cột nổi bật.
- Nền và chuyển cảnh tự gán theo chương; chỉ ghi `nen` khi muốn phá nhịp có chủ đích.
- **Nhịp con**: mỗi cảnh ghi `nhip` = các cụm từ giọng đọc nói trong cảnh, theo thứ tự bước của mẫu
  (`DEFAULT_STEPS` trong `tttc/dung.py`; `bieu-do` = một cụm cho mỗi cột + một cụm cho cột nổi bật).
  Mục tiêu: hình đổi khoảng 2 s một lần. `tttc.canh` báo lỗi nếu cụm không có trong lời đọc của cảnh.
- **Tỉ lệ cảnh** (docs/nghien-cuu/hinh-anh-doi-thu.md): minh họa 25%, số liệu 25%, `b-roll` 20%,
  bằng chứng (`trich-bao`, `trang-nguon`) 15%, còn lại 15%. Không 3 cảnh liền cùng nhóm.
- **`trich-bao`**: `trich` chép nguyên văn từ `nguon.json:trich_dan` (≤ 25 từ), `to_vang` là cụm chứa ý/số chính.
  Không chụp nguyên trang báo; mẫu tự sắp chữ lại kèm tên báo (`nguon.ten`) và ngày.
- **`b-roll`**: chọn clip trong kho `pipeline/broll-kho/kho.json` theo `tu_khoa`/`mo_ta`, độ dài ≥ cảnh + 1 s;
  `tttc.broll.nhap(KHO / tep, V, ghi_cong=<từ kho.json>, bat_dau=<giây>, do_dai=<độ dài cảnh + 0,5>)`;
  ghi `video` = tên tệp trả về. Không có clip hợp: thêm clip mới vào kho (Pexels/Pixabay, tải thủ công) hoặc,
  nếu có khoá Pexels trong Keychain, `broll.search` → `pick` → `download`. Mọi clip: xem 3 khung trước khi dùng –
  **không mặt người nhận ra được, không logo hãng, không chữ nước ngoài lớn**. Một clip dùng cho một cảnh mỗi video.
- Ảnh trang nguồn: chụp lại trang bằng trình duyệt ở độ phân giải ≥ 1600 px rộng, lưu `V/nguon/<id>.png`;
  `khung` là vùng chứa con số (x,y,w,h theo % ảnh).

## 3. hinh
- Cảnh `minh-hoa` cần hình chưa có trong `pipeline/svg/`: thêm hàm vào `pipeline/svg/ve.py` theo `svg/README.md`,
  chạy `uv run python svg/ve.py`. Không vẽ chữ, không logo.
- Cảnh `nhan-vat`: `tttc.anh.search("<tên người>")` → `pick()` → `download(item, V)`; ghi `anh` = tên tệp trả về.
  `pick` trả None thì đổi cảnh đó sang `minh-hoa`.
- `uv run python -m tttc.canh V` tới khi `0 lỗi` (cảnh báo 4–8 s được phép khi có lý do).

## 4. render
1. `uv run python -c "from tttc import dung; dung.compose('V')"`
2. `scripts/render.sh V/composition V/final.mp4 delivery` (khoảng 1–2 giờ cho 11 phút; chạy nền).
3. `dung.contact_sheet('V/final.mp4', canh, 'V/frames/soi-hinh.png')` – **xem ảnh này**: chữ tràn, hình chồng,
   cảnh trống, số sai. Sửa `canh.json`/mẫu, render lại.
4. `dung.check_av('V/final.mp4', 'V/giong.mp3')` phải rỗng.

## 5. shorts
- Gọi skill `yt-shorts` với `kich-ban.md` + `giong-timing.json`: chọn 2–3 đoạn trọn ý, 20–55 s, mỗi đoạn trùng ranh giới cảnh.
- Mỗi đoạn k: `dung.compose('V', w=1080, h=1920, scene_range=(i, j), out=f'short-{k}')`
  rồi `scripts/render.sh V/short-k V/shorts/k.mp4 delivery`.
- Giờ đăng Short: theo `lich-4-tuan-dinh-vi-A.md` (Shorts rơi vào ngày sau video dài).

## 6. dong-goi
1. Gọi skill `yt-package`: 3 cặp tiêu đề (≤ 100 ký tự, ưu tiên ≤ 60) + chữ thumbnail (≤ 3–4 chữ).
2. Thumbnail:
   - Phương án 1, 2: `tttc.thumb.make([(dòng, "white"|"yellow"), ...], V/thumbnails/N.png)`.
   - Phương án 3: TobyFlow `gen_image` (gọi `list_capabilities` trước, poll `get_job`) tạo **nền 16:9**. Prompt phải ghi:
     không chữ, không mặt người thật, không logo hãng, tông tối gần đen với điểm nhấn vàng #FFC800, một vật thể chính.
     Tải ảnh về `V/thumbnails/nen-3.png`, rồi `thumb.make(lines, V/thumbnails/3.png, background=V/thumbnails/nen-3.png)`.
   - Mở bản `-168px` của từng thumbnail: đọc không ra chữ thì sửa.
3. Gọi skill `yt-chapters` với mốc từ `giong-timing.json:paragraphs` (mốc thật, không ước tính).
4. Gọi skill `yt-seo` cho mô tả + tags. Mô tả kết thúc bằng:
   - "📎 Nguồn" – mỗi mục `nguon.json`: giá trị, URL, ngày truy cập.
   - "🖼 Ghi công ảnh" – mỗi dòng `anh/ghi-cong.json:ghi_cong`.
   - Không có ký tự `<` `>` (YouTube từ chối).
5. Ghi `V/dong-goi.json` (đọc bởi `tttc.dang`):
   `{"phuong_an":[{"tieu_de","chu_thumb":[...],"file_thumb":"thumbnails/N.png"}×3], "mo_ta", "tags":[...],
     "shorts":[{"file":"shorts/k.mp4","tieu_de":"... #shorts","ngay":"dd/mm/yyyy","gio":"HH:MM"}]}`
   và `V/dong-goi.md` bản dễ đọc của cùng nội dung.

## 7. duyet-2
- `uv run python -c "from tttc.duyet import render_review_2; print(render_review_2('V'))"`
- `set_step(V, "duyet-2", "cho-duyet")`; gửi `duyet-2.html` (SendUserFile, render) cùng `frames/soi-hinh.png`.
- Tóm tắt: độ dài video, số cảnh, 3 tiêu đề, cảnh báo còn lại. **Dừng.** Không tự chọn phương án.
