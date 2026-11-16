---
name: video-dung
description: Chặng 2 của pipeline video của kênh – giọng VieNeu, chia cảnh, hình minh họa, render HyperFrames, Shorts, đóng gói tiêu đề/thumbnail/mô tả, rồi dừng ở điểm duyệt 2. Dùng khi người dùng gõ /video-dung, "dựng video", hoặc nói "duyệt phương án N" cho video đang chờ duyệt 2.
---

# /video-dung [thư mục video]

Spec mục 4. Chạy Python trong `pipeline/` bằng `uv run`. V = `../videos/<slug>`.
Mỗi bước: ghi `set_step(V, <bước>, "dang-chay")` trước khi làm, rồi `set_step(V, <bước>, "xong")` khi hoàn thành.
Lỗi thì ghi `set_step(V, <bước>, "loi", "<lý do>")`, dừng và báo. Ghi giờ bắt đầu duyệt 2 trước khi chuẩn bị trang.

**Tiết kiệm token** (luật chung ở skill `video-moi`, mục "Tiết kiệm token"):
- Chặng này chạy trong **phiên mới** (không mang lịch sử chặng 1). Shorts (mục 7) chạy buổi tối trong **một phiên mới nữa**.
  Phiên đang có lịch sử việc khác thì nhắc người dùng `/clear` trước.
- Tìm b-roll trên Pexels/Pixabay (mục 2 `b-roll` bước 3–5) và chụp trang nguồn bằng trình duyệt: giao subagent
  `model: "sonnet"` với danh sách cảnh + luật lọc clip; nó tải, soi, nhập kho rồi chỉ trả bảng `cảnh | tệp | ghi_cong`.
- Kiểm cảnh gộp: `uv run python -m tttc.gop kiem-canh V` (canh + chat_luong, chỉ in Lỗi + 8 cảnh báo đầu, bỏ bảng số đo;
  `--day-du` khi cần bảng). Render gộp: `uv run python -m tttc.gop render V` (chạy nền).
- Mở `V/canh.json` theo cảnh cần sửa (Grep `"id": "c0NN"`), đừng đọc lại cả tệp sau mỗi lần sửa.

## 0. Điều kiện
- `trang_thai.review_current(V, "duyet-1")` phải đạt. Nếu cần, chạy /video-moi và gửi duyệt lại.
- Khi người dùng duyệt phương án N của bản đã gửi, chạy `uv run python -m tttc.trang_thai duyet V duyet-2 N`.
  Nếu tệp thay đổi thì gửi duyệt lại. Trong đợt chạy khô, dừng ở duyệt 2.
- Người dùng ghi chỗ cần sửa ở duyệt 2: sửa đúng bước liên quan (cảnh → bước 2–4, tiêu đề → bước 5), chạy lại từ đó.
- Đọc `next_step(V)`, bắt đầu từ bước chưa xong.

## 1. giong
**Giọng VieNeu-TTS chạy trong máy** (cần `~/Documents/VieNeu-TTS` đã cài):

    uv run python -m tttc.giong_vieneu nghe-thu <thư mục> "Hải Đăng" "Thiện Minh"   # nghe thử giọng, một lần
    uv run python -m tttc.giong_vieneu V                                              # tạo giong.mp3 + giong-timing.json

Khi người dùng chọn ElevenLabs, dùng `uv run python -m tttc.tts V` với khóa trong Keychain.

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
5. **`minh-hoa` phải chỉ ra một quan hệ** (user duyệt 12/11/2026): ai trả cho ai, cái gì lớn hơn cái gì, cái gì dẫn tới cái gì.
   Nếu `y` của cảnh chỉ là "cho thấy vật mà lời đọc nhắc" (kính lúp khi nói "xem kỹ", điện thoại khi nói "ứng dụng") thì đó là cảnh khô:
   đổi sang `so-lon`, `trich-bao`, `trang-nguon` hoặc `b-roll` có `tu_khoa`.

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
- Đầu mỗi beat của kịch bản là một cảnh `chuong`, trừ beat móc câu: không thẻ chương hay `mo-dau` trước giây 45 (`tttc.canh` cảnh báo).
- Nhãn `minh-hoa` ≤ 5 từ; nhãn là ý chính, không lặp nguyên lời đọc.
- **Chuyển động lặp** `dong` (mọi cảnh `minh-hoa` mặc định `bob`): `xoay` cho đồng xu/vòng quay, `dap` cho vật đang hoạt động
  (máy chủ, chip), `chop` cho điểm nhấn vàng; `""` để đứng yên. Đạo cụ tự nhấp nhô lệch pha.
- Cho sân khấu có chuyện xảy ra: `minh-hoa` thêm `phu` (1–2 đạo cụ: cay, dong-xu, container, nguoi, mui-ten-len/xuong…);
  `so-lon` thêm `huong` khi số tăng/giảm và `svg` hình nền hợp nghĩa; `bieu-do` thêm `chu_thich` ≤ 2 từ cho cột nổi bật.
