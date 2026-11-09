# Nâng chất lượng video lên chuẩn kênh mẫu – Kế hoạch triển khai

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Video của kênh Túi Tiền Công Nghệ đạt các chỉ số hình, tiếng, kịch bản, thumbnail trong bảng "Thước đo" của benchmark, đo được tự động trước khi render.

**Architecture:** Giữ nguyên pipeline (`canh.json` → `dung.compose` → HyperFrames). Thêm một cổng đo (`chat_luong`), một bộ chia cảnh tự động (`chia`), mẫu cảnh và chuyển động mới, nhân vật dẫn chuyện, trộn nhạc có hạ tiếng, trạng thái nguồn "tự tính", và thumbnail chia đôi. Mỗi thay đổi có test; phần thị giác kiểm bằng ảnh chụp khung hình.

**Tech Stack:** Như pipeline hiện có (Python ≥3.11 qua `uv`, pytest, Pillow, ffmpeg, HyperFrames 0.9.26, GSAP 3.15). Thêm `qlmanage` (có sẵn trên macOS) để xem trước SVG.

**Spec:** `docs/nghien-cuu/kenh-mau-motcongnghe-2026-11-09.md` (số đo và thước đo), `docs/superpowers/specs/2026-11-08-pipeline-video-tu-dong-design.md` (kiến trúc gốc).

## Global Constraints

- Chạy mọi lệnh Python trong `pipeline/` bằng `uv run`; `uv run pytest -q` phải xanh sau mỗi task (hiện 109 test).
- Làm trên nhánh `pipeline`. Mỗi task một commit; thông điệp commit tiếng Việt kiểu `feat: …`, kèm dòng Co-Authored-By theo cấu hình phiên.
- Brand: nền `#111111`, vàng `#FFC800`, trắng `#FFFFFF`, font Inter trong video, SF Pro Heavy (`/System/Library/Fonts/SFNS.ttf`) trong thumbnail.
- Video dài 1920×1080 30 fps; Shorts 1080×1920; thumbnail 1280×720 + bản 168 px rộng.
- **Thay đổi so với spec gốc:** cảnh trung bình 2,8–4,5 s (spec gốc: 4–8 s, 80–120 cảnh). Độ dài hình = độ dài tiếng ±0,5 s giữ nguyên.
- Khoá API lưu bằng `keyring` service `tui-tien-cong-nghe`; không ghi vào file dự án.
- Không có đường nào upload được video thiếu một trong hai điểm duyệt.
- Mọi số hiện trên màn hình hoặc nói trong lời đọc phải có nguồn trong `nguon.json`, trừ số `tu-tinh` (Task 10).
- AI chỉ tạo ảnh nền thumbnail: không chữ, không mặt người thật, không logo hãng.
- Văn bản tiếng Việt chuẩn hoá NFC trước khi so khớp.
- Không dùng logo hãng, không dùng ảnh chân dung ngoài Wikimedia Commons (PD/CC0/CC BY/CC BY-SA, có ghi công) – chờ quyết định D2/D3.
- Hai tác vụ không cùng sửa một tệp: làn A (`dung.py`, `canh.py`, `templates/`), làn B (`svg/`), làn C (`kiem.py`, `tts.py`, `duyet.py`), làn D (`thumb.py`).

## Review Focus

1. **Cảnh quá ngắn sau khi chia tự động** (mảnh cuối, câu một từ) làm hình giật. Test: `test_chia_never_returns_scene_shorter_than_min` (Task 2).
2. **Số tự tính bị ghi nhầm là `xac-minh`, hoặc câu dùng số tự tính không có nhãn "tự tính"** – người xem tưởng là số chính thức. Test: `test_tu_tinh_requires_label_phrase` (Task 10).
3. **Nhạc nền không hạ khi có giọng, hoặc dài/ngắn hơn giọng.** Test: `test_tron_ducks_music_under_voice`, `test_tron_trims_long_music_and_loops_short` (Task 12).
4. **Thumbnail chia đôi khi không tìm được ảnh người tự do, hoặc dòng ghi công quá dài tràn khung.** Test: `test_chia_doi_without_left_image_splits_right_image`, `test_chia_doi_long_credit_stays_inside` (Task 14).
5. **Nhân vật dẫn chuyện lệch giờ khi cắt Shorts (`scene_range`) hoặc xuất hiện trong khung dọc.** Test: `test_compose_scene_range_keeps_mascot_inside_range`, `test_compose_vertical_has_no_mascot` (Task 8).

## Quyết định cần bạn (có mặc định, đổi được)

| # | Câu hỏi | Mặc định nếu bạn không đổi | Ảnh hưởng |
|---|---|---|---|
| D1 | Nhân vật dẫn chuyện riêng của kênh | "Túi": chiếc túi tiền vàng isometric, hai mắt tròn, không kính (khác "Mọt" của kênh mẫu). Bạn duyệt bảng 3 dáng trước khi dùng | Task 8 |
| D2 | Thumbnail dùng chân dung người thật | Chỉ ảnh Commons tự do có ghi công; không có thì dùng hình minh họa | Task 14 |
| D3 | Logo hãng trong video/thumbnail | Không dùng; hãng hiện bằng nhãn chữ | Task 5–7, 14 |
| D4 | Video 1 (13/11 19:00) | Đăng đúng hẹn bằng pipeline hiện có + Task 1–3, 12, 13 (đo, nhạc, giọng). Chuẩn mới áp dụng từ video 3–4 | Lịch |
| D5 | Bài nhạc nền | Bạn chọn 1–2 bài lofi/ambient trong YouTube Audio Library (README ở `am-thanh/nhac/`) | Task 12 |

## Lịch gợi ý (ước lượng, chưa đo)

