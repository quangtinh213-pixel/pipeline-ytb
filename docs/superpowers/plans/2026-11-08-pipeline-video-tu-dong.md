# Pipeline video tự động – Kế hoạch triển khai

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ba lệnh Claude Code (`/video-moi`, `/video-dung`, `/video-dang`) đưa một chủ đề thành video + Shorts đã hẹn giờ trên YouTube, với 2 điểm duyệt của người.

**Architecture:** Mỗi video là một thư mục `videos/<slug>/` có `trang-thai.json` làm sổ trạng thái. Phần sáng tạo/kiểm tra do Claude làm theo SKILL.md; script Python (chạy bằng `uv`) chỉ lo việc máy móc: kiểm nguồn, gọi ElevenLabs, dựng/render HyperFrames, thumbnail, upload YouTube.

**Tech Stack:** Python ≥3.11 qua `uv` (pytest, requests, pillow, keyring, google-api-python-client, google-auth-oauthlib), HyperFrames CLI (`npx hyperframes`), ffmpeg/ffprobe 9, ElevenLabs API, YouTube Data API v3, Wikimedia Commons API, TobyFlow MCP (chỉ cho thumbnail).

**Spec:** `docs/superpowers/specs/2026-11-08-pipeline-video-tu-dong-design.md`

## Global Constraints

- Brand: nền `#111111`, vàng `#FFC800`, trắng `#FFFFFF`, font `/System/Library/Fonts/SFNS.ttf` biến thể Heavy.
- Video dài 1920×1080 30fps; Shorts 1080×1920; thumbnail 1280×720 + bản thử 168 px rộng.
- Cảnh 4–8 giây, 80–120 cảnh/video 11 phút; độ dài hình = độ dài tiếng ±0,5 s.
- Trạng thái bước: `chua-chay | xong | loi | cho-duyet | da-duyet`.
- Trạng thái nguồn: `xac-minh | so-bo | chua-xac-minh`. Số `so-bo` phải có câu cảnh báo; số `chua-xac-minh` không được vào kịch bản đã duyệt.
- Ảnh nhân vật chỉ từ Wikimedia Commons, giấy phép PD / CC0 / CC BY / CC BY-SA.
- Khóa API (ElevenLabs, YouTube OAuth) lưu bằng `keyring` service `tui-tien-cong-nghe`; không ghi vào file trong dự án.
- Không có đường nào upload được video thiếu một trong hai điểm duyệt.
- Văn bản tiếng Việt chuẩn hoá Unicode NFC trước khi so khớp hoặc gửi TTS.
- Thumbnail TobyFlow: AI chỉ tạo ảnh nền, không chữ, không mặt người thật, không logo hãng; chữ chồng bằng code.

## Review Focus

1. **Chạy lại không tính tiền hai lần** – gọi `/video-dung` lần hai sau khi TTS đã xong thì không gọi ElevenLabs nữa. Test: `test_tts_skips_done_paragraphs` (Task 3).
2. **Giờ hẹn đăng theo giờ Việt Nam** – "13/11/2026 19:00" phải thành `2026-11-13T12:00:00Z`. Test: `test_publish_at_converts_vn_time` (Task 10).
3. **Dấu tiếng Việt dạng NFD** (copy từ web) làm lệch so khớp số/nguồn và timestamp từ. Test: `test_check_handles_nfd_text` (Task 1), `test_words_from_alignment_nfd` (Task 3).
4. **Cảnh hở hoặc chồng nhau** khi chia cảnh tay → phụ đề/hình lệch tiếng. Test: `test_validate_scenes_rejects_gap_and_overlap` (Task 5).
5. **Commons trả ảnh không tự do** (Fair use, "All rights reserved") hoặc thiếu tác giả. Test: `test_pick_rejects_nonfree_license` (Task 6).

---

### Task 1: Khung dự án, sổ trạng thái, kiểm nguồn

