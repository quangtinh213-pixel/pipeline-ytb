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
- Chạy `uv run python -m tttc.chia V` để có `V/canh-khung.json`: mốc `start/end` đã cắt đúng ranh giới từ, cảnh liền
  nhau, cảnh đầu 0, cảnh cuối = `duration`, kèm `loi` (lời đọc của cảnh). Chép sang `canh.json`, điền `mau` và nội dung
  từng cảnh; **không tự đổi mốc** (cần đổi thì sửa tay và chạy lại `tttc.canh`).
- Chuẩn kênh mẫu: 2,8–4,5 s/cảnh (cảnh báo ngoài 2,5–6 s, lỗi ngoài 1,5–10 s), khoảng 165–220 cảnh/11 phút.
  Đổi mẫu liên tục, không 3 cảnh liền cùng mẫu.
- Mỗi số hiện trên màn hình phải có `nguon_id` (hoặc `bieu_do.nguon_id`) trỏ vào `nguon.json`; giá trị lấy từ nguồn, không gõ tay khác đi.
- Đầu mỗi beat của kịch bản là một cảnh `chuong`.
- Nhãn `minh-hoa` ≤ 5 từ; nhãn là ý chính, không lặp nguyên lời đọc.
- **Chuyển động lặp** `dong` (mọi cảnh `minh-hoa` mặc định `bob`): `xoay` cho đồng xu/vòng quay, `dap` cho vật đang hoạt động
  (máy chủ, chip), `chop` cho điểm nhấn vàng; `""` để đứng yên. Đạo cụ tự nhấp nhô lệch pha.
- Cho sân khấu có chuyện xảy ra: `minh-hoa` thêm `phu` (1–2 đạo cụ: cay, dong-xu, container, nguoi, mui-ten-len/xuong…);
  `so-lon` thêm `huong` khi số tăng/giảm và `svg` hình nền hợp nghĩa; `bieu-do` thêm `chu_thich` ≤ 2 từ cho cột nổi bật.
- Nền và chuyển cảnh tự gán theo chương; chỉ ghi `nen` khi muốn phá nhịp có chủ đích.
- **Nhịp con**: mỗi cảnh ghi `nhip` = các cụm từ giọng đọc nói trong cảnh, theo thứ tự bước của mẫu
  (`DEFAULT_STEPS` trong `tttc/dung.py`; `bieu-do` = một cụm cho mỗi cột + một cụm cho cột nổi bật).
  Mục tiêu: hình đổi khoảng 2 s một lần. `tttc.canh` báo lỗi nếu cụm không có trong lời đọc của cảnh.
- **Tỉ lệ cảnh** (docs/nghien-cuu/hinh-anh-doi-thu.md): minh họa 25%, số liệu 25%, `b-roll` 20%,
  bằng chứng (`trich-bao`, `trang-nguon`) 15%, còn lại 15%. Không 3 cảnh liền cùng nhóm.
- **`quy-trinh`** (một chuỗi 3–6 bước nối bằng mũi tên: quy trình, chuỗi cung ứng, "tiền đi đâu"): `buoc` = danh sách
  `{nhan, svg?}` (không có `svg` thì hiện số thứ tự), `noi_bat` = chỉ số bước đang nói tới (bước còn lại mờ đi), `nhip` = một
  cụm lời đọc cho mỗi bước.
- **`so-sanh`** (hai vật cạnh nhau, "gấp N lần", "sân bóng so với hạt gạo"): `trai` và `phai` = `{nhan, svg, so?, don_vi?, to?}`;
  `to` (0–1) là cỡ hình tương đối, hai hình đứng trên cùng một đường nền; `ti_le` = nhãn "gấp ~700 lần" (nhãn tự tính phải
  có nguồn `tu-tinh`); có `so` thì bắt buộc `nguon_id` và số + đơn vị phải khớp nguồn.
- **`thoi-gian`** (so nhịp nhiều bên theo năm: "Singapore 2 năm, Ấn Độ 4 năm, mình thì sao"): `truc` {tu, den, don_vi},
  `hang` 2–5 phần tử `{nhan, tu, den, noi_bat?}`; năm trên thanh phải có trong `gia_tri` của `nguon_id` (hoặc là nguồn
  `tu-tinh`); một hàng một cụm `nhip`.