| Giai đoạn | Việc | Bạn cần làm |
|---|---|---|
| 09–12/11 (video 1) | Task 1, 2, 3, 12 (phần trộn nhạc), 13 | Khoá ElevenLabs + nghe thử giọng; chọn nhạc; đăng nhập YouTube; duyệt 2 điểm |
| 13/11 | Video 1 lên sóng | – |
| 14–20/11 | Task 4, 5, 6, 7 (làn A) song song Task 9 (làn B), Task 10, 11 (làn C) | Duyệt bảng nhân vật (D1) |
| 21–27/11 | Task 8, 14, 12 (SFX) | Duyệt thumbnail mẫu |
| 28/11 → | Task 15 (nếu cần), Task 16 trên video 3 hoặc 4 | So sánh cạnh nhau với video kênh mẫu |

Cỡ việc: S ≤ nửa ngày, M ≈ 1 ngày, L ≥ 2 ngày phiên làm việc. Task 1,10,11,13 = S; 2,3,4,5,6,7,12,14,15 = M; 8,9,16 = L.

---

### Task 1: Cổng đo chất lượng `chat_luong` (S)

**Files:**
- Create: `pipeline/tttc/chat_luong.py`, `pipeline/tests/test_chat_luong.py`
- Modify: `pipeline/tttc/duyet.py` (hàm `render_review_2`), `pipeline/tests/test_duyet.py`

**Interfaces:**
- Consumes: `dung.steps(c, words) -> list[float]`, `dung.sfx_events(c, st)`, `dung.transitions(scenes)`, `canh.MAU`.
- Produces:
  - `NHOM: dict[str, set[str]]` = `{"do-hoa": {minh-hoa, quy-trinh, so-sanh, thoi-gian, so-lon, bieu-do, chuong}, "bang-chung": {trich-bao, trang-nguon}, "doi-that": {b-roll, nhan-vat}}`
  - `MUC_TIEU: dict` – ngưỡng đúng như bảng ở mục 4 của benchmark.
  - `do(canh: dict, timing: dict) -> dict` với khoá `so_canh:int, tb_giay:float, duoi_1_5:int, tren_8:int, ti_le:dict[str,float], chay_dai_nhat:int, su_kien_phut:float, sfx_phut:float, toc_do:float`.
  - `kiem(so_do: dict, muc: dict = MUC_TIEU) -> list[str]` (chuỗi bắt đầu `Lỗi:` hoặc `Cảnh báo:`).
  - `main(video_dir: str) -> int` (1 nếu có `Lỗi`).

- [ ] **Step 1: Viết test (`test_chat_luong.py`)**: `test_do_counts_mix_and_average` (4 cảnh dài 3,3,4,2 s → `tb_giay == 3.0`, `ti_le` cộng bằng 1), `test_do_empty_scenes_does_not_divide_by_zero` (`so_canh == 0`, `kiem` trả đúng một `Lỗi: canh.json không có cảnh nào`), `test_do_longest_same_template_run`, `test_kiem_error_on_scene_under_1_5s`, `test_kiem_warns_on_slow_pace` (`tb_giay` 6 → có `Cảnh báo` chứa "Độ dài trung bình"), `test_kiem_passes_channel_like_profile` (hồ sơ giống kênh mẫu → `[]`).
- [ ] **Step 2:** `uv run pytest tests/test_chat_luong.py -q` → FAIL (module chưa có).
- [ ] **Step 3:** Cài `do`/`kiem`/`main` như Interfaces. `su_kien_phut` = (số cảnh + tổng số bước từ `dung.steps` + số cảnh có `dan`) / phút. `toc_do` = số từ / phút từ `timing["words"]`.
- [ ] **Step 4:** Test duyệt 2: `test_review_2_shows_quality_warnings` – dựng video giả có `tb_giay` 6, trang `duyet-2.html` chứa "Độ dài trung bình". Sửa `render_review_2` cộng thêm `chat_luong.kiem(do(canh, timing))` vào `warns` (chỉ khi có `canh.json` và `giong-timing.json`).
- [ ] **Step 5:** `uv run pytest -q` → toàn bộ xanh. Chạy thử `uv run python -m tttc.chat_luong templates/canh-demo` và ghi lại các cảnh báo (đây là số đo gốc của demo).
- [ ] **Step 6: Commit** `feat: cổng đo chất lượng theo chuẩn kênh mẫu`.

### Task 2: Chia cảnh tự động và ngưỡng nhịp mới (M)

**Files:**
- Create: `pipeline/tttc/chia.py`, `pipeline/tests/test_chia.py`
- Modify: `pipeline/tttc/canh.py` (hàm `validate`), `pipeline/tests/test_canh.py` (test `test_validate_flags_long_or_short_scene`), `.claude/skills/video-dung/SKILL.md` (bước 2)

**Interfaces:**
- Consumes: `giong-timing.json` (`words: [{w,start,end}]`, `duration`).
- Produces:
  - `canh.CANH_MIN_LOI = 1.5`, `CANH_MAX_LOI = 10.0`, `CANH_MIN_CB = 2.5`, `CANH_MAX_CB = 6.0`.
  - `chia.chia(timing: dict, muc: float = 3.5, toi_thieu: float = 2.0, toi_da: float = 5.5) -> list[dict]` – mỗi phần tử `{"id": "c001", "start": float, "end": float, "loi": str}`.
  - `chia.main(video_dir: str) -> int` ghi `canh-khung.json` = `{"scenes": [...]}`.

