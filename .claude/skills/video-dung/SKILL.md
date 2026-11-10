---
name: video-dung
description: Chặng 2 của pipeline video của kênh – giọng ElevenLabs, chia cảnh, hình minh họa, render HyperFrames, Shorts, đóng gói tiêu đề/thumbnail/mô tả, rồi dừng ở điểm duyệt 2. Dùng khi người dùng gõ /video-dung, "dựng video", hoặc nói "duyệt phương án N" cho video đang chờ duyệt 2.
---

# /video-dung [thư mục video]

Spec mục 4. Chạy Python trong `pipeline/` bằng `uv run`. V = `../videos/<slug>`.
Mỗi bước: `set_step(V, <bước>, "xong")`; lỗi thì `set_step(V, <bước>, "loi", "<lý do>")`, dừng và báo.

## 0. Điều kiện
- `duyet-1` phải `da-duyet`. Không thì dừng: "Chạy /video-moi và duyệt kịch bản trước."
- Người dùng nói "duyệt phương án N" cho video `duyet-2=cho-duyet`: `set_field(V, "chon", N)`,
  `set_step(V, "duyet-2", "da-duyet")`, báo "Chạy /video-dang". Hết.
- Người dùng ghi chỗ cần sửa ở duyệt 2: sửa đúng bước liên quan (cảnh → bước 2–4, tiêu đề → bước 5), chạy lại từ đó.
- Đọc `next_step(V)`, bắt đầu từ bước chưa xong.

## 1. giong
`uv run python -m tttc.tts V` (khoá ElevenLabs trong Keychain). Đoạn đã có thì không gọi lại (không mất tiền).

**Giọng VieNeu-TTS chạy trong máy** (không tốn tiền, không cần khoá; cần `~/Documents/VieNeu-TTS` đã cài): thay cho `tttc.tts`:

    uv run python -m tttc.giong_vieneu nghe-thu <thư mục> "Hải Đăng" "Thiện Minh"   # nghe thử giọng, một lần
    uv run python -m tttc.giong_vieneu V                                              # tạo giong.mp3 + giong-timing.json

Cấu hình trong `config.json:vieneu` (tuỳ chọn): `voice` (mặc định "Hải Đăng"), `pause_cau` (0,25 s), `pause_doan` (0,5 s),
`python` (mặc định python của VieNeu-TTS), `phat_am` = `{"ChatGPT": "chát gi pi ti"}` đổi chữ **chỉ để gửi cho giọng đọc**
khi đọc sai tên tiếng Anh (mốc từ vẫn theo chữ kịch bản). Mỗi câu một tệp wav trong `V/giong-vieneu/`, tên theo nội dung +
giọng nên sửa câu nào chỉ làm lại câu đó; mốc từ chỉ sai trong phạm vi một câu, đã cắt lặng đầu/cuối câu. Tốc độ khoảng 0,7–1,2×
thời lượng giọng trên máy i9 (video 12 phút mất 10–15 phút). Số trong lời đọc phải viết thành chữ như mọi giọng khác.

**Giọng làm thủ công** (thu âm, ElevenLabs web, TTS khác – không dùng API): người dùng đưa một hoặc nhiều tệp tiếng, đúng thứ
tự kịch bản, đọc đúng chữ trong `Lời đọc` (số viết thành chữ). Thay cho `tttc.tts`:

    uv run python -m tttc.giong_tay V tep1.mp3 [tep2.mp3 ...] [--srt phu-de.srt]

Ghép thành `V/giong.mp3`, lấy mốc từng từ bằng phiên âm (`hyperframes transcribe`, whisper `small` tiếng Việt; **lần đầu tải mô
hình ~466 MB: hỏi người dùng trước**) hoặc nhập phụ đề `.srt` nếu có (không cần tải, mốc chính xác ở mức cue), rồi căn từng từ
kịch bản vào đó và ghi `giong-timing.json`. Lệnh in % từ khớp trực tiếp; dưới 50% là nhầm tệp hoặc đọc sai kịch bản, không ghi gì.
Số đọc thành chữ bị phiên âm thành chữ số vẫn căn được (lấy khoảng của số), nhưng mốc từng từ trong khối đó chỉ gần đúng.
Kiểm `giong-timing.json`: `words[-1].end ≤ duration`.