- Nền tự gán theo vai trò (user duyệt 12/11/2026): `chuong` vàng; bằng chứng (`trich-bao`, `trang-nguon`, `nhan-vat`) kem; số liệu, minh họa, b-roll tối.
  **Tông theo chương** (14/11/2026): ghi `tong` ở cảnh đầu video và ở mỗi cảnh `chuong` để nền tối của các cảnh sau đổi theo vai trò:
  `hook` navy tối (móc câu), `khai-niem` kem ấm (khái niệm, bảng, checklist), `ky-thuat` rêu tối (cơ chế kỹ thuật),
  `viet-nam` ngọc nhạt (tác động Việt Nam, chuỗi cung ứng). Bằng chứng vẫn kem, chương vẫn vàng.
- **Phụ đề cháy vào hình đã tắt cho video ngang** (đối thủ không dùng; đáy khung dành cho bằng chứng và nhãn). Phụ đề vẫn lên
  YouTube qua `phu-de.srt`; Shorts vẫn có phụ đề to. Bật lại: `config.json:render.phu_de = true`.
- **`boi` – bồi dần trên cùng một sân khấu** (mọi mẫu, ≤ 6 mỗi cảnh): `[{chu?, svg?, kieu?, x, y, tu?, mui_ten?}]`. Nhãn pill bật đúng
  lúc lời đọc nói `tu` (≤ 5 từ; `kieu`: `nhan` màu kênh, `vang` điểm chốt, `do` sự cố/cảnh báo, `trang` tên thực thể – thường kèm
  `mui_ten` trai|phai|len|xuong chỉ vào vật). Chỉ `svg` không `chu` = tem/thẻ hình bật lên. `x`, `y` 0–1 là tâm nhãn trên khung;
  tránh dải đáy (y > 0,85) và góc Nhịp. Cảnh sân khấu giữ lâu sau giây 60 cần `boi` + `nhip` đủ ~1 sự kiện mỗi 2–3 s
  (`chat_luong` đếm). Số trong `chu` cần `nguon_id` của cảnh.
- **`tom_tat`** (mọi mẫu, ≤ 14 từ): thanh tóm tắt một dòng ở đáy. Dùng cho mọi cảnh bằng chứng: câu tiếng Việt nói con số/ý
  của ảnh, hoặc bản dịch dòng được khoanh ở `trang-nguon`. Số cần `nguon_id`.
  Người xem nhận ra "đang xem bằng chứng" qua màu nền; chỉ ghi `nen` khi muốn phá nhịp có chủ đích. Chuyển cảnh tự gán.
- **Giây đầu có chữ hoặc số** (`tttc.chat_luong` cảnh báo): cảnh đầu là `so-lon`/`so-sanh`/`trich-bao`/`trang-nguon`/`bieu-do`,
  hoặc `b-roll` có `tu_khoa`/`chia`. Đưa con số hay câu hỏi chính lên khung đầu, đừng mở bằng cảnh stock trống.
- **`b-roll` không để trống** (gần nửa video là b-roll): thêm `tu_khoa` (≤ 5 từ, ý chính của câu, hiện to giữa khung đúng lúc nói
  `nhip[1]`, tự tắt sau 1,8 s) cho khoảng một nửa số cảnh b-roll; hoặc `chia: {so, truoc?, sau?, nhan}` (video lùi sang nửa trái, số hiện
  nửa phải lúc `nhip[2]`) khi lời đọc vừa kể chuyện vừa nêu số. `nhip[0]` vẫn là mốc của `nhan`; để `null` các mốc không dùng.
  Có số trong `tu_khoa` hay `chia` thì bắt buộc `nguon_id`, `tttc.canh` đối chiếu với nguồn như mọi số khác.
- **`so-sanh` có số ở cả hai bên cùng đơn vị** thì tự vẽ hai cột cao đúng tỉ lệ thay cho biểu tượng: chọn mẫu này khi chênh lệch là ý chính.
- **Tự thêm, không cần ghi:** thanh tiến trình chương ở mép trên (tên chương đang xem ở góc phải), và Nhịp ló ra 1,8 s ở cảnh `so-lon`
  có `trong_diem` (`dao_dien` chép sang `canh.json`). Muốn Nhịp chỉ ló ra một lúc ở cảnh khác: `dan.lau` = số giây (0,8–6).
- **Nhịp con**: mỗi cảnh ghi `nhip` = các cụm từ giọng đọc nói trong cảnh, theo thứ tự bước của mẫu
  (`DEFAULT_STEPS` trong `tttc/dung.py`; `bieu-do` = một cụm cho mỗi cột + một cụm cho cột nổi bật).
  Mục tiêu: hình đổi khoảng 2 s một lần. `tttc.canh` báo lỗi nếu cụm không có trong lời đọc của cảnh.