- [ ] **Step 1: Viết test (`test_chia.py`)**: `test_chia_covers_whole_duration_without_gaps` (cảnh đầu `start == 0`, cảnh cuối `end == duration`, `start` mỗi cảnh = `end` cảnh trước), `test_chia_respects_min_and_max` (600 từ giả, mỗi từ 0,4 s), `test_chia_prefers_sentence_end` (từ kết câu ở 3,2 s thắng dấu phẩy ở 3,5 s), `test_chia_never_returns_scene_shorter_than_min` (mảnh cuối ngắn được gộp vào cảnh trước; câu một từ không tách riêng), `test_chia_text_is_union_of_words` (ghép `loi` = ghép mọi từ, không mất, không lặp).
- [ ] **Step 2: Cập nhật test canh**: cảnh 1,2 s → `Lỗi`; 2,0 s → `Cảnh báo`; 3 s → sạch; 7 s → `Cảnh báo`; 11 s → `Lỗi`.
- [ ] **Step 3:** `uv run pytest tests/test_chia.py tests/test_canh.py -q` → FAIL.
- [ ] **Step 4:** Cài `chia`. Thuật toán duyệt từ trái sang phải; điểm ngắt hợp lệ sau từ thứ i khi độ dài ≥ `toi_thieu`; điểm = ưu tiên kết câu (`.!?`) > dấu phẩy/chấm phẩy > đứng trước liên từ {mà, nhưng, còn, thì, vì, nên, tức là, rồi} > gần `muc` nhất; ép ngắt khi chạm `toi_da`. Mốc ngắt = trung điểm giữa `end` từ trước và `start` từ sau.
- [ ] **Step 5:** Thay hằng số cứng trong `canh.validate` bằng bốn hằng số mới. Sửa bước 2 của SKILL `video-dung`: "chạy `uv run python -m tttc.chia V` để có `canh-khung.json`; điền `mau` và nội dung cho từng cảnh, không đổi mốc `start/end`; 2,8–4,5 s/cảnh, ~165–220 cảnh/11 phút".
- [ ] **Step 6:** `uv run pytest -q` → xanh. **Commit** `feat: chia cảnh tự động theo giọng đọc, ngưỡng nhịp 2,8–4,5 s`.

### Task 3: Chạy thử 2 phút, đo render (M, không TDD)

**Files:**
- Create: `pipeline/tttc/giong_tam.py`, `pipeline/tests/test_giong_tam.py`, `docs/nghien-cuu/do-render-2026-11-09.md`
- Modify: `pipeline/templates/canh-demo/tao-demo.py` (dùng lại `giong_tam`)

**Interfaces:**
- Produces: `giong_tam.giong_tam(text: str, out_dir: Path, toc_do: int = 185) -> dict` – tạo `giong.mp3` bằng `say -v Linh`, trả `{"duration", "words", "paragraphs": []}` (cùng định dạng `giong-timing.json`).

- [ ] **Step 1: Test** `test_giong_tam_timing_covers_duration` (bỏ qua nếu không có lệnh `say`): `words[-1]["end"] <= duration`, số từ = số từ của text.
- [ ] **Step 2:** Tách logic `say` + chia thời gian đều theo ký tự từ `tao-demo.py` sang `giong_tam.py`; `tao-demo.py` gọi lại. `uv run pytest -q` xanh.
- [ ] **Step 3:** Tạo `videos/thu-nghiem/` từ ~2 phút đầu của `kich-ban-video-1-antigravity.md` (chuyển sang định dạng `kich-ban.md` + `nguon.json` của pipeline). Chạy `tttc.chia`, điền `canh.json` bằng các mẫu hiện có theo mật độ mới, chạy `tttc.chat_luong`, ghi lại các cảnh báo.
- [ ] **Step 4:** Render `draft` rồi `delivery`: `scripts/render.sh videos/thu-nghiem/composition videos/thu-nghiem/final.mp4 delivery`. Ghi giờ bắt đầu/kết thúc và theo dõi `top` (CPU %, RAM) trong lúc render.
- [ ] **Step 5:** Ghi vào `do-render-2026-11-09.md`: số cảnh, giây render mỗi phút video (draft, delivery), CPU trung bình, **ước tính render 12 phút**, và danh sách lỗi hình nhìn thấy trên bảng soi hình (chữ tràn, cảnh trống, nhịp chậm). Quy tắc quyết định: ước tính delivery > 90 phút **và** CPU trung bình < 60% → làm Task 15; ngược lại bỏ Task 15.
- [ ] **Step 6: Commit** `feat: chạy thử 2 phút đo thời gian render`. (Không `git add videos/thu-nghiem`: `.gitignore` chỉ chặn tệp nặng, các tệp json vẫn bị theo dõi.)

### Task 4: Chuyển động lặp trong cảnh (M)

**Files:**
- Create: `pipeline/templates/canh/dong.js`
- Modify: `pipeline/templates/canh/minh-hoa.html`, `so-lon.html`, `pipeline/tttc/dung.py` (`_scene_file`, `_vars`, docstring đầu tệp), `pipeline/tttc/canh.py` (`validate`), `pipeline/tests/test_dung.py`, `pipeline/tests/test_canh.py`

**Interfaces:**
- Produces:
  - `dong.js` định nghĩa `function dongLap(tl, selector, kieu, t0, t1)` thêm tween lặp **hữu hạn** (không `repeat: -1`, để render xác định) cho `kieu ∈ {"bob","xoay","dap","chop"}` từ `t0` tới `t1`.
  - `canh.DONG = {"", "bob", "xoay", "dap", "chop"}`; trường cảnh `dong` (mặc định `"bob"` cho vật chính `minh-hoa`; `so-lon` mặc định `""`).
  - `_scene_file` thay token `/*__DONG__*/` bằng nội dung `dong.js`.

