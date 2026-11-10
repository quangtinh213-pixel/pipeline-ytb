# Chất lượng hình ảnh và bước đạo diễn Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Hình video sắc nét hơn về kỹ thuật và có ý đồ: cấu hình render đã thử và chọn, cảnh minh họa có phông theo chủ đề, bố cục tham số và camera, bước đạo diễn `dao-dien.json` sinh `canh.json`, chỉ số "độ khô", phụ đề chia theo nghĩa, kiểm tương phản.

**Architecture:** Mở rộng `chat_luong.py` (chỉ số `do_kho`), `canh.py` (`san_khau`, `bo_cuc`, `may_quay`, `cues` mới, cảnh báo nhãn dài), `dung.py` + `templates/canh/minh-hoa.html` + `dong.js` (phông, bố cục, camera, hạt nhiễu), `svg/ve.py` (6 phông), thêm `grain.py`, `tuong_phan.py`, `dao_dien.py`; thêm bước `dao-dien` vào sổ trạng thái và SKILL `video-dung`.

**Tech Stack:** Python ≥ 3.11, pytest (`uv run`), Pillow, HyperFrames 0.9.26 (`--video-bitrate`, `--crf`, `--max-bitrate`, `--keyframe-interval`), GSAP, ffmpeg.

**Spec:** `docs/superpowers/specs/2026-11-09-chat-luong-hinh-anh-design.md`

**Thứ tự thực hiện:** sau kế hoạch giọng văn, kế hoạch vận hành, và **Task 1–6 của kế hoạch nhận diện** (lớp màu); Task 7 dưới đây (6 phông SVG) phải đợi lớp màu để khỏi ghi cứng màu. Task 10 sửa `STEPS` sau khi hai kế hoạch trước đã sửa.

## Global Constraints

- Chỉ số độ khô (cảnh báo, hiệu chỉnh sau chạy khô): số phông khác nhau ≥ 5; không quá 2 cảnh liền cùng phông; không lặp cùng hình chính trong cửa sổ 8 cảnh liền (cảnh `minh-hoa`); 100% cảnh trọng điểm có `an_du` và (nếu là `minh-hoa`) `may_quay`; ≥ 20% số cảnh có chuyển động camera; bản đồ nhịp cảm xúc có đủ `mo`, `dinh`, `dao-chieu`, `chot`; giám khảo: không beat nào dưới 3 ở bất kỳ tiêu chí và trung bình từ 4.
- Cảnh trọng điểm khoảng 30% số cảnh; bước đạo diễn giới hạn khoảng 45 phút, chia theo beat cho subagent chạy song song; vượt thì giảm tỉ lệ cảnh trọng điểm (~20%), không bỏ bước. Đây là số đề xuất.
- `may_quay` ∈ {`dung`, `day-vao`, `keo-ra`, `lia`, `he-lo`}; `nhip_cam_xuc` ∈ {`mo`, `leo`, `dinh`, `dao-chieu`, `ha`, `chot`}; `san_khau` mặc định `nen-dat`, thêm phông bằng cách thêm `svg/phong-<tên>.svg`.
- Ẩn dụ hình không được thêm khẳng định không có nguồn; mọi số trên màn hình vẫn có `nguon_id`.
- Cấu hình render đề xuất để thử: `--video-bitrate 8M --max-bitrate 12M --keyframe-interval 2` (8 Mbps là khuyến nghị YouTube theo hiểu biết của tôi, chưa kiểm lại); chọn theo kết quả thử, không theo số này.
- Tương phản chữ/nền ≥ 4,5:1. Không đổi phong cách isometric.
- Chạy lệnh trong `pipeline/`. Chỉ `git add` đường dẫn cụ thể.

## Review Focus

1. Video cũ không có `dao-dien.json` hay `san_khau`: `chat_luong`, `duyet`, `compose` vẫn chạy, chỉ số tính được từ `canh.json` (Task 1, 6, 10).
2. `canh.json` có cả `phu` lẫn `bo_cuc`, `san_khau` lạ, `may_quay` lạ, `bo_cuc` quá 4 phần tử hoặc tọa độ ngoài 0–1 → `Lỗi:` rõ (Task 6).
3. `dao-dien.json` thiếu cảnh so với `canh-khung.json`, cảnh trọng điểm thiếu `an_du`, hình trong `vat_chinh` chưa vẽ → báo rõ, không sinh `canh.json` hỏng (Task 9).
4. Phụ đề: câu quá dài, từ dài hơn `max_chars`, nhóm cuối chỉ một từ không được tạo ra dòng mồ côi (Task 2).
5. Render với `HF_RENDER_ARGS` rỗng giữ nguyên hành vi cũ; cổng `hyperframes check` vẫn chặn (Task 5).

---

### Task 0: Nền sạch

- [ ] **Step 1:** `uv run pytest -q`. Expected: PASS toàn bộ (ghi số test).
- [ ] **Step 2:** `git status --short -- pipeline/tttc/dung.py pipeline/tttc/canh.py pipeline/templates/canh pipeline/scripts/render.sh pipeline/tests/test_render_gate.py`. Các tệp `M` hoặc `??` là thay đổi cũ chưa commit (gồm `render.sh`, `test_render_gate.py`). **Dừng và hỏi người dùng** commit riêng hoặc stash trước khi sửa.

### Task 1: Chỉ số "độ khô" trong `chat_luong`

**Files:** Modify `pipeline/tttc/chat_luong.py`, `pipeline/tttc/duyet.py:73-74`; Test `pipeline/tests/test_chat_luong.py`, `tests/test_duyet.py`; Create `docs/nghien-cuu/do-kho-nen-2026-11-09.md`.