- **Tỉ lệ cảnh** (user chốt 14/11/2026 theo `docs/nghien-cuu/cach-doi-thu-dung-video-2026-11-14.md` mục 6, thay chuẩn
  10/11; `tttc.chat_luong` đo): **đồ họa sa bàn là chính**, ảnh thật chỉ khi đúng sự kiện.
  Đồ họa tự dựng (`so-lon`, `phan-tram`, `bieu-do`, `so-sanh`, `quy-trinh`, `thoi-gian`, `minh-hoa`, `chu-dong`, `chuong`…) ≥ 70%;
  bằng chứng (`trich-bao`, `trang-nguon`) 8–35%; 1–3 ảnh/clip thật **đúng sự kiện** (ảnh báo, ảnh hãng, ghi nguồn + ngày);
  b-roll kho chung Pexels/Pixabay ≤ 10%. Thiếu hình thật thì dùng đồ họa, **không lấp bằng stock** (clip tối, lệch ngữ cảnh).
  Không 3 cảnh liền cùng mẫu (trừ `b-roll`, miễn là clip khác nhau).
- **Nhịp hai tốc độ**: 30 s đầu cắt nhanh (trung bình ≤ 3,5 s/cảnh). Sau giây 60 được giữ một sân khấu đồ họa
  (`quy-trinh`, `ban-do`, `xep-hang`, `bieu-do`, `thoi-gian`, `minh-hoa` nhiều nhịp) tới 35 s, miễn bồi dần ≥ 20 sự kiện/phút
  trên chính cảnh đó (mỗi bước/nhãn mới ~2–3 s); dưới mức đó `chat_luong` tính là cảnh chậm.
- **Nguồn hình** (user chốt 11/11/2026: không cần kiểm giấy phép, chỉ ghi tên nguồn trên hình). Hình phải cho thấy
  **đúng thứ lời đọc đang nhắc**, không phải cảnh chung chung. Với mỗi cảnh, thử theo thứ tự:
  1. Lời đọc dẫn một nguồn (bài báo, nghị định, công văn, báo cáo, trang giá, biểu đồ gốc, gợi ý tìm kiếm Google,
     bản lưu Wayback để so trước–sau, bình luận dưới video của kênh, Google Maps) → `trang-nguon` chụp bằng `tttc.chup`.
  2. Có ảnh thật của đúng sự việc (ảnh trong bài báo nguồn, ảnh hãng, ảnh tìm trên mạng, ảnh user tự chụp, ảnh chụp
     tay bài đăng mạng xã hội) → tải về rồi `broll.nhap(<tệp ảnh>, V, ghi_cong="Ảnh: <tên báo/hãng>", do_dai=...)`.
  3. Có clip thật (keynote, bản tin, clip phản ứng, clip user tự quay, quay màn hình app) → `uv run yt-dlp
     --download-sections "*<bắt đầu>-<kết thúc>" -o <tệp> <url>` rồi `broll.nhap(<tệp>, V, ghi_cong="Video: <kênh>",
     do_dai=...)`. Mỗi đoạn ≤ 5 s (tránh Content ID); `nhap` đã bỏ tiếng gốc.
  4. Tình huống không có hình thật → ảnh AI sinh, `ghi_cong="Minh họa"`; không dùng làm bằng chứng.
  5. Sau cùng mới tới kho b-roll chung và đồ họa tự dựng.
  Tệp user thả vào `V/tu-quay/` dùng trước mọi nguồn khác. Quay màn hình app: user tự che số tài khoản, số dư trước.
- **Nhân vật dẫn chuyện "Nhịp"** (mọi mẫu): `dan: {the, goc?: phai|trai, huong?, tu?: "cụm lời đọc"}`; `the` ∈ chao, ngac-nhien, nghi, xac-nhan, bo-ngo, tinh-toan; `huong` ∈ truoc, nghieng-trai, nghieng-phai (mặc định nghiêng về giữa màn hình theo `goc`). Bộ ảnh lấy từ `pipeline/nhan-vat/kit.json` (bắt buộc; `tttc.canh` báo Lỗi nếu cặp biểu cảm × hướng không có). Hiện ở góc dưới, bật vào đúng lúc nói `tu` (không có `tu` thì 0,3 s sau đầu cảnh), nhấp nhô; chỉ góc `truoc` có chớp mắt. Dùng ≥ 1 lần mỗi chương và ở các khoảnh khắc: `chao` khi mở chương, `ngac-nhien` trước số gây sốc, `nghi` khi đặt câu hỏi hay nguồn lạ, `xac-nhan` khi số khớp nguồn, `bo-ngo` khi nói chưa kiểm được, `tinh-toan` khi mình tự tính. Không dùng trong Shorts (khung dọc). Chọn `goc` phía không có chữ/số quan trọng. Chỉ cho Nhịp ra khi có lời nói với người xem, câu hỏi `>>` của giọng phụ, hay đoạn tóm ý; không đứng chơi cạnh bằng chứng. Tạo lại bộ nhân vật: `docs/nghien-cuu/nhan-vat-tobyflow.md`.
- **`quy-trinh`** (một chuỗi 3–6 bước nối bằng mũi tên: quy trình, chuỗi cung ứng, "tiền đi đâu"): `buoc` = danh sách
  `{nhan, svg?}` (không có `svg` thì hiện số thứ tự), `noi_bat` = chỉ số bước đang nói tới (bước còn lại mờ đi), `nhip` = một
  cụm lời đọc cho mỗi bước.