- [ ] **Step 1: Viết test**: `test_scene_file_injects_dong_helper` (`"function dongLap"` có trong `_scene_file("minh-hoa","c1")`, không còn `__DONG__`), `test_vars_minh_hoa_default_dong_bob`, `test_validate_rejects_unknown_dong` (`dong: "nhay"` → `Lỗi`).
- [ ] **Step 2:** `uv run pytest tests/test_dung.py tests/test_canh.py -q` → FAIL.
- [ ] **Step 3:** Viết `dong.js` (chu kỳ: bob 2,4 s biên 14 px; xoay 6 s/vòng; dap 1,2 s scale 1→1,04; chop 1,6 s sáng 1→1,25). Gắn token vào đầu script của `minh-hoa` và `so-lon`; gọi `dongLap(tl, "#mh-chinh", v.dong, 0.9, 9)`; đạo cụ dùng `bob` lệch pha 0,4 s.
- [ ] **Step 4:** Thêm `dong` vào `_vars` và biến `composition-variables` của hai mẫu; thêm kiểm `dong` trong `validate`; cập nhật docstring `dung.py` và SKILL.
- [ ] **Step 5:** `uv run pytest -q` xanh. **Kiểm thị giác:** dựng `canh-demo`, chụp `npx hyperframes snapshot` (xem `--help` cho cờ chọn thời điểm) ở 1,5 s và 2,5 s của cảnh `minh-hoa`; hai ảnh phải khác nhau ở vùng vật chính (so bằng `PIL.ImageChops.difference`).
- [ ] **Step 6: Commit** `feat: chuyển động lặp trong cảnh minh họa và số lớn`.

### Task 5: Mẫu `quy-trinh` (M)

Các điểm phải chạm khi thêm một mẫu cảnh (áp dụng cho Task 5, 6, 7): (1) `templates/canh/<mau>.html`; (2) `canh.MAU`; (3) `dung.PREFIX`; (4) nhánh trong `dung._vars`; (5) `dung.DEFAULT_STEPS` hoặc nhánh riêng trong `dung.steps()` khi số bước đổi theo cảnh (như `bieu-do`); (6) nhánh trong `dung.sfx_events`; (7) `canh._check_values` nếu có số trên màn hình; (8) docstring đầu `dung.py` và SKILL `video-dung`; (9) tập `chat_luong.NHOM["do-hoa"]`; (10) test trong `test_dung.py` và `test_canh.py`.

**Files:**
- Create: `pipeline/templates/canh/quy-trinh.html`
- Modify: các điểm (2)–(10) ở trên, `pipeline/tests/test_dung.py`, `pipeline/tests/test_canh.py`

**Interfaces:**
- Produces: mẫu `quy-trinh`, tiền tố id `qt-`. Trường: `tieu_de?: str`, `buoc: list[{"nhan": str, "svg"?: str}]` (3–6 phần tử), `noi_bat?: int`, `nguon_id?: str|list`, `nhip?: list[str]` (một cụm cho mỗi bước). `steps()` trả `[0.5 + 0.55 * i for i in range(len(buoc))]`.

- [ ] **Step 1: Viết test**: `test_validate_quy_trinh_step_count` (2 bước và 7 bước → `Lỗi`; 4 bước → sạch), `test_validate_quy_trinh_noi_bat_in_range`, `test_compose_quy_trinh_vars` (biến `buoc` là JSON danh sách nhãn + đường dẫn `assets/svg/<svg>.svg`), `test_steps_quy_trinh_one_per_step`, `test_sfx_quy_trinh_one_pop_per_step` (âm `pop`, 0,2).
- [ ] **Step 2:** Chạy → FAIL. Cài các điểm (2)–(7), (9).
- [ ] **Step 3:** Viết `quy-trinh.html`: các nút xếp ngang đều trong vùng 1600 px; mỗi nút = hình SVG 220 px + nhãn `nhan-pill`; mũi tên giữa các nút "vẽ" bằng `scaleX` khi bước tiếp theo xuất hiện; nút `noi_bat` có vòng vàng; dùng `dongLap` cho nút nổi bật.
- [ ] **Step 4:** `uv run pytest -q` xanh. **Kiểm thị giác:** thêm một cảnh 4 bước (thiết kế → đúc → đóng gói → kiểm thử) vào demo, xem ảnh chụp khung ở cuối cảnh: chữ không tràn, mũi tên không chồng nút.
- [ ] **Step 5: Commit** `feat: mẫu cảnh quy-trinh`.

### Task 6: Mẫu `so-sanh` (M)

**Files:**
- Create: `pipeline/templates/canh/so-sanh.html`
- Modify: như danh sách điểm chạm ở Task 5, đặc biệt `canh._check_values`.

**Interfaces:**
- Produces: mẫu `so-sanh`, tiền tố `ss-`. Trường: `trai`, `phai` = `{"nhan": str, "svg": str, "so"?: number|str, "to"?: float}` (`to` trong (0, 1], kích thước tương đối, mặc định 1), `don_vi?: str`, `ti_le?: str` (nhãn kiểu "gấp ~700 lần"), `nguon_id` (bắt buộc nếu có `so`). `steps()` mặc định `[0.5, 1.1, 1.8]` (bên trái, bên phải, nhãn tỉ lệ).

- [ ] **Step 1: Viết test**: `test_check_values_so_sanh_matches_source` (số lệch nguồn → `Lỗi`), `test_validate_so_sanh_requires_nguon_id_when_number`, `test_validate_so_sanh_to_range` (`to: 0` và `to: 1.5` → `Lỗi`), `test_compose_so_sanh_vars`.
- [ ] **Step 2:** Chạy → FAIL. Mở rộng `_check_values`: với `so-sanh`, `vals = [trai.so, phai.so]` (bỏ giá trị thiếu), `scale = _unit_scale(don_vi)`.
- [ ] **Step 3:** Cài các điểm chạm và `so-sanh.html` (hai nửa màn hình, huy hiệu "VS" ở giữa, kích thước hình = 560 px × `to`, số lớn dưới mỗi hình đếm lên bằng cùng cơ chế của `so-lon`).
- [ ] **Step 4:** `uv run pytest -q` xanh. **Kiểm thị giác:** cảnh "208 tỷ transistor (to 1,0) so với 300 triệu (to 0,15)": hình bên phải nhỏ rõ rệt, nhãn đọc được.
- [ ] **Step 5: Commit** `feat: mẫu cảnh so-sanh`.