**Interfaces:**
- Produces:
  - `chat_luong.do_kho(canh: dict, dao_dien: dict | None = None, cham: dict | None = None) -> dict` với khóa: `so_phong` (số `san_khau` khác nhau trong các cảnh `minh-hoa`, thiếu thì tính `nen-dat`), `phong_lien_max` (dãy dài nhất cảnh `minh-hoa` liền nhau cùng `san_khau`), `vat_chinh_lap` (số cảnh `minh-hoa` có `svg` đã xuất hiện trong 7 cảnh `minh-hoa` ngay trước), `ti_le_may_quay` (tỉ lệ cảnh có `may_quay` khác `""`/`dung`). Có `dao_dien` (`{"scenes": [{"id","trong_diem","an_du","may_quay","nhip_cam_xuc",...}]}`) thêm `trong_diem_thieu` (cảnh trọng điểm thiếu `an_du`, hoặc thiếu `may_quay` khi cảnh là `minh-hoa` trong `canh`) và `nhip_cam_xuc_du` (bool). Có `cham` (`{"beats": [{"y_nghia","da_dang","chieu_sau","nhip"}]}` điểm 1–5) thêm `cham_thap` (số beat có tiêu chí < 3) và `cham_tb` (trung bình mọi điểm).
  - `MUC_TIEU["do_kho"] = {"phong_min": 5, "phong_lien_max": 2, "lap_max": 0, "may_quay_min": 0.20, "cham_min": 3, "cham_tb_min": 4.0}`.
  - `do(canh, timing, dao_dien=None, cham=None)` thêm khóa `"do_kho"`; `kiem(so_do, muc)` thêm thông báo bắt đầu `Cảnh báo: độ khô:` cho mỗi chỉ số vi phạm; `main` đọc `dao-dien.json` và `dao-dien-cham.json` nếu có.

- [ ] **Step 1: Viết test**

```python
def _mh(i, svg, sk="nen-dat", mq=""):
    return {"id": f"c{i}", "mau": "minh-hoa", "start": i * 3.0, "end": i * 3.0 + 3.0, "svg": svg, "san_khau": sk, "may_quay": mq}

def test_do_kho_counts_stages_runs_repeats_and_camera():
    sc = [_mh(0, "chip"), _mh(1, "laptop", "may-chu", "day-vao"), _mh(2, "chip", "may-chu"), _mh(3, "tien", "may-chu")]
    d = chat_luong.do_kho({"scenes": sc})
    assert d["so_phong"] == 2 and d["phong_lien_max"] == 3 and d["vat_chinh_lap"] == 1 and d["ti_le_may_quay"] == 0.25

def test_do_kho_defaults_missing_stage_to_nen_dat():
    assert chat_luong.do_kho({"scenes": [_mh(0, "chip"), _mh(1, "laptop")]})["so_phong"] == 1

def test_do_kho_reads_director_and_judge():
    dd = {"scenes": [{"id": "c0", "trong_diem": True, "an_du": "", "may_quay": "", "nhip_cam_xuc": "mo"},
                     {"id": "c1", "trong_diem": True, "an_du": "cái cân", "may_quay": "day-vao", "nhip_cam_xuc": "chot"}]}
    cham = {"beats": [{"y_nghia": 4, "da_dang": 2, "chieu_sau": 4, "nhip": 4}]}
    d = chat_luong.do_kho({"scenes": [_mh(0, "chip"), _mh(1, "laptop")]}, dd, cham)
    assert d["trong_diem_thieu"] == 1 and d["nhip_cam_xuc_du"] is False
    assert d["cham_thap"] == 1 and d["cham_tb"] == 3.5

def test_kiem_warns_on_each_violated_do_kho_metric():
    so_do = {**_ok_base(), "do_kho": {"so_phong": 1, "phong_lien_max": 5, "vat_chinh_lap": 2, "ti_le_may_quay": 0.0}}
    msgs = chat_luong.kiem(so_do)
    assert sum(m.startswith("Cảnh báo: độ khô:") for m in msgs) == 4

def test_old_callers_without_director_files_still_work():
    assert "do_kho" in chat_luong.do({"scenes": [_mh(0, "chip")]}, {"words": [], "duration": 3.0})
```
(`_ok_base()` là dict `so_do` hợp lệ lấy từ các test hiện có trong `test_chat_luong.py`.) Thêm test trong `test_duyet.py`: `render_review_2` hiện thông báo "độ khô" khi `canh.json` chỉ có một phông.

- [ ] **Step 2:** `uv run pytest tests/test_chat_luong.py tests/test_duyet.py -q`. Expected: FAIL.
- [ ] **Step 3:** Implement. `duyet.render_review_2` đọc thêm `dao-dien.json`, `dao-dien-cham.json` nếu tồn tại và truyền vào `chat_luong.do`.
- [ ] **Step 4:** `uv run pytest -q`. Expected: PASS.
- [ ] **Step 5: Đo mốc nền.** `uv run python -m tttc.chat_luong ../videos/2026-11-15-nvidia-siet-chip` và `../videos/2026-11-13-goi-ai-dang-tien`; ghi các khóa `do_kho` vào `docs/nghien-cuu/do-kho-nen-2026-11-09.md` (dự kiến `so_phong` = 1). Số này là mốc trước khi có phông mới.
- [ ] **Step 6: Commit**

```bash
git add pipeline/tttc/chat_luong.py pipeline/tttc/duyet.py pipeline/tests docs/nghien-cuu/do-kho-nen-2026-11-09.md
git commit -m "feat: chỉ số độ khô (phông, hình chính lặp, camera, trọng điểm, giám khảo) trong chat_luong"
```

### Task 2: Phụ đề chia theo nghĩa

**Files:** Modify `pipeline/tttc/canh.py:200-213` (`cues`); Test `pipeline/tests/test_canh.py`.

**Interfaces:** `cues(timing: dict, max_chars: int = 42) -> list[tuple[float, float, str]]` giữ chữ ký. Luật mới: ngắt bắt buộc sau `.!?`; khi dòng hiện tại đã ≥ 60% `max_chars` thì ưu tiên ngắt sau `,;:` hoặc sau từ kết thúc bằng dấu đó; khi buộc phải ngắt vì vượt `max_chars`, lùi điểm ngắt về dấu `,;:` gần nhất trong dòng nếu có, và không để nhóm nào chỉ có một từ (trừ khi cả câu một từ); `max_chars` vẫn là giới hạn cứng, trừ một từ dài hơn nó.