- **`so-lon` đếm từ giá trị cũ:** thêm `tu` (giá trị trước đó, vd giá cũ) thì số đếm từ `tu` lên (hoặc xuống) tới `so`, cho người xem thấy mức thay đổi; `tu` cũng phải khớp `nguon_id` như `so`. Không có `tu` thì đếm từ 0.
- **`xep-hang`** (xếp hạng, thị phần, giá, chi tiêu theo thứ tự lớn → nhỏ): `hang` = 2–8 phần tử `{nhan, so}` theo đúng thứ tự muốn hiện (tự xếp), `don_vi`, `nguon_id` (bắt buộc; mọi `so` phải khớp nguồn như `bieu-do`), `noi_bat` = chỉ số hàng cần nhìn, `nhip` = một cụm lời đọc cho mỗi hàng. Thanh ngang dài theo giá trị, số đếm tăng ở đầu thanh. Dùng khi so nhiều bên cùng một thước đo; hai bên thì dùng `so-sanh`. **Chạy theo năm:** thêm `moc` (2–10 nhãn, vd ["2022","2024","2026"]) và cho mỗi hàng `so` là danh sách một giá trị cho mỗi mốc; các hàng tự đổi chỗ theo hạng ở từng mốc, thanh dài ra/ngắn lại, số đếm tới giá trị mới, số năm lớn mờ ở phía sau; `nhip` = một cụm lời đọc cho mỗi mốc. Mọi giá trị ở mọi mốc phải khớp `nguon_id`. Nhãn là tên bằng tiếng Việt, tên hãng giữ nguyên.
- **`ban-do`** (bản đồ vị trí: hàng hóa đi từ đâu tới đâu, nước nào nằm ở đâu): `diem` = 2–6 phần tử `{nhan, vi_do, kinh_do, nuoc?, noi_bat?}` (toạ độ thủ đô hoặc thành phố chính, độ thập phân; `nuoc` = mã ADM0_A3 như VNM, USA, MYS để tô sáng nước đó), `noi` = mũi tên cong `{tu, den, nhan?}` nối hai điểm theo chỉ số, `nhip` = một cụm lời đọc cho mỗi điểm rồi mỗi mũi tên. Hình nước lấy từ `pipeline/du-lieu/nuoc.json` (Natural Earth, phạm vi công cộng; tạo lại bằng `uv run python -m tttc.ban_do <geojson>`), mẫu tự ghi nguồn dữ liệu. **Chọn điểm gần nhau** (cùng khu vực) để hình nước đủ lớn; hai điểm cách nửa vòng Trái Đất thì nước nhỏ chỉ còn là chấm. **Chưa vẽ đảo nhỏ và quần đảo** (dữ liệu bỏ vòng dưới 0,4 độ²): bản đồ không thể hiện Hoàng Sa, Trường Sa; cảnh nào cần chủ quyền biển đảo thì dùng ảnh chụp tài liệu hoặc đồ họa riêng, không dựa vào mẫu này. Nhãn là tên nước/thành phố bằng tiếng Việt (≤ 5 từ), nhãn mũi tên ngắn; điểm cần nhìn đặt `noi_bat`.
- **`so-sanh`** (hai vật cạnh nhau, "gấp N lần", "sân bóng so với hạt gạo"): `trai` và `phai` = `{nhan, svg, so?, don_vi?, to?}`;
  `to` (0–1) là cỡ hình tương đối, hai hình đứng trên cùng một đường nền; `ti_le` = nhãn "gấp ~700 lần" (nhãn tự tính phải
  có nguồn `tu-tinh`); có `so` thì bắt buộc `nguon_id` và số + đơn vị phải khớp nguồn.
- **`thoi-gian`** (so nhịp nhiều bên theo năm: "Singapore 2 năm, Ấn Độ 4 năm, mình thì sao"): `truc` {tu, den, don_vi},
  `hang` 2–5 phần tử `{nhan, tu, den, noi_bat?}`; năm trên thanh phải có trong `gia_tri` của `nguon_id` (hoặc là nguồn
  `tu-tinh`); một hàng một cụm `nhip`.