**Files:**
- Create: `pipeline/pyproject.toml`, `pipeline/config.json`, `.gitignore`
- Create: `pipeline/tttc/__init__.py`, `pipeline/tttc/trang_thai.py`, `pipeline/tttc/kiem.py`
- Test: `pipeline/tests/test_trang_thai.py`, `pipeline/tests/test_kiem.py`

**Interfaces:**
- Produces:
  - `STEPS = ["chu-de","nguon","kich-ban","kiem","duyet-1","giong","canh","hinh","render","shorts","dong-goi","duyet-2","dang"]`
  - `load(video_dir: Path) -> dict`, `set_step(video_dir, step: str, status: str, note: str = "") -> None`, `next_step(video_dir) -> str | None` (bước đầu tiên chưa `xong`/`da-duyet`; trả `None` khi đang `cho-duyet`), `is_approved(video_dir) -> bool` (cả `duyet-1` và `duyet-2` là `da-duyet`), `set_field(video_dir, key: str, value) -> None` (trường phụ như `chon`, `gio_dang`).
  - `kiem.check(script_md: str, nguon: list[dict]) -> list[str]` – danh sách lỗi tiếng Việt, rỗng là đạt.
  - CLI: `uv run python -m tttc.kiem <video_dir>` in lỗi, exit 1 nếu có lỗi.
- Định dạng `nguon.json`: list `{id, gia_tri, trich_dan, url, ngay_truy_cap, anh_chup, trang_thai}`. Kịch bản gắn nguồn bằng `[#id]` ngay sau câu.

- [ ] **Step 1:** `git init` ở `Youtube/`; `.gitignore` gồm `videos/*/giong*.mp3`, `videos/*/*.mp4`, `videos/*/shorts/`, `videos/*/frames/`, `.venv/`, `.mcp.json`. `pyproject.toml` khai báo package `tttc`, python `>=3.11`, các dependency ở Tech Stack. `config.json` có khoá: `elevenlabs {voice_id, model_id:"eleven_multilingual_v2", speed}`, `nguon_tin [ ... 6 nguồn trong spec ... ]`, `gio_dang_mac_dinh "19:00"`, `nhac_nen`, `playlist_id`.
- [ ] **Step 2: Test trạng thái** – `test_new_video_starts_at_chu_de`, `test_next_step_skips_done`, `test_next_step_none_while_waiting_review` (đặt `duyet-1=cho-duyet` → `None`), `test_is_approved_requires_both`, `test_set_step_rejects_unknown_status`, `test_set_field_persists`.
- [ ] **Step 3:** Chạy `cd pipeline && uv run pytest tests/test_trang_thai.py -v` → FAIL.
- [ ] **Step 4:** Viết `trang_thai.py` (JSON, ghi file nguyên tử qua file tạm + `os.replace`).
- [ ] **Step 5: Test kiểm nguồn** (`test_kiem.py`), mỗi test một lỗi:
  - `test_number_without_source` – `"Giá 522.500 đồng mỗi tháng."` → 1 lỗi chứa `"không có nguồn"`.
  - `test_unknown_source_id` – `[#x9]` không có trong nguồn → lỗi chứa `"x9"`.
  - `test_value_mismatch` – câu có `522.000` gắn `[#p1]` với `gia_tri "522.500"` → lỗi.
  - `test_placeholder_left` – còn `[ĐỔI TỶ GIÁ ...]` → lỗi.
  - `test_so_bo_needs_warning` – nguồn `so-bo` mà câu không có "sơ bộ"/"chưa chính thức" → lỗi.
  - `test_unverified_source_blocked` – nguồn `chua-xac-minh` được dùng → lỗi.
  - `test_number_words_ok` – câu chỉ có số viết chữ và `[#p1]` → không lỗi.
  - `test_check_handles_nfd_text` – kịch bản NFD, nguồn NFC → không lỗi.