- [ ] **Step 1: Viết test**

```python
def W(text):
    ws = text.split()
    return {"words": [{"w": w, "start": i * 0.5, "end": i * 0.5 + 0.4} for i, w in enumerate(ws)], "duration": len(ws) * 0.5}

def test_cues_break_at_comma_before_mid_phrase():
    out = [c[2] for c in canh.cues(W("Nhiều người nghe tin đó và hỏi, tới lượt Việt Nam chưa?"), 30)]
    assert out == ["Nhiều người nghe tin đó và hỏi,", "tới lượt Việt Nam chưa?"]

def test_cues_never_leave_single_word_orphan():
    out = [c[2] for c in canh.cues(W("a b c d e f g h i j k l m n o p q"), 10)]
    assert all(len(x.split()) >= 2 for x in out) and "".join(out).replace(" ", "") == "abcdefghijklmnopq"

def test_cues_respect_max_chars_and_sentence_end():
    out = [c[2] for c in canh.cues(W("Một hai ba bốn năm. Sáu bảy tám chín mười mười một."), 20)]
    assert out[0].endswith("năm.") and all(len(x) <= 20 for x in out)

def test_cues_timing_covers_words():
    t = W("Xin chào các bạn, mình là người kể chuyện.")
    out = canh.cues(t, 20)
    assert out[0][0] == t["words"][0]["start"] and out[-1][1] == t["words"][-1]["end"]
```
Các test `cues`/`to_srt` hiện có phải vẫn PASS (nếu một test cũ khẳng định ngắt giữa cụm, sửa kỳ vọng và ghi lý do trong commit).

- [ ] **Step 2:** `uv run pytest tests/test_canh.py -q`. Expected: FAIL.
- [ ] **Step 3:** Implement. Chạy `uv run pytest -q`. Expected: PASS. Chạy `uv run python -m tttc.canh ../videos/2026-11-15-nvidia-siet-chip` và xem 20 dòng đầu `phu-de.srt` mới (tệp tạm: ghi sang thư mục thử, không đè video đã đăng).
- [ ] **Step 4: Commit** `git add pipeline/tttc/canh.py pipeline/tests/test_canh.py && git commit -m "feat: phụ đề ngắt theo nghĩa, không dòng mồ côi"`.

### Task 3: Kiểm tương phản phụ đề từ khung hình

**Files:** Create `pipeline/tttc/tuong_phan.py`, `pipeline/tests/test_tuong_phan.py`

**Interfaces:**
- Produces: `ti_le(png: Path, vung: tuple[int, int, int, int]) -> float` = tỉ lệ tương phản WCAG giữa độ sáng phân vị 95 và phân vị 5 trong vùng `(x0, y0, x1, y1)`; `kiem_phu_de(video_mp4: Path, canh: dict, nguong: float = 4.5, vung: tuple = (210, 960, 1710, 1044), run=subprocess.run) -> list[str]`: với mỗi cảnh lấy một khung giữa cảnh bằng `ffmpeg`, nếu `ti_le` < `nguong` thêm `Cảnh báo: cảnh {id} phụ đề khó đọc (tương phản {x:.1f}:1)`. Dòng lệnh `python -m tttc.tuong_phan <thư mục video>` đọc `final.mp4`, `canh.json`, in thông báo.

- [ ] **Step 1: Viết test** với PNG tổng hợp: nền đen chữ trắng → `ti_le` > 7; xám nhạt trên xám nhạt (200 và 210) → < 1,2; `kiem_phu_de` với `run` giả ghi sẵn hai PNG (một đạt, một không) cho hai cảnh trả đúng một thông báo chứa id cảnh thứ hai.
- [ ] **Step 2:** `uv run pytest tests/test_tuong_phan.py -q`. Expected: FAIL. Implement (`Pillow` đọc ảnh xám, `numpy` không có sẵn thì dùng `sorted` trên danh sách điểm ảnh). Expected sau đó: PASS.
- [ ] **Step 3:** Chạy thật trên `final.mp4` của video nvidia (ghi kết quả vào `docs/nghien-cuu/do-kho-nen-2026-11-09.md`).
- [ ] **Step 4: Commit** `git add pipeline/tttc/tuong_phan.py pipeline/tests/test_tuong_phan.py docs/nghien-cuu && git commit -m "feat: kiểm tương phản phụ đề từ khung hình đã render"`.

### Task 4: Điều tra dòng mờ giây 290 và chữ tràn

**Files:** Create `docs/nghien-cuu/dong-mo-giay-290-2026-11-09.md`; Modify `pipeline/tttc/canh.py` (cảnh báo nhãn dài), `pipeline/tests/test_canh.py`.

**Interfaces:** `canh.validate` thêm `Cảnh báo: {id} nhãn dài {n} từ (≤ 5)` cho mọi cảnh có trường `nhan` quá 5 từ (mẫu `minh-hoa`, `so-lon`, `so-sanh` mỗi bên, `quy-trinh` mỗi bước).

- [ ] **Step 1: Điều tra.** Tìm cảnh chứa giây 290 của `videos/2026-11-15-nvidia-siet-chip/canh.json`; `dung.compose(video, scene_range=(i - 1, i + 2), out="thu-290")` rồi `scripts/render.sh .../thu-290 .../thu-290.mp4 draft`; trích khung mỗi 0,25 giây quanh cảnh bằng `ffmpeg` và ghép bảng soi. Đọc `templates/canh/so-lon.html` tìm hiệu ứng `blur` của dòng phụ. Ghi vào tài liệu: dòng mờ kéo dài bao lâu, là hiệu ứng hiện dần hay lỗi. **Quy tắc:** nếu mờ quá 1,0 s trên thông tin chính thì rút hiệu ứng còn ≤ 0,4 s trong mẫu; đã đúng ý đồ thì ghi "không sửa".
- [ ] **Step 2: Kiểm tràn.** Dựng cảnh thử có `nhan` 12 từ, chạy `npx hyperframes check` (qua `render.sh`) và ghi `check` có bắt được không. Dù bắt được hay không, thêm cảnh báo nhãn dài ở `validate`.
- [ ] **Step 3: Viết test**