## 1b. dao-dien
Claude là đạo diễn: quyết mỗi cảnh phục vụ điều gì trước khi chọn mẫu và hình (spec: docs/superpowers/specs/2026-11-09-chat-luong-hinh-anh-design.md mục 4). Muốn bỏ qua (video cũ, hoặc `canh.json` viết tay như mục 2): vẫn phải `set_step(V, "dao-dien", "xong", "bỏ qua: canh.json viết tay")`, nếu không `next_step` cứ trả `dao-dien` và cổng chạy khô báo thiếu giờ kết thúc.

**Bốn nguyên tắc đạo diễn:**
1. **Hình bổ nghĩa, không chép lời.** Mỗi cảnh phải trả lời: cảnh này giúp người xem hiểu hay cảm thấy điều gì mà lời đọc chưa tự nói ra?
2. **Mỗi beat có một khoảnh khắc nhấn** (đỉnh) và một nhịp thở trước hoặc sau nó.
3. **Ẩn dụ phải kiểm được.** Hình ẩn dụ không được thêm khẳng định không có nguồn (ví dụ không vẽ đám đông giận dữ khi nguồn không nói về phản ứng công chúng). Mọi số trên màn hình vẫn có `nguon_id`.
4. **Đa dạng có chủ đích:** đổi phông, vật chính, bố cục khi ý đổi, không đổi chỉ để đổi.

**Cách làm** (giới hạn khoảng 45 phút; vượt thì giảm cảnh trọng điểm xuống ~20%, không bỏ bước):
1. `uv run python -m tttc.chia V` để có `V/canh-khung.json` (mốc và `loi` từng cảnh).
2. Viết `V/dao-dien.json` = `{"scenes": [...]}`, mỗi cảnh trong `canh-khung.json` một mục: `y` (người xem phải hiểu/cảm thấy gì), `nhip_cam_xuc`
   (`mo|leo|dinh|dao-chieu|ha|chot`), `trong_diem` (true/false), `canh` (`mau` + trường của mẫu như mục 2), và với `minh-hoa`:
   `san_khau`, `vat_chinh`, `dao_cu` (≤ 4 tên SVG), `may_quay` (`dung|day-vao|keo-ra|lia|he-lo`). Cảnh trọng điểm (mở bài, số lớn,
   đảo chiều, kết, đỉnh mỗi beat; khoảng **30%** số cảnh) bắt buộc có `an_du` (hình ẩn dụ và vì sao đúng với nguồn) và `may_quay` khác `dung`;
   chỉ cảnh này được chỉ đạo sâu, còn lại theo luật đa dạng (không 3 cảnh liền cùng mẫu/phông/vật chính). `am_thanh`, `dan` tùy chọn.
3. Chia theo beat cho subagent chạy song song, mỗi agent viết phần `dao-dien.json` của beat mình; một agent tổng hợp ghép lại và kiểm nhịp
   cảm xúc toàn video (có đỉnh và nhịp thở ở mỗi beat, không dồn trọng điểm vào một chỗ).
4. `uv run python -m tttc.dao_dien V`: in Lỗi/Cảnh báo, **có Lỗi thì không ghi gì**; sạch Lỗi thì sinh `V/canh.json` (cũ lưu `canh-truoc-dao-dien.json`) và `V/hinh-thieu.json`.
   Vẽ từng hình trong `hinh-thieu.json` bằng `pipeline/svg/ve.py` (mục 3), rồi chạy lại lệnh để Cảnh báo hết.
5. **Giám khảo hình ảnh** (subagent độc lập, không chia sẻ ngữ cảnh): đưa cho nó `dao-dien.json`, `canh-khung.json` (lời đọc từng cảnh), `nguon.json`
   và kết quả `uv run python -m tttc.chat_luong V` (bảng số đo), cùng nội dung `pipeline/phong-cach/giam-khao-hinh.md`. Nó ghi `V/dao-dien-cham.json`.
   Claude sửa `dao-dien.json` theo cảnh khô và ẩn dụ vượt nguồn nó chỉ ra, chạy lại bước 4, chấm lại: **tối đa 2 vòng sửa**.
   Giám khảo là một agent chứ không phải người xem thật; điểm chỉ là mốc, phép thử thật là retention sau khi đăng.
   Chưa được phép tạo subagent thì dùng agy làm giám khảo: ghép nội dung `giam-khao-hinh.md` + `dao-dien.json` (kèm mẫu, nhãn, lời đọc từng cảnh) + `nguon.json` + bảng số đo rồi gọi `tttc.phan_bien.goi`; vòng 2 dùng `--conversation` cũ (cách làm và kết quả thử: docs/nghien-cuu/do-kho-nen-2026-11-09.md). Giám khảo chấm dễ tay và chưa bắt được ẩn dụ vượt nguồn: người viết `an_du` vẫn phải tự kiểm từng ẩn dụ với `nguon.json`.