- [ ] **Step 6:** FAIL → viết `kiem.py`. Quy ước: "số" là chuỗi khớp `\d[\d.,]*`; bỏ qua ngày dạng `dd/mm/yyyy` và mốc `mm:ss`; câu tách theo `[.!?]\s`.
- [ ] **Step 7:** `uv run pytest -v` → PASS. Chạy `uv run python -m tttc.kiem` trên một bản sao của video 1, cho thấy 3 lỗi giữ chỗ tỷ giá.
- [ ] **Step 8:** Commit `feat: sổ trạng thái và kiểm nguồn`.

### Task 2: Trang duyệt + skill `/video-moi`

**Files:**
- Create: `pipeline/tttc/duyet.py`, `pipeline/templates/duyet.html`
- Create: `.claude/skills/video-moi/SKILL.md`
- Test: `pipeline/tests/test_duyet.py`

**Interfaces:**
- Consumes: `trang_thai.*`, `kiem.check`.
- Produces: `duyet.render_review_1(video_dir) -> Path` (`duyet-1.html`), `duyet.render_review_2(video_dir) -> Path` (`duyet-2.html`, dùng ở Task 9). HTML tĩnh một file, theme brand, có bảng số → nguồn với link `url` và `anh_chup`.

- [ ] **Step 1: Test** – `test_review_1_lists_every_source_id` (mọi `id` trong `nguon.json` đều xuất hiện), `test_review_1_shows_kiem_errors` (lỗi kiểm hiện thành khối cảnh báo), `test_review_1_escapes_html` (trích dẫn có `<script>` bị escape).
- [ ] **Step 2:** FAIL → viết `duyet.py` bằng `string.Template` + `html.escape`. Chạy lại → PASS.
- [ ] **Step 3:** Viết `SKILL.md` cho `/video-moi [chủ đề]`. Các bước theo đúng mục 3 của spec:
  - tạo `videos/<yyyy-mm-dd-slug>/`;
  - chọn đề (đọc `config.json:nguon_tin`, chấm 3 câu, ghi `chu-de.md` gồm 3 đề + điểm);
  - đọc nguồn gốc → `nguon.json` + ảnh chụp trong `nguon/`;
  - gọi skill `yt-script` → `kich-ban.md` có `[#id]`, số trong lời đọc viết thành chữ;
  - chạy `tttc.kiem` cho tới khi sạch, sau đó dispatch một subagent độc lập rà lại kịch bản với nguồn;
  - `render_review_1`, đặt `duyet-1=cho-duyet`, gửi file cho người dùng rồi dừng.
  - Khi người dùng nói "duyệt" thì đặt `da-duyet`.
  - Mỗi bước gọi `set_step`; khi bắt đầu luôn đọc `next_step` trước.
- [ ] **Step 4:** Kiểm thử tay: chạy `/video-moi "so sánh gói AI"` trên thư mục mới, kỳ vọng có `duyet-1.html` và `trang-thai.json` dừng ở `duyet-1=cho-duyet`.
- [ ] **Step 5:** Commit `feat: chặng 1 /video-moi`.

### Task 3: Giọng đọc ElevenLabs

**Files:**
- Create: `pipeline/tttc/tts.py`
- Test: `pipeline/tests/test_tts.py`

**Interfaces:**
- Consumes: `config.json:elevenlabs`, khoá từ `keyring.get_password("tui-tien-cong-nghe","elevenlabs")`.
- Produces:
  - `spoken_paragraphs(script_md: str) -> list[str]` – chỉ lấy dòng **Lời đọc**, bỏ `[#id]`, `[TRÊN MÀN HÌNH]`, markdown; NFC.
  - `words_from_alignment(alignment: dict, offset: float) -> list[dict]` – `{w, start, end}`.
  - `synthesize(video_dir) -> None` – ghi `giong/doan-NNN.mp3` + `.json`, ghép bằng ffmpeg concat thành `giong.mp3`, ghi `giong-timing.json` = `{"duration": float, "words": [...], "paragraphs": [{"i", "start", "end"}]}`.