- **`chu-dong`** (câu chốt, câu hỏi xoáy, kết luận của chương; tối đa 1–2 lần mỗi chương): `cau` ≤ 16 từ, nên chép đúng lời đọc để từng chữ hiện đúng lúc giọng nói tới; `nhan_tu` = cụm trong `cau` được tô màu nhấn và gạch dạ quang; `nho` = dòng nhỏ phía trên (≤ 5 từ, vd "Câu hỏi", "Điểm mấu chốt"). Không dùng thay phụ đề cho câu thường.
- **`phan-tram`** (tỉ lệ, "một phần tư", "7 trên 10 người"): `so` 0–100, `nhan` = ý nghĩa con số, `tieu_de?`, `nguon_id` bắt buộc (khớp nguồn như `so-lon`; tỉ lệ tự tính dùng nguồn `tu-tinh`). Vòng tròn chạy tới đúng tỉ lệ, số đếm cùng nhịp.
- **`mo-dau`** (logo kênh, 2–3 s): đặt sau đoạn móc câu, **từ giây 45 trở đi** (không chen vào 30 s đầu), `cau?` = câu hỏi của video. Một lần mỗi video.
- **`ket-thuc`** (màn hình kết thúc): luôn là cảnh cuối, dài ≥ 5 s (lý tưởng 8–10 s), lời đọc là lời chào/kêu gọi đăng ký. `cau?`, `moi?`, `nut?`, `nut_xong?`, `khung?`. Khi đăng, đặt 2 phần tử video gợi ý của YouTube Studio đúng vào hai khung bên phải.
- **Chuyển cảnh tự gán**: vào chương ba lớp màu nhấn quét qua, rời chương ba lớp tối, vào `so-lon`/`phan-tram`/`mo-dau`/`ket-thuc` mống mắt khép–mở, còn lại chớp tối hoặc cắt thẳng. Viền tối điện ảnh quanh khung: `config.json:render.vien_toi` (mặc định 0,28; 0 = tắt).
- **`trich-bao`**: `trich` chép nguyên văn từ `nguon.json:trich_dan` (≤ 25 từ), `to_vang` là cụm chứa ý/số chính.
  Khi 2–3 nguồn cùng nói về một việc (đối chiếu, "ai nói gì"): dùng `cac: [{nguon_id, tom_tat}]` thay cho `trich` – các thẻ
  song song, mỗi thẻ huy hiệu chữ cái + tên báo + ngày + tóm tắt ≤ 6 từ; `nhip` một cụm cho mỗi thẻ. Đừng lặp 5–6 tờ giấy kem đơn.
- **`trang-nguon`**: `vien` (`nhan`|`vang`|`do`) đổi màu viền khoanh; `zoom` 2,5–3,5 khi muốn phóng sát đúng dòng/con số
  (mặc định tự tính); kèm `tom_tat` là bản dịch/tóm tắt tiếng Việt in đậm ở đáy.
  Không chụp nguyên trang báo; mẫu tự sắp chữ lại kèm tên báo (`nguon.ten`) và ngày.
- **`b-roll`** – clip riêng cho từng video (kho chung chỉ là phần nền):
  1. Liệt kê mọi cảnh `b-roll` của video và hình cần thấy (vd "cánh quạt điện gió", "chợ Bến Thành").
  2. Tìm trong `pipeline/broll-kho/kho.json` theo `tu_khoa`/`mo_ta`, độ dài ≥ cảnh + 1 s. Có clip hợp và chưa
     dùng trong video này thì dùng. **B-roll thuần Việt Nam:** cảnh có người, phố, nhà, quán, chợ, xe, tiền, phong cảnh
     chỉ nhận clip `boi_canh: "vn"`; clip `trung-tinh`/`chua-ro` chỉ cho cận vật, màn hình, bàn tay; clip `ngoai` chỉ
     khi lời đọc nói đúng nước `nuoc`. Bảng nhãn và nguồn tìm clip Việt Nam: `pipeline/broll-kho/README.md`.
  3. Không có: mở trình duyệt có sẵn ở `https://www.pexels.com/`, dán `pipeline/scripts/pexels-tim.js` vào
     `javascript_tool`, gọi `await pxl("<từ khoá tiếng Anh cụ thể>", 4)`. Cảnh cần bối cảnh Việt Nam: thêm "Vietnam"/
     "Hanoi"/"Saigon" vào từ khoá; hết thì tìm Pixabay rồi Wikimedia Commons. Chọn 1–2 ứng viên hợp nhất.
  4. `broll.tai_ve(link, "<chu-de>-<id>", broll.KHO, f"Video: {user} trên Pexels", nguon=page,
     mo_ta="<mô tả tiếng Việt>", tu_khoa=[...Việt + Anh...], boi_canh="vn"|"trung-tinh"|"ngoai"|"chua-ro")` – chỉ nhận videos.pexels.com / cdn.pixabay.com /
     upload.wikimedia.org.
  5. `broll.soi(clip, V/frames/broll-<ten>.jpg)` rồi **xem ảnh**: có mặt người nhận ra được, logo hãng, chữ nước
     ngoài lớn, tiền nước khác khi nói về tiền Việt → xoá clip khỏi kho (tệp + mục kho.json), tìm clip khác.
  6. `broll.nhap(KHO / tep, V, ghi_cong=<từ kho.json>, bat_dau=<giây>, do_dai=<độ dài cảnh + 0,5>)`; ghi
     `video` = tên tệp trả về. Một clip dùng cho một cảnh mỗi video.
  Không tìm được clip đạt sau 2 lượt từ khoá: đổi cảnh đó sang `minh-hoa` hoặc `so-lon`, không dùng clip kém.
  Có khoá Pexels trong Keychain thì `broll.search`/`pick`/`download` thay cho bước 3–4.