```python
def test_long_label_warns_over_five_words():
    sc = {"scenes": [{"id": "c1", "mau": "minh-hoa", "start": 0, "end": 3, "svg": "chip", "nhan": "một hai ba bốn năm sáu"}]}
    out = canh.validate(sc, {"duration": 3.0, "words": []})
    assert any(m.startswith("Cảnh báo: c1 nhãn dài 6 từ") for m in out)
    sc["scenes"][0]["nhan"] = "một hai ba bốn năm"
    assert not any("nhãn dài" in m for m in canh.validate(sc, {"duration": 3.0, "words": []}))
```
- [ ] **Step 4:** `uv run pytest tests/test_canh.py -q`. Expected: FAIL rồi PASS sau khi implement; `uv run pytest -q` PASS.
- [ ] **Step 5: Commit** `git add pipeline/tttc/canh.py pipeline/tests/test_canh.py docs/nghien-cuu/dong-mo-giay-290-2026-11-09.md && git commit -m "feat: cảnh báo nhãn dài; ghi kết quả điều tra dòng mờ"` (kèm `pipeline/templates/canh/so-lon.html` nếu có sửa).

### Task 5: Độ nét kỹ thuật — hạt nhiễu, tham số render, thử 4 cấu hình

**Files:** Create `pipeline/tttc/grain.py`, `pipeline/tests/test_grain.py`, `docs/nghien-cuu/cau-hinh-render-2026-11-09.md`; Modify `pipeline/tttc/dung.py` (`render_args`, hạt nhiễu trong `compose`), `pipeline/scripts/render.sh`, `pipeline/config.json`, `pipeline/tests/test_dung.py`, `pipeline/tests/test_render_gate.py`.

**Interfaces:**
- Produces: `grain.tao_grain(out: Path, size: int = 256, seed: int = 7) -> Path` ghi PNG xám ngẫu nhiên xác định theo `seed`. `dung.render_args(cfg: dict | None = None) -> list[str]` từ `config.json["render"]` = `{"bitrate": "8M" | null, "max_bitrate": "12M" | null, "keyframe": 2 | null, "grain": 0.0}` → `["--video-bitrate", b, "--max-bitrate", m, "--keyframe-interval", str(k)]` chỉ gồm các khóa có giá trị; `python -m tttc.dung render-args` in chúng. `compose`: khi `render.grain` > 0 chép `grain.png` vào `assets/` và thêm CSS `#root::after { content: ""; position: absolute; inset: 0; background: url(assets/grain.png); opacity: <grain>; pointer-events: none; z-index: 9; }`. `render.sh` thêm `${HF_RENDER_ARGS-$(…render-args)}` vào lệnh `hyperframes render`; biến môi trường `HF_RENDER_ARGS` (kể cả rỗng) thắng cấu hình.

- [ ] **Step 1: Viết test**

```python
def test_grain_is_deterministic_and_seed_dependent(tmp_path):
    a = grain.tao_grain(tmp_path / "a.png", 64, 7).read_bytes()
    assert a == grain.tao_grain(tmp_path / "b.png", 64, 7).read_bytes()
    assert a != grain.tao_grain(tmp_path / "c.png", 64, 8).read_bytes()
    assert Image.open(tmp_path / "a.png").size == (64, 64)

def test_render_args_only_includes_set_keys():
    assert dung.render_args({"bitrate": "8M", "max_bitrate": "12M", "keyframe": 2, "grain": 0}) == \
        ["--video-bitrate", "8M", "--max-bitrate", "12M", "--keyframe-interval", "2"]
    assert dung.render_args({}) == [] and dung.render_args({"bitrate": "8M"}) == ["--video-bitrate", "8M"]

def test_compose_adds_grain_overlay_only_when_enabled(video, monkeypatch):
    monkeypatch.setattr(dung, "_render_cfg", lambda: {"grain": 0.02})
    out = dung.compose(video)
    assert (out / "assets" / "grain.png").exists() and "assets/grain.png" in (out / "index.html").read_text(encoding="utf-8")
    monkeypatch.setattr(dung, "_render_cfg", lambda: {})
    assert not (dung.compose(video) / "assets" / "grain.png").exists()
```
Trong `test_render_gate.py` đổi `FAKE_NPX` để ghi tham số (`echo "render $*" >> "$FAKE_LOG"`), thêm test: đặt `HF_RENDER_ARGS="--video-bitrate 8M"` thì dòng log chứa `--video-bitrate 8M`; `HF_RENDER_ARGS=""` thì không chứa `--video-bitrate`.

- [ ] **Step 2:** `uv run pytest tests/test_grain.py tests/test_dung.py tests/test_render_gate.py -q`. Expected: FAIL.
- [ ] **Step 3:** Implement; `dung._render_cfg() -> dict` đọc `config.json["render"]` (trả `{}` nếu thiếu). Chạy `uv run pytest -q`. Expected: PASS.
- [ ] **Step 4 (thí nghiệm, cần bạn xem):** Chọn đoạn 2–3 phút nhiều gradient và chữ nhỏ của video nvidia. Dựng và render bốn cấu hình: (1) hiện tại; (2) `bitrate 8M`, `max_bitrate 12M`, `keyframe 2`; (3) như 2 cộng `grain 0.02`; (4) như 3 render 1440p (`compose(..., w=2560, h=1440)`). Ghi cho mỗi bản thời gian render, kích thước. **Bạn** tải bốn tệp lên YouTube riêng tư và xem ở 1080p, so banding, độ rõ chữ nhỏ, đường viền; ghi lựa chọn và lý do vào `docs/nghien-cuu/cau-hinh-render-2026-11-09.md`, đặt `config.json["render"]` theo cấu hình rẻ nhất mà banding hết.
- [ ] **Step 5: Commit**