- API: `POST https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps`, body `{text, model_id, voice_settings:{speed}}`; trả `audio_base64` + `alignment.{characters, character_start_times_seconds, character_end_times_seconds}`.

- [ ] **Step 1: Test** (mock `requests.post`):
  - `test_spoken_paragraphs_strips_markers`
  - `test_words_from_alignment_offsets` (offset 10,0 cộng vào mọi mốc)
  - `test_words_from_alignment_nfd`
  - `test_tts_skips_done_paragraphs` (đã có `doan-001.mp3` + `.json` thì không gọi API cho đoạn 1)
  - `test_tts_retries_only_failed_paragraph` (đoạn 2 lỗi 500 lần đầu → chỉ đoạn 2 gọi lại)
  - `test_timing_duration_matches_audio` (dùng 2 mp3 im lặng 1 s tạo bằng ffmpeg → `duration` ≈ 2,0 ± 0,05)
- [ ] **Step 2:** FAIL → viết `tts.py`. Offset mỗi đoạn lấy bằng `ffprobe` độ dài thật của các đoạn trước, không dùng mốc cuối của alignment. Mỗi đoạn retry tối đa 3 lần với 429/5xx.
- [ ] **Step 3:** PASS. Kiểm thật một lần với khoá thật trên 1 đoạn ngắn, mở `giong.mp3` nghe thử, kiểm `words[-1].end ≤ duration`.
- [ ] **Step 4:** Commit `feat: giọng ElevenLabs có timestamp`.

### Task 4: Mẫu cảnh HyperFrames + thư viện SVG (điểm duyệt hình)

**Files:**
- Create: `pipeline/templates/canh/{minh-hoa,bieu-do,so-lon,nhan-vat,trang-nguon,chuong}.html`, `pipeline/templates/canh/base.css`
- Create: `pipeline/svg/*.svg` (10 hình đầu: toa-nha-quoc-hoi, dien-thoai, chip, laptop, tien, tai-lieu, nha-may, may-chu, co-viet-nam, bieu-do-nen)
- Create: `pipeline/svg/README.md` (quy ước vẽ)

**Interfaces:**
- Produces: mỗi mẫu là fragment HyperFrames nhận dữ liệu qua `data-*` / JSON nhúng, đúng các trường của `canh.json` ở Task 5. Quy ước SVG: viewBox `0 0 400 400`, isometric 30°, nét `#111111` 6px, chỉ dùng màu brand + 2 xám `#2A2A2A` `#BDBDBD`, không chữ trong SVG.

- [ ] **Step 1:** Nạp skill `hyperframes`, `hyperframes-cli`, `hyperframes-registry` (để dùng lại khối chữ/biểu đồ có sẵn trước khi tự viết).
- [ ] **Step 2:** Viết 6 mẫu + `base.css` (font SF Pro Heavy, nhãn chữ đậm trong khung bo tròn, ghi nguồn góc dưới trái 22px).
- [ ] **Step 3:** Vẽ 10 SVG theo quy ước.
- [ ] **Step 4:** Dựng `pipeline/templates/canh/demo/` gồm 1 cảnh mỗi mẫu với số liệu giá thật từ video 1; render khung hình (`npx hyperframes` snapshot/still) ra `demo/frames/*.png`.
- [ ] **Step 5: ĐIỂM DỪNG** – gửi ảnh các khung cho người dùng duyệt. Chưa có câu "duyệt" thì không sang Task 7.
- [ ] **Step 6:** Commit `feat: mẫu cảnh và thư viện SVG`.

### Task 5: Chia cảnh và phụ đề

**Files:**
- Create: `pipeline/tttc/canh.py`
- Test: `pipeline/tests/test_canh.py`