## 2. canh
Viết `V/canh.json` theo docstring đầu `tttc/dung.py` (6 mẫu, trường từng mẫu). **Video có `dao-dien.json` thì `canh.json` đã được sinh ở mục 1b:**
chạy `uv run python -m tttc.canh V` rồi `uv run python -m tttc.chat_luong V` trên tệp đó, chỉ sửa tay khi hai lệnh báo (sửa ở `dao-dien.json` rồi sinh lại, đừng sửa `canh.json` sinh ra).
- Chạy `uv run python -m tttc.chia V` để có `V/canh-khung.json`: mốc `start/end` đã cắt đúng ranh giới từ, cảnh liền
  nhau, cảnh đầu 0, cảnh cuối = `duration`, kèm `loi` (lời đọc của cảnh). Chép sang `canh.json`, điền `mau` và nội dung
  từng cảnh; **không tự đổi mốc** (cần đổi thì sửa tay và chạy lại `tttc.canh`).
- Chuẩn kênh mẫu: 2,8–4,5 s/cảnh (cảnh báo ngoài 2,5–6 s, lỗi ngoài 1,5–10 s), khoảng 165–220 cảnh/11 phút.
  Đổi mẫu liên tục, không 3 cảnh liền cùng mẫu.
- **Mọi chữ hiện trên màn hình là tiếng Việt** (nhãn, tiêu đề, trích, đơn vị, chữ trên hình); tên riêng và viết tắt (Nvidia, GPU) giữ nguyên. Trích nguồn tiếng Anh: `trich` giữ nguyên văn để kiểm chứng với `trich_dan`, rồi viết `trich_vi` (bản dịch sát nghĩa của kênh, không thêm ý) và `to_vang_vi` (cụm nằm trong `trich_vi`); màn hình chỉ hiện bản dịch kèm nhãn "Bản dịch của kênh". `tttc.canh` báo Lỗi nếu còn chữ có vẻ tiếng Anh.
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
- **Tỉ lệ cảnh** (chuẩn kênh mẫu, docs/nghien-cuu/kenh-mau-motcongnghe-2026-11-09.md mục 4; `tttc.chat_luong` đo):
  đồ họa tự dựng (`minh-hoa`, `quy-trinh`, `so-sanh`, `thoi-gian`, `so-lon`, `bieu-do`, `chuong`) ≥ 70%;
  bằng chứng (`trich-bao`, `trang-nguon`) 8–18%; ảnh/video đời thật (`b-roll`, `nhan-vat`) ≤ 15%. Không 3 cảnh liền cùng mẫu.
- **Nhân vật dẫn chuyện "Túi"** (mọi mẫu): `dan: {the: chao|ngac-nhien|nghi, goc?: phai|trai, huong?, tu?: "cụm lời đọc"}` (khi có `pipeline/nhan-vat/kit.json`: `the` và `huong` lấy từ bộ nhân vật; `huong` mặc định nghiêng về giữa màn hình; `tttc.canh` báo Lỗi nếu cặp không có trong kit) — hiện ở góc dưới,
  bật vào đúng lúc nói `tu` (không có `tu` thì 0,3 s sau đầu cảnh), nhấp nhô và chớp mắt. Dùng ≥ 1 lần mỗi chương và ở các
  khoảnh khắc "bất ngờ" (số lớn, đảo chiều, câu hỏi hứa): `chao` khi mở chương, `ngac-nhien` trước một con số gây sốc, `nghi` khi
  đặt câu hỏi. Không dùng trong Shorts (khung dọc). Chọn `goc` phía không có chữ/số quan trọng.
- **`quy-trinh`** (một chuỗi 3–6 bước nối bằng mũi tên: quy trình, chuỗi cung ứng, "tiền đi đâu"): `buoc` = danh sách
  `{nhan, svg?}` (không có `svg` thì hiện số thứ tự), `noi_bat` = chỉ số bước đang nói tới (bước còn lại mờ đi), `nhip` = một
  cụm lời đọc cho mỗi bước.