- **`trich-bao`**: `trich` chép nguyên văn từ `nguon.json:trich_dan` (≤ 25 từ), `to_vang` là cụm chứa ý/số chính.
  Không chụp nguyên trang báo; mẫu tự sắp chữ lại kèm tên báo (`nguon.ten`) và ngày.
- **`b-roll`** – clip riêng cho từng video (kho chung chỉ là phần nền):
  1. Liệt kê mọi cảnh `b-roll` của video và hình cần thấy (vd "cánh quạt điện gió", "chợ Bến Thành").
  2. Tìm trong `pipeline/broll-kho/kho.json` theo `tu_khoa`/`mo_ta`, độ dài ≥ cảnh + 1 s. Có clip hợp và chưa
     dùng trong video này thì dùng.
  3. Không có: mở trình duyệt có sẵn ở `https://www.pexels.com/`, dán `pipeline/scripts/pexels-tim.js` vào
     `javascript_tool`, gọi `await pxl("<từ khoá tiếng Anh cụ thể>", 4)`. Chọn 1–2 ứng viên hợp nhất.
  4. `broll.tai_ve(link, "<chu-de>-<id>", broll.KHO, f"Video: {user} trên Pexels", nguon=page,
     mo_ta="<mô tả tiếng Việt>", tu_khoa=[...Việt + Anh...])` – chỉ nhận videos.pexels.com / cdn.pixabay.com /
     upload.wikimedia.org.
  5. `broll.soi(clip, V/frames/broll-<ten>.jpg)` rồi **xem ảnh**: có mặt người nhận ra được, logo hãng, chữ nước
     ngoài lớn, tiền nước khác khi nói về tiền Việt → xoá clip khỏi kho (tệp + mục kho.json), tìm clip khác.
  6. `broll.nhap(KHO / tep, V, ghi_cong=<từ kho.json>, bat_dau=<giây>, do_dai=<độ dài cảnh + 0,5>)`; ghi
     `video` = tên tệp trả về. Một clip dùng cho một cảnh mỗi video.
  Không tìm được clip đạt sau 2 lượt từ khoá: đổi cảnh đó sang `minh-hoa` hoặc `so-lon`, không dùng clip kém.
  Có khoá Pexels trong Keychain thì `broll.search`/`pick`/`download` thay cho bước 3–4.
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
2. `scripts/render.sh V/composition V/final.mp4 delivery` (đo 09/11/2026 trên máy i9 16 luồng: delivery ≈ 2× thời lượng, khoảng 25 phút cho video 12 phút; chạy nền; xem docs/nghien-cuu/do-render-2026-11-09.md).
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
   - Phương án 1: `tttc.thumb.make([(dòng, "white"|"yellow"), ...], V/thumbnails/1.png)`.
   - Phương án 2: CoDesign (IMG.LY). Trước `edit` đầu tiên nạp skill `codesign:handbook`, `codesign:api`, `codesign:judge`
     (cùng một lượt) – bỏ bước hỏi ý, brief đã đủ: trang 1280×720, nền #111111, chữ trắng/vàng #FFC800 đậm, chữ
     thumbnail của phương án 2, có thể thêm một hình/đạo cụ (không mặt người thật, không logo hãng). Chạy vòng `judge`
     tới khi qua, `export` png → `V/thumbnails/2.png`; > 2 MB thì xuất lại nhỏ hơn (YouTube từ chối). Tạo bản nhỏ:
     `Image.open(p).resize((168, 94), Image.LANCZOS).save(V/thumbnails/2-168px.png)`.
     CoDesign hỏng/chưa đăng nhập: dùng `thumb.make` như phương án 1 và ghi lý do trong `dong-goi.md`.
   - Phương án chia đôi (khuôn kênh mẫu, thay cho một trong ba phương án): `tttc.thumb.chia_doi(trai, phai, dong, out, ghi_cong)`.
     `trai` = chân dung từ `anh.search` → `anh.pick` → `anh.download` (giấy phép tự do, có ghi công; `pick` trả None thì
     `trai=None`, ảnh phải được cắt đôi); `phai` = `thumb.khung_tu_video(V/final.mp4, t, V/thumbnails/khung.png, bo_day=0.12)`
     của cảnh minh họa đẹp nhất (bỏ dải phụ đề); `dong` ≤ 2 dòng, mỗi dòng 3–5 chữ; `ghi_cong` = `anh/ghi-cong.json:ghi_cong`.
     Không dùng ảnh người thật ngoài Wikimedia Commons, không logo hãng.
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