- Ảnh trang nguồn: `uv run python -m tttc.chup <url> V/nguon/<id>.png "<câu trích nguyên văn, ngắn>"` – lệnh in ra
  `khung` (x,y,w,h theo % ảnh) quanh câu đó, ghi vào cảnh. Báo "không thấy câu trích" thì rút câu ngắn lại (câu vắt
  qua chữ đậm/đường dẫn không khớp). Trang đòi đăng nhập (mạng xã hội): nhờ user chụp tay vào `V/tu-quay/`.
  Xem lại ảnh trước khi dùng: còn banner che chữ thì chụp lại bằng trình duyệt có sẵn.

## 3. hinh
- Cảnh `minh-hoa` cần hình chưa có trong `pipeline/svg/`: thêm hàm vào `pipeline/svg/ve.py` theo `svg/README.md`,
  chạy `uv run python svg/ve.py`. Không vẽ chữ, không logo.
- Cảnh `nhan-vat`: `tttc.anh.search("<tên người>")` → `pick()` → `download(item, V)`; ghi `anh` = tên tệp trả về.
  `pick` trả None thì đổi cảnh đó sang `minh-hoa`.
- `uv run python -m tttc.gop kiem-canh V` (chạy `tttc.canh` rồi `tttc.chat_luong`) tới khi cả hai `0 lỗi`
  (cảnh báo độ dài 2,5–6 s được phép khi có lý do). Gom nhiều chỗ sửa rồi mới chạy lại.
- Với `chat_luong`: tới khi **0 Lỗi**; đọc từng Cảnh báo (nhịp, tỉ lệ mẫu, sự kiện hình và hiệu ứng
  âm thanh mỗi phút, tốc độ đọc) và sửa hoặc ghi lý do giữ. Chỉ sang bước render khi đạt (render tốn cả chục phút).

## 4. render
`uv run python -m tttc.gop render V` (chạy nền) làm liền bốn việc dưới đây và dừng ngay nếu `kiem-canh` còn Lỗi; khi
xong in đường dẫn `soi-hinh.png` và kết quả `check_av`. Cần chạy lẻ từng việc thì dùng lệnh gốc:
1. `uv run python -c "from tttc import dung; dung.compose('V')"`
2. `scripts/render.sh V/composition V/final.mp4 delivery` (đo 09/11/2026 trên máy i9 16 luồng: delivery ≈ 2× thời lượng, khoảng 25 phút cho video 12 phút; chạy nền; xem docs/nghien-cuu/do-render-2026-11-09.md).
3. `dung.contact_sheet('V/final.mp4', canh, 'V/frames/soi-hinh.png')` – **xem ảnh này**: chữ tràn, hình chồng,
   cảnh trống, số sai. Sửa `canh.json`/mẫu, render lại.
4. `dung.check_av('V/final.mp4', 'V/giong.mp3')` phải rỗng.

## 5. dong-goi
1. Gọi skill `yt-package`: 3 cặp tiêu đề (≤ 100 ký tự, ưu tiên ≤ 60) + chữ thumbnail theo ba tầng `nhan`/`so`/`hoi` của bước 2.
   Tiêu đề theo luật `tttc.tieu_de` (xem skill `video-moi` bước kiểm tiêu đề): dạng `[sự kiện + số]: [một câu hỏi]?`, không giật gân,
   không "!", không nhãn in hoa mở đầu. Phương án nào `tieu_de.kiem` còn lỗi thì viết lại trước khi dựng thumbnail, không đưa lên duyệt 2.