- **`ban-do`** (bản đồ vị trí: hàng hóa đi từ đâu tới đâu, nước nào nằm ở đâu): `diem` = 2–6 phần tử `{nhan, vi_do, kinh_do, nuoc?, noi_bat?}` (toạ độ thủ đô hoặc thành phố chính, độ thập phân; `nuoc` = mã ADM0_A3 như VNM, USA, MYS để tô sáng nước đó), `noi` = mũi tên cong `{tu, den, nhan?}` nối hai điểm theo chỉ số, `nhip` = một cụm lời đọc cho mỗi điểm rồi mỗi mũi tên. Hình nước lấy từ `pipeline/du-lieu/nuoc.json` (Natural Earth, phạm vi công cộng; tạo lại bằng `uv run python -m tttc.ban_do <geojson>`), mẫu tự ghi nguồn dữ liệu. **Chọn điểm gần nhau** (cùng khu vực) để hình nước đủ lớn; hai điểm cách nửa vòng Trái Đất thì nước nhỏ chỉ còn là chấm. **Chưa vẽ đảo nhỏ và quần đảo** (dữ liệu bỏ vòng dưới 0,4 độ²): bản đồ không thể hiện Hoàng Sa, Trường Sa; cảnh nào cần chủ quyền biển đảo thì dùng ảnh chụp tài liệu hoặc đồ họa riêng, không dựa vào mẫu này. Nhãn là tên nước/thành phố bằng tiếng Việt (≤ 5 từ), nhãn mũi tên ngắn; điểm cần nhìn đặt `noi_bat`.
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
- `uv run python -m tttc.canh V` tới khi `0 lỗi` (cảnh báo độ dài 2,5–6 s được phép khi có lý do).
- `uv run python -m tttc.chat_luong V` tới khi **0 Lỗi**; đọc từng Cảnh báo (nhịp, tỉ lệ mẫu, sự kiện hình và hiệu ứng
  âm thanh mỗi phút, tốc độ đọc) và sửa hoặc ghi lý do giữ. Chỉ sang bước render khi đạt (render tốn cả chục phút).

## 4. render
1. `uv run python -c "from tttc import dung; dung.compose('V')"`
2. `scripts/render.sh V/composition V/final.mp4 delivery` (đo 09/11/2026 trên máy i9 16 luồng: delivery ≈ 2× thời lượng, khoảng 25 phút cho video 12 phút; chạy nền; xem docs/nghien-cuu/do-render-2026-11-09.md).
3. `dung.contact_sheet('V/final.mp4', canh, 'V/frames/soi-hinh.png')` – **xem ảnh này**: chữ tràn, hình chồng,
   cảnh trống, số sai. Sửa `canh.json`/mẫu, render lại.
4. `dung.check_av('V/final.mp4', 'V/giong.mp3')` phải rỗng.

## 5. dong-goi
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

## 6. duyet-2
- `uv run python -c "from tttc.duyet import render_review_2; print(render_review_2('V'))"`
- `set_step(V, "duyet-2", "cho-duyet")`; gửi `duyet-2.html` (SendUserFile, render) cùng `frames/soi-hinh.png`.
- Tóm tắt: độ dài video, số cảnh, 3 tiêu đề, cảnh báo còn lại. **Dừng.** Không tự chọn phương án.

## 7. shorts (sau khi đăng video dài, buổi tối)
- Gọi skill `yt-shorts` với `kich-ban.md` + `giong-timing.json`: chọn 2–3 đoạn trọn ý, 20–55 s, mỗi đoạn trùng ranh giới cảnh.
- Mỗi đoạn k: `dung.compose('V', w=1080, h=1920, scene_range=(i, j), out=f'short-{k}')`
  rồi `scripts/render.sh V/short-k V/shorts/k.mp4 delivery`.
- Giờ đăng Short: sáng ngày hôm sau video dài (đề xuất 08:00 giờ Việt Nam).
- Shorts không nằm trên đường găng: dựng sau khi `dang` xong (máy rảnh buổi tối), giờ đăng Short là sáng hôm sau. Dựng xong thì thêm từng mục vào `dong-goi.json:shorts` (`file`, `tieu_de`, `ngay`, `gio`) rồi đăng bằng `/video-dang` (`tttc.dang short`). `dong-goi.json:shorts` có thể rỗng khi duyệt 2.
- `set_step(V, "shorts", "xong")` sau khi tất cả Short đã dựng.