```bash
git add pipeline/tttc/grain.py pipeline/tttc/dung.py pipeline/scripts/render.sh pipeline/config.json pipeline/tests docs/nghien-cuu/cau-hinh-render-2026-11-09.md
git commit -m "feat: tham số render và hạt nhiễu chống banding, chọn cấu hình bằng thử nghiệm"
```

### Task 6: `minh-hoa` có `san_khau`, `bo_cuc`, `may_quay`

**Files:** Modify `pipeline/tttc/canh.py` (hằng số và kiểm), `pipeline/tttc/dung.py:93-97,265`, `pipeline/templates/canh/minh-hoa.html`, docstring đầu `dung.py`; Test `pipeline/tests/test_canh.py`, `tests/test_dung.py`.

**Interfaces:**
- Produces (`canh.py`): `MAY_QUAY = {"", "dung", "day-vao", "keo-ra", "lia", "he-lo"}`; `san_khau_hop_le(svg_dir: Path = SVG_DIR) -> set[str]` = `{"nen-dat"}` cộng phần sau `phong-` của mọi tệp `phong-*.svg`. Kiểm trong `validate` cho cảnh `minh-hoa`: `san_khau` ∈ tập hợp lệ; `may_quay` ∈ `MAY_QUAY`; `bo_cuc` là danh sách 1–4 phần tử `{svg, x, y, to}` với `svg` có trong thư viện, `x`,`y` ∈ [0,1], `to` ∈ [0,2; 1,5]; không dùng đồng thời `phu` và `bo_cuc`. Thông báo `Lỗi:` nêu id cảnh và trường.
- `dung._vars` cho `minh-hoa` thêm: `phong` (`assets/svg/nen-dat.svg` nếu `san_khau` là `nen-dat`/thiếu, ngược lại `assets/svg/phong-<tên>.svg`), `bo_cuc` (JSON, mỗi phần tử có `svg` đổi thành `assets/svg/<tên>.svg`), `may_quay` (mặc định `"dung"`), `thoi_luong` (`end − start`, làm tròn 3 chữ số).
- Template `minh-hoa.html`: thêm bốn biến vào `data-composition-variables`; `#mh-dat img` lấy `phong` (`data-var-src`); khi `bo_cuc` khác `[]` ẩn `#mh-phu-1/2` và dựng đạo cụ từ `bo_cuc` trong `#mh-the-gioi` (vị trí theo tỉ lệ vùng sàn 1100×1100 tại (410,100), cỡ `to` × 230 px, cùng kiểu xuất hiện `back.out` như phụ cũ); mốc xuất hiện lấy từ `nhip[1..]` như phụ cũ, thiếu thì 0,5 + 0,08 × thứ tự.

- [ ] **Step 1: Viết test**

```python
def _mh(**kw): return {"scenes": [{"id": "c1", "mau": "minh-hoa", "start": 0, "end": 4, "svg": "chip", **kw}]}
T = {"duration": 4.0, "words": []}

def test_validate_rejects_unknown_stage_camera_and_bad_layout(tmp_path):
    for f in ("nen-dat", "phong-may-chu", "chip", "cay"):
        (tmp_path / f"{f}.svg").write_text("<svg/>")
    ok = canh.validate(_mh(san_khau="may-chu", may_quay="day-vao",
                           bo_cuc=[{"svg": "cay", "x": 0.2, "y": 0.6, "to": 1.0}]), T, tmp_path)
    assert [m for m in ok if m.startswith("Lỗi")] == []
    assert any("san_khau" in m for m in canh.validate(_mh(san_khau="mars"), T, tmp_path))
    assert any("may_quay" in m for m in canh.validate(_mh(may_quay="xoay-tit"), T, tmp_path))
    assert any("bo_cuc" in m for m in canh.validate(_mh(bo_cuc=[{"svg": "cay", "x": 1.5, "y": 0.5, "to": 1}]), T, tmp_path))
    assert any("bo_cuc" in m for m in canh.validate(_mh(bo_cuc=[{"svg": "cay", "x": .5, "y": .5, "to": 1}] * 5), T, tmp_path))
    assert any("phu" in m and "bo_cuc" in m for m in canh.validate(_mh(phu=["cay"], bo_cuc=[{"svg": "cay", "x": .5, "y": .5, "to": 1}]), T, tmp_path))
```
Trong `test_dung.py`: cảnh `minh-hoa` có `san_khau: "may-chu"`, `bo_cuc` 2 phần tử, `may_quay: "day-vao"` → `compositions/c2.html` tồn tại và `index.html` có `assets/svg/phong-may-chu.svg`, `"may_quay": "day-vao"`, `"thoi_luong": 5.0` trong `data-variable-values`; cảnh cũ (không có trường mới) cho `assets/svg/nen-dat.svg` và `"may_quay": "dung"`.

- [ ] **Step 2:** `uv run pytest tests/test_canh.py tests/test_dung.py -q`. Expected: FAIL.
- [ ] **Step 3:** Implement. Thêm `phong-may-chu.svg` giả (`<svg/>`) chỉ trong `tmp_path` của test; thư viện thật lấy phông ở Task 7. Cập nhật docstring `dung.py` mục `minh-hoa`.
- [ ] **Step 4:** `uv run pytest -q`. Expected: PASS, `test_dac_trung`/golden (nếu đã có từ kế hoạch nhận diện) không đổi với cảnh cũ.
- [ ] **Step 5: Commit** `git add pipeline/tttc pipeline/templates/canh/minh-hoa.html pipeline/tests && git commit -m "feat: minh-hoa nhận san_khau, bo_cuc, may_quay"`.

### Task 7: Sáu phông SVG theo chủ đề

**Files:** Modify `pipeline/svg/ve.py` (6 hàm + `ITEMS`), `pipeline/svg/README.md`, `pipeline/tests/test_svg.py`.