### Task 7: Mẫu `thoi-gian` (M)

**Files:**
- Create: `pipeline/templates/canh/thoi-gian.html`
- Modify: như danh sách điểm chạm ở Task 5.

**Interfaces:**
- Produces: mẫu `thoi-gian`, tiền tố `tg-`. Trường: `truc: {"tu": number, "den": number, "don_vi": str}`, `hang: list[{"nhan": str, "tu": number, "den": number, "noi_bat"?: bool}]` (2–5 hàng), `nguon_id` (bắt buộc). `steps()` = `[0.5 + 0.6 * i for i in range(len(hang))]`.

- [ ] **Step 1: Viết test**: `test_validate_thoi_gian_rows_in_axis` (hàng nằm ngoài trục, hoặc `tu >= den` → `Lỗi`), `test_validate_thoi_gian_row_count`, `test_check_values_thoi_gian_years_in_source` (năm không có trong `gia_tri` của nguồn → `Lỗi`), `test_compose_thoi_gian_vars`.
- [ ] **Step 2:** Chạy → FAIL; cài các điểm chạm (`_check_values` lấy mọi `tu`/`den`).
- [ ] **Step 3:** Viết `thoi-gian.html`: trục ngang có vạch năm; mỗi hàng là thanh vàng lớn dần từ trái sang phải theo `nhip`; hàng `noi_bat` có viền trắng; nhãn bên trái.
- [ ] **Step 4:** `uv run pytest -q` xanh. **Kiểm thị giác:** ví dụ Singapore 2024–2026, Ấn Độ 2024–2028, Hoà Lạc 2026–2030.
- [ ] **Step 5: Commit** `feat: mẫu cảnh thoi-gian`.

### Task 8: Nhân vật dẫn chuyện "Túi" (L)

**Files:**
- Modify: `pipeline/svg/ve.py` (hàm `tui(the: str, nham: bool)` + `ITEMS`), `pipeline/tttc/dung.py` (`compose`), `pipeline/tttc/canh.py` (`validate`), `pipeline/tests/test_dung.py`, `pipeline/tests/test_canh.py`
- Create: `pipeline/svg/tui-chao.svg`, `tui-ngac-nhien.svg`, `tui-nghi.svg` và ba bản `-nham.svg` (sinh bằng `ve.py`)

**Interfaces:**
- Produces: trường cảnh `dan: {"the": "chao"|"ngac-nhien"|"nghi", "goc": "phai"|"trai", "tu"?: str}`; `canh.DAN_THE = {"chao","ngac-nhien","nghi"}`. `compose` thêm một clip `#dan-{k}` (track 3) cho mỗi cảnh có `dan`, gồm hai `<img>` mở mắt/nhắm mắt; tween: bật vào ở `phrase_time(tu)` hoặc 0,3 s sau đầu cảnh, nhấp nhô nhẹ, chớp mắt (đổi độ mờ hai ảnh 0,12 s) mỗi 2,8 s. Khung dọc (Shorts) không có nhân vật.

- [ ] **Step 1 (cổng duyệt D1):** viết `tui()` theo quy ước `svg/README.md` (isometric, một điểm nhấn vàng, không chữ), sinh 3 dáng; ghép thành một ảnh (`qlmanage -t -s 300 -o <thư mục tạm> svg/tui-*.svg`, ghép bằng Pillow) và **gửi bạn duyệt**. Chưa làm bước 2 khi chưa được duyệt.
- [ ] **Step 2: Viết test**: `test_validate_dan_unknown_pose`, `test_compose_adds_mascot_clip_for_scene_with_dan` (có `id="dan-0"` với `data-start` bằng đầu cảnh), `test_compose_scene_range_keeps_mascot_inside_range` (với `scene_range` cắt giữa video, mọi `data-start` của clip nhân vật nằm trong `[0, total]`), `test_compose_vertical_has_no_mascot` (`h > w` → không có `dan-`).
- [ ] **Step 3:** Chạy → FAIL. Cài `compose` và `validate`. Ghi chú trong mã: `# shortcut: Shorts không có nhân vật; thêm khi có nhu cầu`.
- [ ] **Step 4:** `uv run pytest -q` xanh. **Kiểm thị giác:** cảnh `so-lon` có `dan: {"the":"ngac-nhien","goc":"phai","tu":"năm trăm"}` – chụp khung tại thời điểm từ đó được nói: nhân vật không che số lớn.
- [ ] **Step 5: Commit** `feat: nhân vật dẫn chuyện Túi`.

### Task 9: Mở rộng thư viện SVG từ 17 lên ≥ 55 hình (L)

**Files:**
- Create: `pipeline/tests/test_svg.py`, `pipeline/svg/sheet.py`
- Modify: `pipeline/svg/ve.py` (`ITEMS`), `pipeline/svg/README.md`

**Interfaces:**
- Produces: `sheet.sheet(svg_dir: Path, out_png: Path, cot: int = 8) -> Path` (ghép ảnh `qlmanage` của mọi SVG kèm tên tệp). Quy tắc thư viện (test): không có `<text`; `viewBox` vuông (rộng = cao); ≤ 20 KB mỗi tệp; màu ⊂ bảng brand `{#111111,#FFFFFF,#BDBDBD,#6E6E6E,#2A2A2A,#FFC800,#E0B000,#C79C00}`, trừ ngoại lệ có tên: `cay` (`#5A4426,#6E5430,#8A6A3A`), `co-viet-nam` (`#A51B15,#DA251D`), `nen-dat` (`#141414,#1A1A1A,#262626,#2F2F2F,#3A3A3A`).