**Interfaces:**
- Consumes: `giong-timing.json` (Task 3).
- Produces:
  - Định dạng `canh.json`: `{"scenes":[{"id","mau","start","end","nhan"?,"svg"?,"bieu_do"?:{"kieu","nhan_x","gia_tri","don_vi","nguon_id"},"so"?,"anh"?,"nguon_anh"?,"chuong"?}]}` – `mau` là một trong 6 mẫu.
  - `validate(scenes: dict, timing: dict, svg_dir: Path) -> list[str]`
  - `to_srt(timing: dict, max_chars: int = 42) -> str`
  - CLI `python -m tttc.canh <video_dir>`: validate rồi ghi `phu-de.srt`.

- [ ] **Step 1: Test**
  - `test_validate_scenes_rejects_gap_and_overlap`
  - `test_validate_first_starts_zero_last_ends_duration` (±0,5 s)
  - `test_validate_flags_long_or_short_scene` (dưới 2 s hoặc trên 12 s là lỗi; ngoài 4–8 s là cảnh báo)
  - `test_validate_missing_svg_file`
  - `test_validate_chart_source_exists` (`nguon_id` phải có trong `nguon.json`)
  - `test_srt_lines_max_42_chars_and_ordered`
- [ ] **Step 2:** FAIL → viết `canh.py` → PASS.
- [ ] **Step 3:** Commit `feat: kiểm cảnh và phụ đề`.

### Task 6: Ảnh nhân vật từ Wikimedia Commons

**Files:**
- Create: `pipeline/tttc/anh.py`
- Test: `pipeline/tests/test_anh.py`, `pipeline/tests/fixtures/commons_*.json`

**Interfaces:**
- Produces: `search(query: str, limit: int = 10) -> list[dict]` (gọi `commons.wikimedia.org/w/api.php` với `generator=search&gsrnamespace=6&prop=imageinfo&iiprop=url|extmetadata&iiurlwidth=1600`); `pick(results) -> dict | None` – `{file, url, tac_gia, giay_phep, link}`; `download(item, video_dir) -> Path` vào `anh/`, nối một dòng vào `anh/ghi-cong.json`. Header `User-Agent: TuiTienCongNghe-pipeline/0.1` (không kèm email).

- [ ] **Step 1: Test** với fixture:
  - `test_pick_rejects_nonfree_license` (Fair use / không có LicenseShortName → bỏ)
  - `test_pick_accepts_cc_by_sa_and_pd`
  - `test_pick_strips_html_from_artist`
  - `test_download_appends_credit`
- [ ] **Step 2:** FAIL → viết → PASS.
- [ ] **Step 3:** Commit `feat: ảnh Commons có ghi công`.

### Task 7: Dựng, render, bảng soi hình

**Files:**
- Create: `pipeline/tttc/dung.py`, `pipeline/scripts/render.sh`
- Test: `pipeline/tests/test_dung.py`

**Interfaces:**
- Consumes: `canh.json`, `giong.mp3`, `phu-de.srt`, mẫu ở Task 4, `config.json:nhac_nen`.
- Produces:
  - `compose(video_dir, w=1920, h=1080, scene_range: tuple[int,int] | None = None, out="composition") -> Path` – thư mục HyperFrames; nhạc nền −20 dB dưới giọng.
  - `render.sh <composition_dir> <out.mp4>` – gọi HyperFrames render cục bộ.
  - `contact_sheet(video_mp4, scenes, out_png) -> Path` – 1 khung giữa mỗi cảnh, lưới 10 cột (ffmpeg `select` + `tile`).
  - `check_av(video_mp4, audio) -> list[str]` – lệch quá 0,5 s là lỗi.

- [ ] **Step 1: Test**
  - `test_compose_includes_every_scene_once`
  - `test_compose_scene_range_rebases_time` (cảnh 10–15 bắt đầu ở 0)
  - `test_check_av_detects_drift` (video 10 s + audio 11 s tạo bằng ffmpeg → 1 lỗi)
  - `test_contact_sheet_size` (3 cảnh → ảnh 1 hàng)