2. Thumbnail – **hai khuôn đã khóa cho Test & Compare: `ban-co-toi` và `ho-so`** (người dùng chốt 16/11/2026; `docs/superpowers/specs/2026-11-16-dinh-huong-cluster-a-va-vong-hoc-design.md` mục 5.1).
   Trong bộ 3 phương án của mỗi video dài, xuất cả `tttc.thumb.ban_co_toi(anh, nhan, so, hoi, V/thumbnails/N.png, ghi_cong, tam=(x, y), zoom=...)` và `tttc.thumb.ho_so(anh, nhan, so, hoi, V/thumbnails/N.png, ghi_cong, tam=(x, y), zoom=...)` để chạy Test & Compare trực tiếp trên YouTube Studio. Không dùng `thumb.make`, `thumb.khung`, CoDesign hay nền TobyFlow cho video dài nữa.
   - `nhan`: chủ thể + động từ xung đột, ≤ 3 từ ("NVIDIA BỐC HƠI", "META BỊ PHẠT"); có thể để `""`.
   - `so`: con số làm chính, lấy từ `nguon.json` và khớp số trong tiêu đề ("-190 TỶ USD", "805 TRIỆU EURO").
   - `hoi`: **một** câu hỏi ≤ 3 từ ("MỸ RA TRÁT?", "VIỆT NAM PHẠT?"); dài hơn thì chữ nhỏ, không đọc được trên điện thoại.
   - `anh`: ảnh thật của nhân vật/sự kiện (Wikimedia Commons, ảnh báo/hãng có ghi công) hoặc khung đẹp nhất của video
     (`thumb.khung_tu_video(V/final.mp4, t, V/thumbnails/khung.png, bo_day=0.12)`). Dùng `tam=(x, y)` và `zoom` (vd `zoom=1.8–2.5` cho ảnh có mặt người) để gương mặt nhân vật luôn rõ ở cỡ 168×94 px.
     **Không** dùng mặt người do AI tạo trông như ảnh thật, không logo hãng làm ảnh chính.
   - `ghi_cong` = `anh/ghi-cong.json:ghi_cong` nếu ảnh có ghi công.
   - Cách chia 3 phương án: PA 1 dùng `ban-co-toi`, PA 2 dùng `ho-so` (giữ cùng chữ để đo Nền tối vs Nền kem), PA 3 đổi góc chữ/ảnh.
   - Mở bản `-168px` của từng thumbnail: đọc không ra chữ thì sửa.
3. Gọi skill `yt-chapters` với mốc từ `giong-timing.json:paragraphs` (mốc thật, không ước tính).
4. Gọi skill `yt-seo` cho mô tả + tags. Mô tả kết thúc bằng:
   - "📎 Nguồn" – mỗi mục `nguon.json`: giá trị, URL, ngày truy cập.
   - "🖼 Ghi công ảnh" – mỗi dòng `anh/ghi-cong.json:ghi_cong`.
   - Không có ký tự `<` `>` (YouTube từ chối).
5. Ghi `V/dong-goi.json` (đọc bởi `tttc.dang`):
   `{"phuong_an":[{"tieu_de","chu_thumb":[nhan, so, hoi],"file_thumb":"thumbnails/N.png","khuon":"ho-so"}×3], "mo_ta", "tags":[...],
     "shorts":[{"file":"shorts/k.mp4","tieu_de":"... #shorts","ngay":"dd/mm/yyyy","gio":"HH:MM"}]}`
   và `V/dong-goi.md` bản dễ đọc của cùng nội dung.

## 6. duyet-2
- `uv run python -c "from tttc.duyet import render_review_2; print(render_review_2('V'))"`
- `uv run python -m tttc.trang_thai gui-duyet V duyet-2` ngay sau khi tạo trang, trước khi gửi `duyet-2.html` và `frames/soi-hinh.png`.
- Tóm tắt: độ dài video, số cảnh, 3 tiêu đề, cảnh báo còn lại. **Dừng.** Không tự chọn phương án.
- Khi người dùng duyệt phương án xong, nhắc: đăng (`/video-dang`) và Shorts (mục 7) mỗi việc một phiên mới (`/clear` trước).

## 7. shorts dọc gốc (sau khi đăng video dài, buổi tối)
Thiết kế: `docs/superpowers/specs/2026-11-15-shorts-doc-goc-design.md`. Mỗi Short là một video riêng: kịch bản riêng,
giọng đọc mới, hình dựng bằng mẫu dọc 1080×1920 (`templates/canh-doc/`). **Không** cắt đoạn từ video dài nữa
(`scene_range` + `short_hook` chỉ còn để dựng lại Short cũ). Lý do: Short cắt từ giữa bài và thu nhỏ sân khấu ngang chỉ giữ
9,6–18,9% người lướt tới.