- [ ] **Step 1: Viết test** `test_every_svg_follows_library_rules` (duyệt mọi `svg/*.svg`; 17 hình hiện có phải qua) và `test_library_has_at_least_55_shapes` (chưa qua).
- [ ] **Step 2:** Chạy → số hình FAIL, quy tắc PASS. Thêm hình theo ba đợt, mỗi đợt xong chạy `uv run python svg/ve.py` và `sheet.py`, **xem ảnh tổng**, sửa hình xấu rồi mới sang đợt sau:
  - Đợt A – chip/bán dẫn (16): `wafer`, `nha-may-duc`, `phong-sach`, `may-quang-khac`, `chip-bao-mat`, `usb`, `o-khoa`, `chia-khoa`, `khien`, `transistor`, `soi-toc`, `hat-gao`, `san-bong`, `thuoc-do`, `dong-ho`, `lich`.
  - Đợt B – AI/dữ liệu/crypto (12): `trung-tam-du-lieu`, `bo-nao-ai`, `robot`, `dam-may`, `pin`, `tia-set`, `tram-phat-song`, `bong-bong`, `do-thi-roi`, `ket-sat`, `the-ngan-hang`, `vi-tien`.
  - Đợt C – kinh tế/chính trị/đời sống (12): `can-cung-cau`, `bua-phan-quyet`, `ta-hang`, `cang-bien`, `oto`, `kinh-lup`, `ten-lua`, `hop-thu`, `thue-phan-tram`, `nguoi-nhom`, `tui-xach`, `cao-oc`.
- [ ] **Step 3:** `uv run pytest -q` xanh. Cập nhật `svg/README.md` với bảng nhóm hình.
- [ ] **Step 4: Commit** `feat: thư viện SVG 55+ hình theo ba nhóm chủ đề`.

### Task 10: Trạng thái nguồn `tu-tinh` (S)

**Files:**
- Modify: `pipeline/tttc/kiem.py`, `pipeline/tttc/duyet.py` (`_sources_table`), `pipeline/tests/test_kiem.py`, `pipeline/tests/test_duyet.py`, `.claude/skills/video-moi/SKILL.md` (bước 2)

**Interfaces:**
- Produces: mục `nguon.json` với `"trang_thai": "tu-tinh"` bắt buộc có `cong_thuc: str` và `dau_vao: list[str]` (id có thật trong `nguon.json`). `kiem.WARN_TU_TINH = ("tự tính", "tự ướm", "mình tính", "không phải dự báo")`.

- [ ] **Step 1: Viết test**: `test_tu_tinh_requires_formula_and_inputs` (thiếu `cong_thuc` hoặc `dau_vao` trỏ id không tồn tại → lỗi), `test_tu_tinh_requires_label_phrase` (câu có số tự tính mà không chứa cụm trong `WARN_TU_TINH` → lỗi; có cụm → sạch), `test_tu_tinh_value_still_matched` (số trong câu lệch `gia_tri` → lỗi như mọi nguồn), `test_sources_table_shows_formula` (trang duyệt 1 hiện `cong_thuc` thay cho trích dẫn).
- [ ] **Step 2:** Chạy → FAIL. Cài trong `kiem.check` (cùng chỗ xử lý `so-bo`) và `_sources_table`.
- [ ] **Step 3:** Sửa SKILL `video-moi` bước 2: số suy ra từ hai số khác (hiệu năm, tỉ lệ, "gấp N lần") ghi `tu-tinh` với `cong_thuc`, không ghi `xac-minh`; câu trong kịch bản phải nói "mình tự tính".
- [ ] **Step 4:** `uv run pytest -q` xanh. **Commit** `feat: trạng thái nguồn tu-tinh cho số tự suy ra`.

### Task 11: Kiểm phong cách kịch bản (S)

**Files:**
- Create: `pipeline/tttc/phong_cach.py`, `pipeline/tests/test_phong_cach.py`, `docs/phong-cach-kich-ban.md`
- Modify: `pipeline/tttc/tts.py` (`spoken_paragraphs`), `pipeline/tests/test_tts.py`, `pipeline/tttc/duyet.py` (`render_review_1`), `.claude/skills/video-moi/SKILL.md` (bước 3)

**Interfaces:**
- Produces:
  - `tts.spoken_paragraphs(script_md: str, keep_tags: bool = False) -> list[str]` (mặc định hành vi cũ).
  - `phong_cach.kiem(script_md: str) -> list[str]` – chỉ trả `Cảnh báo:`: 90 từ đầu thiếu thẻ `[#id]` (số có nguồn) hoặc thiếu dấu `?`; 60 từ cuối thiếu `?`; số từ lời đọc ngoài 1.500–1.900.

- [ ] **Step 1: Viết test**: `test_spoken_paragraphs_keep_tags`, `test_hook_needs_number_and_question`, `test_closing_needs_question`, `test_length_window`.
- [ ] **Step 2:** Chạy → FAIL. Cài; `render_review_1` cộng `phong_cach.kiem` vào danh sách cảnh báo.
- [ ] **Step 3:** Viết `docs/phong-cach-kich-ban.md` (một trang, 8 quy tắc rút từ mục 2 của benchmark: móc = sự kiện + cặp số lạ + 3 câu hỏi hứa; xưng "mình"; ví dụ đời thường ≤ 2 phút/lần; tự hỏi tự đáp; nói tên nguồn trong lời; số tự tính gắn nhãn; mỗi phần là một câu hỏi; kết trả lời tiêu đề rồi mời đoán). SKILL `video-moi` bước 3 yêu cầu gửi tệp này cho `yt-script`.
- [ ] **Step 4:** `uv run pytest -q` xanh. **Commit** `feat: kiểm phong cách kịch bản và thẻ phong cách`.