- [ ] **Step 2:** FAIL → viết → PASS.
- [ ] **Step 3:** Render thật bản demo của Task 4 kèm 30 s giọng, xem `final.mp4` và bảng soi hình.
- [ ] **Step 4:** Commit `feat: dựng và render`.

### Task 8: Thumbnail (mẫu chữ + nền TobyFlow)

**Files:**
- Create: `pipeline/tttc/thumb.py`
- Modify: `brand/make_brand.py` (dùng lại `font`/`centered` từ `tttc.thumb` thay vì định nghĩa lại)
- Test: `pipeline/tests/test_thumb.py`

**Interfaces:**
- Produces: `make(lines: list[tuple[str, str]], out: Path, background: Path | None = None) -> tuple[Path, Path]` – `lines` là `(chữ, "white"|"yellow")`; có `background` thì phủ ảnh 1280×720 (crop giữa) với lớp đen 55% trước khi viết chữ; trả về (ảnh 1280×720, bản 168 px).

- [ ] **Step 1: Test** – `test_make_sizes` (1280×720 và 168×94), `test_make_with_background_darkens` (độ sáng trung bình nền ≤ 45% ảnh gốc), `test_text_fits_width` (chữ dài tự giảm cỡ, không tràn quá 1200 px).
- [ ] **Step 2:** FAIL → viết → PASS. Chạy lại `python3 brand/make_brand.py`, ảnh ra giống bản cũ.
- [ ] **Step 3:** Commit `feat: thumbnail có nền TobyFlow`.

### Task 9: Skill `/video-dung`

**Files:**
- Create: `.claude/skills/video-dung/SKILL.md`
- Modify: `pipeline/tttc/duyet.py` (thêm `render_review_2`)
- Test: `pipeline/tests/test_duyet.py` (thêm)

**Interfaces:**
- Consumes: tất cả Task 3–8.
- Produces: `dong-goi.md` gồm 3 phương án `{tieu_de, chu_thumb, file_thumb}`, mô tả, chương, tags; `duyet-2.html`.

- [ ] **Step 1: Test** – `test_review_2_lists_three_options`, `test_review_2_links_video_and_shorts`, `test_review_2_shows_remaining_warnings` (nguồn `so-bo`).
- [ ] **Step 2:** FAIL → viết `render_review_2` → PASS.
- [ ] **Step 3:** Viết `SKILL.md`. Từ chối chạy nếu `duyet-1` chưa `da-duyet`. Các bước, mỗi bước gọi `set_step`:
  1. `tts.synthesize`
  2. Claude viết `canh.json` theo timestamp, vẽ SVG còn thiếu vào `pipeline/svg/` theo README, `anh.py` cho ảnh nhân vật, rồi chạy `tttc.canh` cho tới khi sạch
  3. `compose` + `render.sh` → `final.mp4`
  4. `contact_sheet`; Claude xem ảnh, sửa cảnh lỗi và render lại; `check_av`
  5. skill `yt-shorts` chọn đoạn → `compose(w=1080,h=1920,scene_range=...)` → `shorts/*.mp4`
  6. skill `yt-package` → 3 phương án; phương án 3 lấy nền từ TobyFlow `gen_image`. Prompt nền: không chữ, không mặt người thật, không logo, tông tối với điểm nhấn vàng. `thumb.make` chồng chữ.
  7. skill `yt-chapters` với mốc từ `giong-timing.json:paragraphs`; skill `yt-seo` cho mô tả, nối mục nguồn từ `nguon.json` và mục ghi công từ `anh/ghi-cong.json`
  8. `render_review_2`, đặt `duyet-2=cho-duyet`, gửi file rồi dừng. Khi người dùng duyệt thì ghi phương án đã chọn bằng `set_field(video_dir, "chon", 1|2|3)`.
- [ ] **Step 4:** Commit `feat: chặng 2 /video-dung`.