**Interfaces:** Thêm vào `ITEMS`: `phong-may-chu`, `phong-nha-may`, `phong-cang`, `phong-thanh-pho`, `phong-san-giao-dich`, `phong-co-quan`. Mỗi phông gồm **đúng các đa giác của `nen_dat()`** (cùng tấm sàn, nên cùng `viewBox`) cộng chi tiết đặt ở **rìa sàn**, chừa trống vùng giữa cho vật chính: dãy tủ máy chủ và dây cáp thấp; dải băng chuyền và nhà xưởng thấp; chồng container và chân cần cẩu; khối nhà thấp quanh rìa; sàn có dải bảng giá (thanh màu, không chữ) và màn hình; cột trụ, bậc thềm, chân cột cờ. Chỉ dùng màu theme và màu ngoại lệ đã có của `nen-dat`; không chữ, không logo.

- [ ] **Step 1: Viết test** (trong `test_svg.py`): với mỗi tệp `phong-*.svg`: `viewBox` bằng đúng `viewBox` của `nen-dat.svg`; kích thước ≤ 40.000 byte (quy tắc 20 KB chỉ áp cho hình khác); không `<text`; màu ⊆ `BRAND | EXTRA["nen-dat"]`; có ≥ 6 phông: `len(list(SVG_DIR.glob("phong-*.svg"))) >= 6`.
- [ ] **Step 2:** `uv run pytest tests/test_svg.py -q`. Expected: FAIL.
- [ ] **Step 3:** Vẽ sáu hàm theo `svg/README.md`, thêm vào `ITEMS`, chạy `uv run python svg/ve.py` rồi `uv run python -m tttc.theme ap-dung` (nếu kế hoạch nhận diện đã xong) hoặc `uv run python svg/sheet.py`. Xem `svg/thu-vien.png`: mỗi phông nhận ra chủ đề, vùng giữa trống.
- [ ] **Step 4:** `uv run pytest -q`. Expected: PASS. Cập nhật `README.md` (nhóm "Phông" và quy tắc ≤ 40 KB cho `phong-*`).
- [ ] **Step 5: Commit** `git add pipeline/svg pipeline/tests/test_svg.py && git commit -m "feat: sáu phông theo chủ đề cho minh-hoa"`.

### Task 8: Camera trong `dong.js` và `minh-hoa`

**Files:** Modify `pipeline/templates/canh/dong.js`, `pipeline/templates/canh/minh-hoa.html`; Test `pipeline/tests/test_dung.py`.

**Interfaces:** `mayQuay(tl, sel, kieu, t0, dur)` trong `dong.js`: `kieu` ∈ {`day-vao`, `keo-ra`, `lia`, `he-lo`} thêm tween lên `sel` trong `[t0, t0 + dur]` (`scale` trong 1,0–1,3, dịch ngang ≤ 80 px, `ease: "none"` hoặc `sine.inOut`); `""`/`"dung"` không làm gì. `he-lo` bắt đầu phóng 1,35 quanh vật chính rồi kéo ra ở 40% thời lượng. Template gọi `mayQuay(tl, "#mh-the-gioi", v.may_quay, 0.4, parseFloat(v.thoi_luong) - 0.4)` sau các tween vào cảnh.

- [ ] **Step 1: Viết test**

```python
def test_dong_js_defines_camera_for_every_kind():
    js = (dung.TPL / "dong.js").read_text(encoding="utf-8")
    assert "function mayQuay(" in js
    for kieu in ("day-vao", "keo-ra", "lia", "he-lo"):
        assert f'"{kieu}"' in js

def test_minh_hoa_template_calls_camera_on_the_world():
    html = (dung.TPL / "minh-hoa.html").read_text(encoding="utf-8")
    assert 'mayQuay(tl, "#mh-the-gioi", v.may_quay' in html
```
- [ ] **Step 2:** `uv run pytest tests/test_dung.py -q`. Expected: FAIL. Implement. Expected: PASS.
- [ ] **Step 3 (xem ảnh):** Dựng 4 cảnh `minh-hoa` (mỗi cảnh một `may_quay` khác nhau trên phông `may-chu`), render `draft`, trích khung ở 0,8 s và `thoi_luong − 0,3` s: xác nhận cảnh `day-vao` và `keo-ra` đổi tỉ lệ, `lia` đổi vị trí ngang, `dung` đứng yên (ngoài chuyển động lặp). Ghi nhận xét vào commit.
- [ ] **Step 4: Commit** `git add pipeline/templates/canh pipeline/tests/test_dung.py && git commit -m "feat: camera đẩy vào, kéo ra, lia, hé lộ cho minh-hoa"`.

### Task 9: `tttc/dao_dien.py`

**Files:** Create `pipeline/tttc/dao_dien.py`, `pipeline/tests/test_dao_dien.py`