### Task 12: Trộn nhạc có hạ tiếng và hiệu ứng âm thanh dày hơn (M)

**Files:**
- Create: `pipeline/tttc/tron_am.py`, `pipeline/tests/test_tron_am.py`
- Modify: `pipeline/tttc/dung.py` (`compose`, `sfx_events`, bỏ `NHAC_DB` và thẻ `<audio id="nhac">`), `pipeline/tests/test_dung.py`, `pipeline/am-thanh/sfx/*.mp3`, `CREDITS.md`, `nhac/README.md`, `pipeline/config.json` (`nhac_nen`)

**Interfaces:**
- Produces: `tron_am.tron(giong: Path, nhac: Path, out: Path, ha_db: float = -20.0, vao: float = 1.0, ra: float = 2.0) -> Path` – `out` dài đúng bằng `giong` (±0,05 s), nhạc cắt/lặp cho vừa, nhạc ở `ha_db` dưới giọng khi có tiếng, nhạc tăng ≥ 6 dB trong chỗ lặng (ffmpeg `sidechaincompress`). Khi `config.nhac_nen` có giá trị, `compose` ghi bản trộn vào `assets/giong.mp3` và không còn thẻ nhạc riêng.

- [ ] **Step 1: Viết test**: `test_tron_keeps_voice_duration`; `test_tron_ducks_music_under_voice` (nhạc = sin 440 Hz, giọng = sin 1000 Hz trong 0–2 s và 4–6 s, im ở 2–4 s; đo bằng `bandpass=f=440,volumedetect`: mức 440 Hz ở 2–4 s cao hơn mức ở 0–2 s ≥ 6 dB); `test_tron_trims_long_music_and_loops_short`; trong `test_dung.py`: `test_compose_mixes_music_into_voice_track`, `test_compose_without_music_copies_voice`.
- [ ] **Step 2:** Chạy → FAIL. Cài `tron`; sửa `compose`.
- [ ] **Step 3:** Thêm 4 hiệu ứng (`ding`, `go-phim`, `khoa-cach`, `whoosh-dai`) chọn từ thư viện Pixabay kèm skill `media-use`, ghi `CREDITS.md`; thêm vào `sfx_events` của các mẫu mới (`quy-trinh`: `pop` mỗi bước; `so-sanh`: `pop` hai bên + `ding` ở nhãn tỉ lệ; `thoi-gian`: `whoosh-short` mỗi thanh) và `ding` cho `so-lon` khi đếm xong; giữ `ping` cũ nếu test cũ cần.
- [ ] **Step 4 (bạn làm, D5):** chọn bài nhạc, đặt vào `am-thanh/nhac/`, ghi `config.json:nhac_nen`.
- [ ] **Step 5:** `uv run pytest -q` xanh. **Kiểm đo thật:** dựng `canh-demo` có nhạc, chạy `npx hyperframes audio` trên bản render để thấy mức nhạc giảm khi có giọng. **Commit** `feat: trộn nhạc nền hạ tiếng, thêm hiệu ứng âm thanh`.

### Task 13: Chọn giọng và thông số giọng (S)

**Files:**
- Modify: `pipeline/tttc/tts.py` (`_call`, `seg_name`, thêm `audition`), `pipeline/config.json`, `pipeline/tests/test_tts.py`

**Interfaces:**
- Produces: `config.elevenlabs` thêm khoá tùy chọn `stability`, `similarity_boost`, `style` (số 0–1); `_call` đưa chúng vào `voice_settings` khi có; `seg_name` băm cả ba giá trị (đổi thông số thì tổng hợp lại). `tts.audition(text: str, voice_ids: list[str], out_dir: Path, post=requests.post, key: str | None = None, cfg: dict | None = None) -> list[Path]` ghi `out_dir/<voice_id>.mp3`.

- [ ] **Step 1: Viết test**: `test_call_sends_voice_settings_when_configured`, `test_seg_name_changes_with_stability`, `test_audition_writes_one_file_per_voice`.
- [ ] **Step 2:** Chạy → FAIL; cài; `uv run pytest -q` xanh.
- [ ] **Step 3 (bạn làm):** tạo khoá ElevenLabs, đưa vào Keychain; chọn 3–4 giọng nam miền Bắc trong thư viện; chạy `audition` với đoạn 30 s có từ khó ("ChatGPT", "nanomet", "năm trăm hai mươi hai nghìn năm trăm đồng"); nghe và chọn; điền `voice_id`. Tiêu chí: tự nhiên, không đều đều, đọc đúng số và tên riêng, tốc độ 130–160 từ/phút (đo bằng `chat_luong.toc_do`).
- [ ] **Step 4: Commit** `feat: thông số giọng và nghe thử nhiều giọng`.

### Task 14: Thumbnail chia đôi (M)

**Files:**
- Modify: `pipeline/tttc/thumb.py`, `pipeline/tests/test_thumb.py`, `.claude/skills/video-dung/SKILL.md` (bước 6)

**Interfaces:**
- Produces:
  - `thumb.chia_doi(trai: Path | None, phai: Path, dong: list[str], out: Path, ghi_cong: str = "", vs: bool = True) -> tuple[Path, Path]` (ảnh 1280×720 và bản 168 px). Khi `trai is None`, chia đôi bằng hai nửa của `phai` (cắt trái/phải).
  - `thumb.khung_tu_video(video: Path, t: float, out: Path) -> Path` (ffmpeg lấy một khung).
  - Bố cục: viền vàng 10 px; đường chia răng cưa quanh x = 640 (7 răng, biên 24 px); huy hiệu "VS" vàng r = 62 giữa khung; tối đa 2 hộp chữ nền vàng chữ đen đậm ở góc dưới trái (chiều rộng ≤ 1100 px); dòng ghi công 18 px góc trên phải, rộng ≤ 460 px, cắt bằng "…" nếu dài hơn.