- **Chọn góc:** 2 Short mỗi video, mỗi Short một góc tự đứng được (người chưa xem video dài vẫn hiểu), có ít nhất một con số
  có nguồn trong `V/nguon.json`. Ưu tiên đề tiêu dùng có giá cụ thể.
- **Kịch bản** `V/ngan/k/kich-ban.md` (dòng đầu `Loại: shorts`, mục 7 của `docs/template-kich-ban.md`, 35–50 giây):
  câu nói đầu tiên là câu hook có con số gắn `[#id]`; kết bằng câu nối lại câu đầu để xem lặp (không kêu bấm video liên kết);
  không dùng giọng phụ `>>`. Kiểm, sửa hết dòng `Lỗi`:
  `phong_cach.kiem_short(kich_ban)` + `kiem.check(kich_ban, nguon của V)`.
- **Giọng:** `giong_vieneu.synthesize('V/ngan/k', giong_vieneu.cfg_shorts())` (nghỉ 0,10 s).
- **Cảnh** `V/ngan/k/canh.json` = `{"khuon": "doc", "scenes": [...]}`, cảnh đầu luôn là `moc` bắt đầu ở 0 có `chu` (≤ 8 từ)
  và `so`. Năm mẫu dọc:
  - `moc`: `chu`, `so` (chuỗi hiển thị, ≤ 12 ký tự), `nhan?`, `nguon_id` khi có số.
  - `bang-chung`: `anh` (đường dẫn trong `anh/`, `nguon/` hoặc `broll/` của V, vd `nguon/x.png`; chỗ khác không được chép khi dựng), `vung` = `[x, y, w, h]` trong 0–1 cắt đúng dòng/con số,
    `tom_tat` (một dòng tiếng Việt), `nguon_id`. Không chiếu nguyên trang.
  - `anh`: đúng một trong `anh` (đường dẫn như `bang-chung`, vd `anh/x.jpg`) / `video` (chỉ tên tệp trong `V/broll/`), `diem_giu` = `[x, y]` trong 0–1 (chỗ giữ khi cắt dọc), `nhan?`.
  - `doi-chieu`: `tren`, `duoi` = `{"nhan", "so"}`, `noi_bat` = `tren`/`duoi`, `nguon_id`.
  - `ket`: `chu`, `so?`.
  Cảnh ≤ 6 s, trung bình ≤ 3,5 s. Kiểm: `canh.validate(canh, timing, nguon=nguon của V, video_dir='V/ngan/k', goc='V')`.
- **Dựng:** `dung.compose('V/ngan/k', goc='V')` → `scripts/render.sh V/ngan/k/composition V/shorts/k.mp4 delivery`
  → `chat_luong.kiem_short(canh, timing, 'V/shorts/k.mp4')` (sửa hết `Lỗi`) → `dung.trich_khung('V/shorts/k.mp4', 'V/ngan/k')`.
- **Tiêu đề Short:** chấm bằng `tieu_de.kiem` và `tieu_de.kiem_khop_nguon` như video dài (không giật gân, không "!").
- **Đóng gói:** thêm vào `dong-goi.json:shorts` `{"file": "shorts/k.mp4", "tieu_de", "ngay", "gio", "khuon": "doc", "mo_ta"?}`
  (`mo_ta` riêng nếu có, không thì dùng mô tả video dài; dòng trỏ về video dài tự thêm lúc đăng).
- Giờ đăng Short: sáng ngày hôm sau video dài (đề xuất 08:00 giờ Việt Nam). Shorts không nằm trên đường găng: dựng sau khi
  `dang` xong (máy rảnh buổi tối).
- **Gửi người dùng** từng Short: tệp mp4, `khung-0.png`, `khung-3.png`, tiêu đề, giờ đăng, cảnh báo còn lại. **Dừng.**
  Khi người dùng nói "ok" với Short i: `uv run python -m tttc.trang_thai duyet-short ../videos/<slug> <i>` (ghi sha256 tệp +
  mọi trường của mục Short; đổi bất cứ thứ gì sau đó, kể cả `mo_ta`, là phải duyệt lại). Sau đó đăng bằng `/video-dang`
  (`tttc.dang short`). `dong-goi.json:shorts` có thể rỗng khi duyệt 2.
- **Đo:** nhắc người dùng nhập tỉ lệ "ở lại xem" từ Studio vào cột `o_lai_short` của `theo-doi.csv` sau 48 giờ (cột
  `khuon_short` do `dang` tự ghi). Mỗi lứa chỉ đổi một biến; lứa đầu 6 Short chỉ đổi cách dựng, giữ loại đề tiêu dùng có giá
  cụ thể. Sau 6 Short dọc gốc mà trung vị `o_lai_short` dưới 25% thì dừng thêm mẫu cảnh, xem lại câu hook và chọn đề.
- `set_step(V, "shorts", "xong")` sau khi tất cả Short đã dựng.