**Interfaces:**
- Consumes: `canh.MAU`, `canh.MAY_QUAY`, `canh.san_khau_hop_le`, `canh.phrase_time`, `dung.DEFAULT_STEPS`.
- Produces:
  - `NHIP_CAM_XUC = {"mo","leo","dinh","dao-chieu","ha","chot"}`; `SLOT = [(0.2, 0.62), (0.8, 0.66), (0.24, 0.3), (0.76, 0.3)]` (vị trí đạo cụ theo thứ tự).
  - Định dạng `dao-dien.json`: `{"scenes": [{"id","y","nhip_cam_xuc","trong_diem","an_du"?,"san_khau"?,"vat_chinh"?,"dao_cu"? [≤ 4 tên],"may_quay"?,"am_thanh"?,"dan"? {the,huong?,goc?,tu?},"canh": {"mau": ..., ...trường của mẫu}}]}`.
  - `validate(dd: dict, khung: dict, svg_dir: Path = SVG_DIR) -> list[str]`: `Lỗi:` khi id/thứ tự cảnh không khớp `khung["scenes"]`, thiếu `y`, `nhip_cam_xuc` ngoài tập, `trong_diem` không phải bool, `canh.mau` ngoài `MAU`, `san_khau` hoặc `may_quay` không hợp lệ, cảnh `trong_diem` thiếu `an_du`, cảnh trọng điểm `minh-hoa` thiếu `may_quay` khác `dung`; `Cảnh báo:` khi `vat_chinh`/`dao_cu` chưa có trong thư viện.
  - `hinh_thieu(dd: dict, svg_dir: Path = SVG_DIR) -> list[str]` tên hình chưa vẽ, không trùng, sắp xếp.
  - `sinh_canh(dd: dict, khung: dict, timing: dict) -> dict`: mỗi cảnh = `{"id","start","end"}` từ `khung` + các trường của `canh`; với `minh-hoa`: `svg` = `vat_chinh` (nếu `canh` chưa có), `san_khau`, `may_quay`, `bo_cuc` dựng từ `dao_cu` theo `SLOT` (`to` = 1.0); `dan` chép sang; `nhip` nếu `canh` chưa có và mẫu có `n = len(DEFAULT_STEPS[mau]) > 0`: phần tử k là cụm 3 từ của lời đọc cảnh bắt đầu ở vị trí `round((k + 1) × số_từ / (n + 1))` (cụm luôn có trong lời đọc nên `phrase_time` ≠ None).
  - `main(video_dir: str) -> int`: đọc `dao-dien.json`, `canh-khung.json`, `giong-timing.json`; có `Lỗi:` thì in và trả 1; ngược lại sao lưu `canh.json` thành `canh-truoc-dao-dien.json` (nếu có), ghi `canh.json`, `hinh-thieu.json`, in số cảnh, tỉ lệ cảnh trọng điểm, danh sách hình thiếu; trả 0.

- [ ] **Step 1: Viết test**

```python
KHUNG = {"scenes": [{"id": "c1", "start": 0.0, "end": 4.0, "loi": "một hai ba bốn năm sáu bảy tám chín mười"},
                    {"id": "c2", "start": 4.0, "end": 8.0, "loi": "a b c d e f g h"}]}
TIMING = {"duration": 8.0, "words": [{"w": w, "start": i * 0.4, "end": i * 0.4 + 0.3}
                                     for i, w in enumerate((KHUNG["scenes"][0]["loi"] + " " + KHUNG["scenes"][1]["loi"]).split())]}
def _dd(**over):
    s1 = {"id": "c1", "y": "mở", "nhip_cam_xuc": "mo", "trong_diem": True, "an_du": "cái cân", "san_khau": "nen-dat",
          "vat_chinh": "chip", "dao_cu": ["cay", "dong-xu"], "may_quay": "day-vao",
          "canh": {"mau": "minh-hoa", "nhan": "Chip"}}
    s2 = {"id": "c2", "y": "chốt", "nhip_cam_xuc": "chot", "trong_diem": False,
          "canh": {"mau": "so-lon", "so": 5, "nhan": "X", "nguon_id": "p1"}}
    return {"scenes": [{**s1, **over.get("s1", {})}, {**s2, **over.get("s2", {})}]}

def test_validate_clean_director_file(svg_dir):
    assert [m for m in dao_dien.validate(_dd(), KHUNG, svg_dir) if m.startswith("Lỗi")] == []

@pytest.mark.parametrize("over,key", [
    ({"s1": {"y": ""}}, "y"), ({"s1": {"an_du": ""}}, "an_du"), ({"s1": {"may_quay": "dung"}}, "may_quay"),
    ({"s1": {"nhip_cam_xuc": "la"}}, "nhip_cam_xuc"), ({"s1": {"san_khau": "mars"}}, "san_khau"),
    ({"s2": {"canh": {"mau": "khong-co"}}}, "mau")])
def test_validate_flags_each_director_rule(over, key, svg_dir):
    assert any(m.startswith("Lỗi") and key in m for m in dao_dien.validate(_dd(**over), KHUNG, svg_dir))

def test_validate_flags_missing_scene_and_warns_on_undrawn_prop(svg_dir):
    dd = _dd(); dd["scenes"].pop()
    assert any("c2" in m and m.startswith("Lỗi") for m in dao_dien.validate(dd, KHUNG, svg_dir))
    assert any(m.startswith("Cảnh báo") and "chua-ve" in m for m in dao_dien.validate(_dd(s1={"dao_cu": ["chua-ve"]}), KHUNG, svg_dir))
    assert dao_dien.hinh_thieu(_dd(s1={"dao_cu": ["chua-ve", "chua-ve"]}), svg_dir) == ["chua-ve"]

def test_sinh_canh_keeps_timing_contiguous_and_builds_layout_and_nhip(svg_dir):
    out = dao_dien.sinh_canh(_dd(), KHUNG, TIMING)["scenes"]
    assert [(s["id"], s["start"], s["end"]) for s in out] == [("c1", 0.0, 4.0), ("c2", 4.0, 8.0)]
    s = out[0]
    assert s["mau"] == "minh-hoa" and s["svg"] == "chip" and s["san_khau"] == "nen-dat" and s["may_quay"] == "day-vao"
    assert [b["svg"] for b in s["bo_cuc"]] == ["cay", "dong-xu"] and (s["bo_cuc"][0]["x"], s["bo_cuc"][0]["y"]) == dao_dien.SLOT[0]
    assert len(s["nhip"]) == 3 and all(canh.phrase_time(TIMING["words"], p, s["start"], s["end"]) is not None for p in s["nhip"])

def test_main_writes_canh_json_backup_and_hinh_thieu(tmp_path, svg_dir, monkeypatch):
    monkeypatch.setattr(dao_dien, "SVG_DIR", svg_dir)
    for name, data in (("dao-dien.json", _dd()), ("canh-khung.json", KHUNG), ("giong-timing.json", TIMING),
                       ("canh.json", {"scenes": [{"id": "cu"}]})):
        (tmp_path / name).write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    assert dao_dien.main(str(tmp_path)) == 0
    assert json.loads((tmp_path / "canh-truoc-dao-dien.json").read_text(encoding="utf-8")) == {"scenes": [{"id": "cu"}]}
    assert [s["id"] for s in json.loads((tmp_path / "canh.json").read_text(encoding="utf-8"))["scenes"]] == ["c1", "c2"]
    assert json.loads((tmp_path / "hinh-thieu.json").read_text(encoding="utf-8")) == []
```
(`svg_dir` là fixture tạo thư mục có `nen-dat.svg`, `chip.svg`, `cay.svg`, `dong-xu.svg`. `main` luôn truyền `SVG_DIR` của module vào `validate`, để test thay được bằng `monkeypatch`.)