- [ ] **Step 1: Viết test**: `test_chia_doi_sizes`, `test_chia_doi_uses_brand_yellow_in_label_area` (≥ 12% điểm ảnh vàng trong 30% dưới của bản 168 px), `test_chia_doi_without_left_image_splits_right_image`, `test_chia_doi_long_credit_stays_inside` (ghi công 200 ký tự → không có điểm ảnh sáng ngoài vùng 460 px góc trên phải), `test_khung_tu_video_returns_png`.
- [ ] **Step 2:** Chạy → FAIL; cài; `uv run pytest -q` xanh.
- [ ] **Step 3:** Cập nhật SKILL bước 6: phương án 2 = `chia_doi` với `trai` = chân dung từ `anh.pick` (có ghi công; không có thì `None`), `phai` = `khung_tu_video` của cảnh minh họa đẹp nhất; phương án 1 và 3 giữ nguyên.
- [ ] **Step 4: Kiểm thị giác** (D2): tạo 1 thumbnail mẫu cho video 1, gửi bạn duyệt; mở bản 168 px để chắc đọc ra chữ.
- [ ] **Step 5: Commit** `feat: thumbnail chia đôi theo khuôn kênh mẫu`.

### Task 15: Render song song theo chương (M, chỉ làm nếu Task 3 yêu cầu)

**Files:**
- Create: `pipeline/scripts/render-song-song.sh`
- Modify: `pipeline/tttc/dung.py` (thêm `chia_doan`), `pipeline/tests/test_dung.py`, `.claude/skills/video-dung/SKILL.md` (bước 4)

**Interfaces:**
- Produces: `dung.chia_doan(scenes: list[dict], so_doan: int) -> list[tuple[int, int]]` – các đoạn liền nhau phủ hết cảnh, ranh giới đặt ở cảnh `chuong` gần điểm chia đều nhất, mốc thời gian làm tròn về lưới 1/30 s. Script render từng đoạn bằng `compose(scene_range=…)`, chạy `N` tiến trình song song, nối hình bằng `ffmpeg -f concat -c copy`, rồi ghép tiếng đã trộn (`-map 0:v -map 1:a`).

- [ ] **Step 1: Viết test**: `test_chia_doan_covers_all_scenes_contiguously`, `test_chia_doan_boundaries_are_chapters`, `test_chia_doan_balanced_within_40_percent`.
- [ ] **Step 2:** Chạy → FAIL; cài; xanh.
- [ ] **Step 3:** Viết script; chạy trên `videos/thu-nghiem` với N = 2 và 3. Chấp nhận khi: tổng thời gian ngắn hơn bản tuần tự ≥ 30%, `dung.check_av` rỗng, số khung của video nối bằng số khung kỳ vọng ±2.
- [ ] **Step 4: Commit** `feat: render song song theo chương`.

### Task 16: Nghiệm thu trên video thật (L)

**Files:**
- Create: `docs/nghien-cuu/nghiem-thu-video-<n>.md`
- Modify: `theo-doi.csv` (sau khi đăng), tệp nhớ `pipeline-video-tu-dong.md`

- [ ] **Step 1:** Chọn đề cho video 3 hoặc 4 bằng `/video-moi` theo công thức tin nóng + góc Việt Nam (xem benchmark mục 1).
- [ ] **Step 2:** `/video-dung` toàn bộ; trước khi render chạy `uv run python -m tttc.chat_luong V` – phải **0 `Lỗi`**; ghi lại mọi `Cảnh báo` còn lại và lý do giữ.
- [ ] **Step 3 (bạn làm):** xem cạnh nhau với một video cùng độ dài của kênh mẫu, chấm 1–5 cho: nhịp hình, nhân vật/minh họa, âm thanh, thumbnail, kịch bản. **Đạt** khi trung bình ≥ 4 và không mục nào dưới 3. Không đạt → ghi mục thấp nhất vào backlog, không đăng.
- [ ] **Step 4:** Sau đăng: ghi view 24 giờ/7 ngày, CTR, giữ chân 30 giây vào `theo-doi.csv`; áp quy tắc 0,5x/3x trong `ke-hoach-nhan-ban-MotCongNghe.md` mục 7 sau ≥ 3 video theo chuẩn mới (đừng kết luận từ một video).
- [ ] **Step 5:** Cập nhật tệp nhớ pipeline; **Commit** `docs: nghiệm thu video theo chuẩn kênh mẫu`.

---

## Ngoài phạm vi đợt này

- Mẫu `ban-do` (cần khối bản đồ của HyperFrames registry), giọng phụ, nhân vật trong Shorts, đọc retention tự động, chạy theo lịch (hướng B).
- Dùng logo hãng và chân dung ngoài Commons: chỉ làm nếu bạn đổi D2/D3 sau khi tự cân nhắc rủi ro bản quyền.

## Rủi ro đã biết

- Render 12 phút chưa từng đo (spec ghi "1–2 giờ" là ước lượng). Mật độ cảnh mới có thể làm lâu hơn; Task 3 trả lời trước khi đầu tư các mẫu mới.
- Tôi có đủ SVG đẹp và đúng ý hay không chỉ biết sau khi xem ảnh tổng của Task 9; có thể cần vài vòng sửa.
- Thước đo lấy từ một video xem kỹ và ước lượng của công cụ; ngưỡng cần chỉnh sau 3 video thật.
- Kênh mẫu có thể đã bùng nhờ yếu tố ta không thấy được (thời điểm, quảng bá). Đạt thước đo không bảo đảm đạt view.