### Task 10: Upload YouTube + skill `/video-dang`

**Files:**
- Create: `pipeline/tttc/dang.py`, `.claude/skills/video-dang/SKILL.md`, `theo-doi.csv` (header: `ngay,tieu_de,gio_dang,link,view_24h,view_7d,ctr,giu_chan_30s`)
- Test: `pipeline/tests/test_dang.py`

**Interfaces:**
- Consumes: `trang_thai.is_approved`, `dong-goi.md`, phương án `chon`.
- Produces:
  - `publish_at(date_vn: str, time_vn: str) -> str` – RFC3339 UTC, múi `Asia/Ho_Chi_Minh`.
  - `build_body(video_dir) -> dict` – `snippet{title,description,tags,categoryId:"28",defaultLanguage:"vi"}`, `status{privacyStatus:"private",publishAt,selfDeclaredMadeForKids:false,containsSyntheticMedia:true}`.
  - `upload(video_dir, date_vn, time_vn) -> str` – `videos.insert` (resumable), `thumbnails.set`, `captions.insert` (SRT, `vi`), `playlistItems.insert`; nối dòng vào `theo-doi.csv`; đặt `dang=xong`; trả video id.
  - `login()` – OAuth installed-app flow với scope `youtube.upload` + `youtube.force-ssl`; refresh token lưu bằng keyring.

- [ ] **Step 1: Test** (không gọi mạng):
  - `test_publish_at_converts_vn_time` (`"13/11/2026","19:00"` → `"2026-11-13T12:00:00Z"`)
  - `test_upload_refuses_without_both_approvals` (raise, không gọi API)
  - `test_build_body_uses_chosen_option`
  - `test_build_body_title_max_100_chars`
  - `test_upload_appends_tracker_row` (mock client)
- [ ] **Step 2:** FAIL → viết → PASS.
- [ ] **Step 3:** Viết `SKILL.md`. Hỏi ngày/giờ (mặc định lấy từ `lich-4-tuan-dinh-vi-A.md`), xác nhận lại với người dùng trước khi upload, upload video rồi lần lượt từng Short (hẹn giờ theo lịch), báo link Studio.
- [ ] **Step 4:** Commit `feat: chặng 3 /video-dang`.

### Task 11: Chạy thật với video 1

**Files:**
- Create: `videos/2026-11-13-goi-ai/` (chuyển `kich-ban-video-1-antigravity.md` + `seo-video-1.md` + `goi-y-tieu-de-thumbnail-video-1.md` vào thành `kich-ban.md`/tài liệu tham khảo; tạo `nguon.json` từ 3 trang giá)

- [ ] **Step 1:** Người dùng: tạo khoá ElevenLabs và chọn giọng (ghi `voice_id` vào `config.json`), chạy `uv run python -c "import keyring; keyring.set_password('tui-tien-cong-nghe','elevenlabs', input())"`, chạy `uv run python -m tttc.dang login` (tạo dự án Google Cloud + OAuth client theo hướng dẫn trong SKILL).
- [ ] **Step 2:** Mở lại 3 trang giá, cập nhật `nguon.json`, điền tỷ giá ngày thu, gắn `[#id]` vào kịch bản, sửa 3 chỗ lệch đã thấy (dòng 44, "3 mẹo" → "4 mẹo", câu "11 phút"). `tttc.kiem` sạch → duyệt 1.
- [ ] **Step 3:** `/video-dung` → duyệt 2.
- [ ] **Step 4:** `/video-dang` hẹn giờ thứ Sáu 13/11/2026 19:00. Kiểm trong YouTube Studio: video riêng tư có lịch, thumbnail, phụ đề, nhãn nội dung tổng hợp.
- [ ] **Step 5:** Ghi lại thời gian người bỏ ra (mục tiêu ≤ 45 phút) và lỗi gặp phải vào `docs/superpowers/notes/2026-11-13-chay-thu.md`. Commit.