- [ ] **Step 2:** `uv run pytest tests/test_dao_dien.py -q`. Expected: FAIL.
- [ ] **Step 3:** Implement; thêm `__main__` (`python -m tttc.dao_dien <thư mục video>`).
- [ ] **Step 4:** `uv run pytest tests/test_dao_dien.py -q`. Expected: PASS; `uv run pytest -q` PASS.
- [ ] **Step 5: Commit** `git add pipeline/tttc/dao_dien.py pipeline/tests/test_dao_dien.py && git commit -m "feat: dao_dien kiểm và sinh canh.json từ dao-dien.json"`.

### Task 10: Bước `dao-dien` trong quy trình và giám khảo hình ảnh

**Files:** Modify `pipeline/tttc/trang_thai.py` (`STEPS`, di trú), `pipeline/tests/test_trang_thai.py`, `.claude/skills/video-dung/SKILL.md`; Create `pipeline/phong-cach/giam-khao-hinh.md`.

**Interfaces:** `STEPS` thêm `"dao-dien"` giữa `"giong"` và `"canh"`. `load` di trú: thiếu `dao-dien` trong tệp cũ và bất kỳ bước từ `"canh"` trở đi khác `chua-chay` → `{"status": "xong", "note": "video có trước bước này"}`; ngược lại `chua-chay`.

- [ ] **Step 1: Viết test** (cùng kiểu Task 4 của kế hoạch giọng văn): `STEPS.index("dao-dien") == STEPS.index("giong") + 1 == STEPS.index("canh") - 1`; video mới đã `giong` xong thì `next_step` = `dao-dien`; tệp cũ có `canh` = `xong` không bị đẩy lùi (`next_step` không trả `dao-dien`); tệp cũ có `giong` xong nhưng `canh` chưa chạy thì `next_step` = `dao-dien`.
- [ ] **Step 2:** `uv run pytest tests/test_trang_thai.py -q`. Expected: FAIL, rồi PASS sau khi implement.
- [ ] **Step 3:** `video-dung/SKILL.md`: thêm mục `dao-dien` giữa mục 1 (giong) và mục "canh": (a) bốn nguyên tắc đạo diễn của spec 3 mục 4.1 (chép nguyên văn); (b) `uv run python -m tttc.chia V` rồi viết `dao-dien.json` theo định dạng ở Task 9, cảnh trọng điểm ~30% (mở bài, số lớn, đảo chiều, kết, đỉnh mỗi beat) chỉ đạo sâu, còn lại theo luật đa dạng; (c) chia theo beat cho subagent chạy song song, một agent tổng hợp kiểm nhịp cảm xúc toàn video, giới hạn khoảng 45 phút; (d) `uv run python -m tttc.dao_dien V` rồi vẽ hình trong `hinh-thieu.json` bằng `svg/ve.py`; (e) giám khảo: subagent độc lập, không chia sẻ ngữ cảnh, nhận `dao-dien.json` + bảng soi cảnh và nội dung `phong-cach/giam-khao-hinh.md`, ghi `dao-dien-cham.json`; tối đa 2 vòng sửa; (f) mục `canh` đổi thành "chạy `tttc.canh` và `tttc.chat_luong`" trên `canh.json` đã sinh. Các video cũ không có `dao-dien.json` vẫn viết `canh.json` bằng tay.
- [ ] **Step 4:** Viết `giam-khao-hinh.md`: vai trò, bốn tiêu chí (ý nghĩa, đa dạng, chiều sâu, nhịp cảm xúc) chấm 1–5 mỗi beat, yêu cầu nêu cảnh khô và ẩn dụ vượt nguồn, và đầu ra JSON đúng định dạng `{"beats": [{"y_nghia","da_dang","chieu_sau","nhip","ghi_chu"}]}`.
- [ ] **Step 5:** `uv run pytest -q`. Expected: PASS. Kiểm `grep -n "dao_dien\|giam-khao-hinh" .claude/skills/video-dung/SKILL.md`: có cả hai.
- [ ] **Step 6: Commit** `git add pipeline/tttc/trang_thai.py pipeline/tests/test_trang_thai.py .claude/skills/video-dung/SKILL.md pipeline/phong-cach/giam-khao-hinh.md && git commit -m "feat: bước dao-dien và giám khảo hình ảnh trong quy trình dựng"`.

### Task 11: Chạy thử trên video thật và hiệu chỉnh

- [ ] **Step 1:** Trên `videos/2026-11-15-nvidia-siet-chip` (không đè `canh.json` đã đăng: chép sang `videos/thu-nghiem/dao-dien-thu/`), Claude đóng vai đạo diễn cho 3 beat đầu: viết `dao-dien.json`, `uv run python -m tttc.dao_dien`, vẽ hình thiếu, chạy giám khảo. Ghi thời gian từng phần bằng `trang_thai.gio`.
- [ ] **Step 2:** Dựng và render `draft` ba beat đó; `dung.contact_sheet`; **bạn xem** và so với cùng đoạn của bản đã đăng.
- [ ] **Step 3:** `uv run python -m tttc.chat_luong` trên `canh.json` thử: ghi `do_kho` cạnh mốc nền ở `docs/nghien-cuu/do-kho-nen-2026-11-09.md`. Hiệu chỉnh các ngưỡng đánh dấu "đề xuất" (tỉ lệ cảnh trọng điểm, 45 phút, ngưỡng độ khô, điểm giám khảo) theo số đo và ý bạn; ghi lý do.
- [ ] **Step 4: Commit** `git add docs/nghien-cuu pipeline && git commit -m "docs: chạy thử bước đạo diễn và hiệu chỉnh ngưỡng độ khô"`.
