# Giọng văn kịch bản tự nhiên và phản biện agy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Kịch bản qua cổng giọng văn (danh sách cấm cứng, nhịp, phản biện 2 vòng với agy, nghe thử 60 giây) trước điểm duyệt 1, để không phải làm lại giọng/cảnh/render vì "mùi AI".

**Architecture:** Mở rộng `tttc/phong_cach.py` (kiểm, thêm lệnh chạy riêng), thêm `tttc/phan_bien.py` (gọi `agy` bằng `subprocess`, lưu phản hồi thô, không phân tích nội dung), thêm bước `phan-bien-giong` vào sổ trạng thái, chặn `duyet.render_review_1` khi chưa xong, thêm `giong_vieneu.nghe_thu`. Phần nội dung (mẫu giọng, SKILL, thẻ phong cách) là tệp văn bản.

**Tech Stack:** Python ≥ 3.11, pytest (chạy bằng `uv run`), ffmpeg, `agy` 1.5.3 (CLI), VieNeu-TTS (đã có).

**Spec:** `docs/superpowers/specs/2026-11-09-giong-van-kich-ban-design.md`

## Global Constraints

- Thông báo kiểm có tiền tố `Lỗi:` hoặc `Cảnh báo:`, tiếng Việt như hiện có. Danh sách cấm là **Lỗi**; mọi thứ khác là cảnh báo.
- Ngoại lệ danh sách cấm: chữ nằm trong dấu ngoặc kép (`"..."` hoặc `“...”`) trích nguyên văn từ nguồn.
- Ngưỡng nhịp (cảnh báo): ≥ 10% câu ≤ 5 từ (đã có); độ lệch chuẩn/trung bình độ dài câu ≥ 0,5; không quá 4 câu liền cùng độ dài (±20% so với câu đầu chuỗi); không quá 8 câu dài hơn 28 từ; tính từ cảm thán không quá 5; từ đệm không quá 15. Thống kê nhịp chỉ tính khi có ≥ 20 câu.
- agy: `agy -p "<prompt>" --output-format json --print-timeout 600s`, vòng 2 thêm `--conversation <id>`. **Không** `--dangerously-skip-permissions`, **không** `--json-schema`. Đúng 2 vòng. Chỉ gửi phần lời đọc.
- Mẫu giọng không lấy từ lời của @MotCongNghe. Sửa theo agy không được đổi con số, thẻ `[#id]`, câu "sơ bộ"/"mình tự tính".
- Test không gọi `agy` hay VieNeu thật; dùng `run` giả như `_fake_worker` trong `tests/test_giong_vieneu.py`.
- Chạy lệnh trong `pipeline/`. Chỉ `git add` đường dẫn cụ thể (nhánh `pipeline` đang có thay đổi chưa commit từ trước, xem Task 0).

## Review Focus

1. Câu trích nguồn trong ngoặc kép chứa từ cấm ("bước ngoặt") → không được báo Lỗi (Task 1).
2. Văn bản ở dạng Unicode tách dấu (NFD) hoặc viết hoa toàn bộ vẫn bị bắt từ cấm (Task 1).
3. Kịch bản không có phần "Lời đọc", hoặc ngắn dưới 20 câu → lệnh kiểm im lặng, không báo thống kê nhịp sai (Task 1, 2, 3).
4. Video cũ đã qua duyệt 1 không bị đẩy lùi về bước `phan-bien-giong` (Task 4).
5. agy không có trong máy / quá thời gian / trả JSON hỏng / `status` khác `SUCCESS` → lỗi rõ ràng, không treo, không bỏ qua im lặng (Task 5).

---

### Task 0: Nền sạch

**Files:** không sửa.

- [ ] **Step 1:** Chạy `uv run pytest -q` trong `pipeline/`. Expected: toàn bộ test hiện có PASS (ghi lại số test).
- [ ] **Step 2:** Chạy `git status --short -- pipeline/tttc/phong_cach.py pipeline/tests/test_phong_cach.py pipeline/tttc/duyet.py pipeline/tttc/trang_thai.py pipeline/tttc/giong_vieneu.py`. Hai tệp `phong_cach.py` và `test_phong_cach.py` đang ở trạng thái `M` (thay đổi chưa commit từ trước). **Dừng và hỏi người dùng** commit chúng riêng (hoặc stash) trước khi tiếp tục, để commit của kế hoạch này sạch. Không tự commit hộ.

### Task 1: Danh sách cấm cứng `tu_cam`

**Files:**
- Create: `pipeline/phong-cach/tu-cam.json`
- Modify: `pipeline/tttc/phong_cach.py` (thêm `TU_CAM`, `tu_cam`; xóa `DICH_THO` và vòng lặp dùng nó trong `mui_may`)
- Test: `pipeline/tests/test_phong_cach.py`

**Interfaces:**
- Produces: `phong_cach.TU_CAM: Path`; `phong_cach.tu_cam(script_md: str, path: Path = TU_CAM) -> list[str]` — mỗi vi phạm một chuỗi bắt đầu `Lỗi:`; rỗng nếu kịch bản không có lời đọc.

- [ ] **Step 1: Viết test (thêm vào `test_phong_cach.py`, thêm `import unicodedata, pytest`, thay test `test_translationese_phrase_is_named` cũ)**

```python
CAM = [("Đây là một bước đột phá của ngành.", "từ cấm"),
       ("Giải pháp hoàn hảo cho mọi nhà.", "từ cấm"),
       ("Không chỉ rẻ hơn mà còn nhanh hơn.", "từ cấm"),
       ("Chiếc chìa khóa vàng của ngành.", "từ cấm")]

@pytest.mark.parametrize("spoken,key", CAM)
def test_tu_cam_flags_banned_phrase_as_error(spoken, key):
    out = phong_cach.tu_cam(_script(spoken))
    assert len(_w(out, key)) == 1 and out[0].startswith("Lỗi:")

def test_translationese_phrase_is_named():
    out = _w(phong_cach.tu_cam(_script("Hãy nhìn đúng những gì trang giá nói. Giá là chín trăm.")), "dịch thô")
    assert len(out) == 1 and "hãy nhìn đúng" in out[0].lower()
    assert _w(phong_cach.tu_cam(_script("Mở bảng giá ra xem họ ghi gì.")), "dịch thô") == []

def test_tu_cam_opening_only_in_first_40_words():
    assert _w(phong_cach.tu_cam(_script("Bạn đã bao giờ tự hỏi vì sao chip đắt? Giá là chín trăm.")), "mở bài")
    late = _filler(60) + " Bạn đã bao giờ tự hỏi vì sao chip đắt?"
    assert _w(phong_cach.tu_cam(_script(late)), "mở bài") == []

def test_tu_cam_closing_only_in_last_60_words():
    assert _w(phong_cach.tu_cam(_script(_filler(100) + " Tóm lại, chip đắt.")), "kết bài")
    assert _w(phong_cach.tu_cam(_script("Tóm lại, chip đắt. " + _filler(100))), "kết bài") == []

def test_tu_cam_ignores_quoted_source_text():
    assert phong_cach.tu_cam(_script('Bài báo viết “một bước ngoặt của ngành” rồi dừng.')) == []
    assert phong_cach.tu_cam(_script('Bài báo viết "một bước ngoặt của ngành" rồi dừng.')) == []
    assert len(phong_cach.tu_cam(_script("Đây là bước ngoặt của ngành."))) == 1

def test_tu_cam_matches_decomposed_unicode_and_uppercase():
    assert len(phong_cach.tu_cam(_script(unicodedata.normalize("NFD", "ĐỘT PHÁ là từ bị cấm.")))) == 1

def test_tu_cam_silent_without_spoken_paragraphs():
    assert phong_cach.tu_cam("Chỉ có ghi chú, không có lời đọc.") == []
```

- [ ] **Step 2:** Chạy `uv run pytest tests/test_phong_cach.py -q`. Expected: FAIL (`AttributeError: ... 'tu_cam'`).
- [ ] **Step 3: Tạo `pipeline/phong-cach/tu-cam.json` với đúng nội dung này**

```json
{
  "tu": ["đột phá", "nâng tầm", "hãy cùng khám phá", "giải pháp hoàn hảo", "bức tranh toàn cảnh",
         "chiếc chìa khóa vàng", "chiếc chìa khoá vàng", "bước ngoặt"],
  "mau": ["không chỉ[^.!?…]*mà còn"],
  "mo_bai": ["bạn đã bao giờ tự hỏi", "trong kỷ nguyên số ngày nay"],
  "ket_bai": ["tóm lại", "hãy nhớ rằng", "hãy bắt đầu hành trình ngay hôm nay"],
  "dich_tho": ["hãy nhìn đúng", "như các bạn đã biết", "không thể phủ nhận", "trong thế giới ngày nay",
               "hãy cùng nhau", "tóm lại bằng", "điều quan trọng cần lưu ý", "chúng ta sẽ cùng"]
}
```

- [ ] **Step 4: Implement `tu_cam` trong `phong_cach.py`.** Lấy lời đọc bằng `tts.spoken_paragraphs` (đã chuẩn hóa NFC), cắt bỏ chữ trong ngoặc kép bằng regex rồi hạ chữ thường để so khớp. `tu`/`dich_tho`: tìm chuỗi con; `mau`: `re.search`; `mo_bai`: chỉ 40 từ đầu; `ket_bai`: chỉ 60 từ cuối. Định dạng thông báo: `Lỗi: từ cấm «{cụm}»: {70 ký tự quanh vi phạm}`, `Lỗi: mở bài sáo rỗng «{cụm}»`, `Lỗi: kết bài đúc kết đạo lý «{cụm}»`, `Lỗi: cụm nghe như dịch thô từ tiếng Anh: «{cụm}»`. Xóa hằng `DICH_THO` và vòng lặp của nó trong `mui_may`.
- [ ] **Step 5:** Chạy `uv run pytest tests/test_phong_cach.py -q`. Expected: PASS.
- [ ] **Step 6: Commit**

```bash
git add pipeline/phong-cach/tu-cam.json pipeline/tttc/phong_cach.py pipeline/tests/test_phong_cach.py
git commit -m "feat: danh sách cấm cứng cho giọng văn kịch bản (tu_cam), dịch thô chuyển thành Lỗi"
```

### Task 2: Kiểm nhịp, từ đệm, trải nghiệm bịa; bỏ yêu cầu "đổi ý"

**Files:**
- Modify: `pipeline/tttc/phong_cach.py` (thêm `NHIP`, `CAM_THAN`, `TU_DEM`, `TRAI_NGHIEM`, `nhip`; bỏ khối `"đổi ý"` và biến `low` thừa trong `mui_may`)
- Test: `pipeline/tests/test_phong_cach.py`

**Interfaces:**
- Produces: `phong_cach.NHIP = {"cv_min": 0.5, "chuoi_max": 4, "dai_tu": 28, "dai_max": 8, "cam_than_max": 5, "dem_max": 15, "toi_thieu_cau": 20}`; `phong_cach.nhip(script_md: str) -> list[str]` chỉ trả `Cảnh báo:`.
- Regex (không phân biệt hoa/thường): `CAM_THAN = r"\b(?:rất|vô cùng|cực kỳ|khổng lồ|đáng kinh ngạc|choáng)\b"`; `TU_DEM = r"kiểu như|nói thật là|đoạn này mới cấn|tính ra thì"`; `TRAI_NGHIEM = r"\b(?:mình từng|hồi mình|có lần mình|tôi từng)\b"`.

- [ ] **Step 1: Viết test** (thay `test_needs_change_of_mind_condition`)

```python
def _sents(lengths):
    return " ".join(" ".join(["từ"] * (n - 1)) + " xong." for n in lengths)

def test_change_of_mind_is_no_longer_required():
    assert _w(_mui("Phán quyết là ở bản miễn phí."), "đổi ý") == []

def test_nhip_flags_uniform_sentence_lengths():
    assert len(_w(phong_cach.nhip(_script(_sents([12] * 30))), "độ lệch")) == 1
    assert _w(phong_cach.nhip(_script(_sents([3, 14, 9, 22, 5, 17, 11, 30, 4, 13] * 3))), "độ lệch") == []

def test_nhip_flags_run_longer_than_four_similar_sentences():
    base = [3, 20, 9, 27, 5, 16, 11, 24, 4, 14] * 2
    assert len(_w(phong_cach.nhip(_script(_sents(base + [10, 10, 11, 10, 9] + base))), "câu liền")) == 1
    assert _w(phong_cach.nhip(_script(_sents(base + [10, 10, 11, 10] + base))), "câu liền") == []

def test_nhip_flags_more_than_eight_long_sentences():
    assert len(_w(phong_cach.nhip(_script(_sents([30] * 9 + [5] * 12))), "dài hơn 28")) == 1
    assert _w(phong_cach.nhip(_script(_sents([30] * 8 + [5] * 12))), "dài hơn 28") == []

def test_nhip_counts_emotive_adjectives_and_fillers():
    assert len(_w(phong_cach.nhip(_script("Giá rất cao. " * 6)), "cảm thán")) == 1
    assert _w(phong_cach.nhip(_script("Giá rất cao. " * 5)), "cảm thán") == []
    assert len(_w(phong_cach.nhip(_script("Kiểu như vậy đó. " * 16)), "từ đệm")) == 1
    assert _w(phong_cach.nhip(_script("Kiểu như vậy đó. " * 15)), "từ đệm") == []

def test_nhip_flags_invented_personal_experience():
    assert len(_w(phong_cach.nhip(_script("Hồi mình nợ thẻ năm chục triệu. Giá là chín trăm.")), "trải nghiệm cá nhân")) == 1
    assert _w(phong_cach.nhip(_script("Mình đọc xong tài liệu sáng nay. Giá là chín trăm.")), "trải nghiệm cá nhân") == []

def test_nhip_skips_statistics_on_short_excerpts():
    out = phong_cach.nhip(_script(_sents([12] * 10)))
    assert _w(out, "độ lệch") == [] and _w(out, "câu liền") == []
```

- [ ] **Step 2:** Chạy `uv run pytest tests/test_phong_cach.py -q`. Expected: FAIL (`nhip` chưa có; test "đổi ý" mới FAIL vì `mui_may` còn yêu cầu).
- [ ] **Step 3: Implement `nhip(script_md)`.** Tách câu như `mui_may` (`re.split(r"(?<=[.!?…])\s+", ...)`), độ dài = số từ. Với ≥ `toi_thieu_cau` câu: độ lệch chuẩn/trung bình (`statistics.pstdev`) < `cv_min` → `Cảnh báo: độ lệch chuẩn/trung bình độ dài câu {x:.2f}, cần ≥ 0,5 (nhịp quá đều)`; chuỗi dài nhất các câu liền có độ dài trong ±20% độ dài **câu đầu chuỗi** > `chuoi_max` → `Cảnh báo: {n} câu liền cùng độ dài`; số câu > `dai_tu` từ > `dai_max` → `Cảnh báo: {n} câu dài hơn 28 từ, khó đọc to`. Không phụ thuộc số câu: cảm thán > `cam_than_max` → `Cảnh báo: {n} tính từ cảm thán...`; từ đệm > `dem_max` → `Cảnh báo: {n} từ đệm...`; mỗi lần khớp `TRAI_NGHIEM` → `Cảnh báo: cụm kể trải nghiệm cá nhân «...», kênh tin tức không được bịa trải nghiệm`.
- [ ] **Step 4:** Xóa khối `if "đổi ý" not in low:` và biến `low` trong `mui_may`.
- [ ] **Step 5:** Chạy `uv run pytest tests/test_phong_cach.py -q`. Expected: PASS.
- [ ] **Step 6: Commit**

```bash
git add pipeline/tttc/phong_cach.py pipeline/tests/test_phong_cach.py
git commit -m "feat: kiểm nhịp, từ đệm, trải nghiệm bịa; bỏ yêu cầu điều kiện đổi ý"
```

### Task 3: `kiem` gộp các kiểm mới và lệnh chạy riêng

**Files:**
- Modify: `pipeline/tttc/phong_cach.py` (`kiem` nối thêm `tu_cam` và `nhip`; thêm `main`)
- Test: `pipeline/tests/test_phong_cach.py`

**Interfaces:**
- Consumes: `tu_cam`, `nhip` (Task 1–2).
- Produces: `phong_cach.main(video_dir: str) -> int` đọc `kich-ban.md`, in từng thông báo dạng `- {msg}` rồi `{n} Lỗi, {m} cảnh báo`, trả 1 nếu có `Lỗi:`, ngược lại 0; chạy được bằng `python -m tttc.phong_cach <thư mục video>`.

- [ ] **Step 1: Viết test** (thêm `from pathlib import Path`)

```python
def test_kiem_includes_tu_cam_and_nhip():
    out = phong_cach.kiem(_long(head=OK_HEAD + "Đây là bước đột phá. " + "Giá rất cao. " * 6))
    assert _w(out, "từ cấm") and _w(out, "cảm thán")

def test_main_exit_code_follows_errors(tmp_path, capsys):
    (tmp_path / "kich-ban.md").write_text(_long(head=OK_HEAD + "Đây là bước đột phá. "), encoding="utf-8")
    assert phong_cach.main(str(tmp_path)) == 1 and "Lỗi" in capsys.readouterr().out
    (tmp_path / "kich-ban.md").write_text(_long(head=OK_HEAD, tail="Bạn đoán năm nào?"), encoding="utf-8")
    assert phong_cach.main(str(tmp_path)) == 0

BASELINE = [Path(__file__).resolve().parents[2] / "videos" / v for v in
            ("2026-11-15-nvidia-siet-chip/kich-ban-v2.md", "2026-11-13-goi-ai-dang-tien/kich-ban.md")]

@pytest.mark.skipif(not all(p.exists() for p in BASELINE), reason="kịch bản đã duyệt không có trong máy này")
@pytest.mark.parametrize("p", BASELINE)
def test_approved_scripts_stay_clean(p):
    assert phong_cach.kiem(p.read_text(encoding="utf-8")) == []
```

- [ ] **Step 2:** Chạy `uv run pytest tests/test_phong_cach.py -q`. Expected: FAIL (`main` chưa có, `kiem` chưa nối).
- [ ] **Step 3:** Implement: `kiem` trả `out + mui_may(...) + tu_cam(...) + nhip(...)` (vẫn im lặng khi không có lời đọc); thêm `main` và khối `if __name__ == "__main__": sys.exit(main(sys.argv[1]))`.
- [ ] **Step 4:** Chạy `uv run pytest tests/test_phong_cach.py -q`. Expected: PASS, kể cả `test_approved_scripts_stay_clean`. Nếu test đó FAIL, **đọc thông báo và sửa ngưỡng hoặc luật có chủ đích** (ghi lý do vào commit); không nới ngầm.
- [ ] **Step 5:** Chạy `uv run python -m tttc.phong_cach ../videos/2026-11-15-nvidia-siet-chip` và với `2026-11-13-goi-ai-dang-tien`. Expected: `0 Lỗi, 0 cảnh báo`, thoát mã 0.
- [ ] **Step 6: Commit**

```bash
git add pipeline/tttc/phong_cach.py pipeline/tests/test_phong_cach.py
git commit -m "feat: python -m tttc.phong_cach thoát mã 1 khi có Lỗi; kiem gộp tu_cam và nhip"
```

### Task 4: Bước `phan-bien-giong` trong sổ trạng thái

**Files:**
- Modify: `pipeline/tttc/trang_thai.py:6-7` (`STEPS`), `load` (di trú)
- Test: `pipeline/tests/test_trang_thai.py`

**Interfaces:**
- Produces: `STEPS` có `"phan-bien-giong"` ngay sau `"kich-ban"`, trước `"kiem"`. `load`: khi tệp sổ cũ **thiếu** bước này **và** bất kỳ bước từ `"duyet-1"` trở đi khác `chua-chay` thì mặc định `{"status": "xong", "note": "video có trước bước này"}`; ngược lại `chua-chay`.

- [ ] **Step 1: Viết test**

```python
def test_phan_bien_giong_sits_between_kich_ban_and_kiem():
    assert tt.STEPS.index("phan-bien-giong") == tt.STEPS.index("kich-ban") + 1 == tt.STEPS.index("kiem") - 1

def test_new_video_must_review_voice_before_kiem(tmp_path):
    for s in ["chu-de", "nguon", "kich-ban"]:
        tt.set_step(tmp_path, s, "xong")
    assert tt.next_step(tmp_path) == "phan-bien-giong"

def _old(tmp_path, duyet_1=None):
    steps = {s: {"status": "xong", "note": ""} for s in ["chu-de", "nguon", "kich-ban", "kiem"]}
    if duyet_1:
        steps["duyet-1"] = {"status": duyet_1, "note": ""}
    (tmp_path / "trang-thai.json").write_text(json.dumps({"steps": steps}), encoding="utf-8")

def test_old_video_past_review_1_is_not_pushed_back(tmp_path):
    _old(tmp_path, "da-duyet")
    assert tt.load(tmp_path)["steps"]["phan-bien-giong"]["status"] == "xong"
    assert tt.next_step(tmp_path) == "giong"

def test_old_video_before_review_1_still_needs_voice_review(tmp_path):
    _old(tmp_path)
    assert tt.next_step(tmp_path) == "phan-bien-giong"
```

- [ ] **Step 2:** `uv run pytest tests/test_trang_thai.py -q`. Expected: FAIL.
- [ ] **Step 3:** Implement: thêm bước vào `STEPS`; trong `load`, tính điều kiện di trú từ `data["steps"]` thô **trước** khi điền mặc định. Các test cũ trong tệp này phải vẫn PASS.
- [ ] **Step 4:** `uv run pytest tests/test_trang_thai.py -q`. Expected: PASS.
- [ ] **Step 5: Commit**

```bash
git add pipeline/tttc/trang_thai.py pipeline/tests/test_trang_thai.py
git commit -m "feat: bước phan-bien-giong trong sổ trạng thái, video cũ không bị đẩy lùi"
```

### Task 5: `tttc/phan_bien.py` — gọi agy

**Files:**
- Create: `pipeline/tttc/phan_bien.py`, `pipeline/tests/test_phan_bien.py`

**Interfaces:**
- Produces:
  - `class AgyLoi(RuntimeError)`.
  - `goi(prompt: str, conversation_id: str | None = None, timeout_s: int = 600, luu: Path | None = None, run=subprocess.run) -> dict` trả `{"status": str, "response": str, "conversation_id": str}`. Chạy `["agy", "-p", prompt, "--output-format", "json", "--print-timeout", f"{timeout_s}s"]` (+ `["--conversation", id]`), `timeout=timeout_s + 30`. Nếu có `luu`, ghi stdout thô vào đó trước khi phân tích. Ném `AgyLoi` khi: không tìm thấy `agy`, quá thời gian, mã thoát ≠ 0, stdout không phải JSON, hoặc `status != "SUCCESS"`.
  - `loi_doc(script_md: str) -> str`: các đoạn `tts.spoken_paragraphs(script_md)` nối bằng dòng trống (không có `[TRÊN MÀN HÌNH]`, không có thẻ `[#id]`).
  - `dung_prompt(vong: int, loi_doc: str, tu_cam_text: str, phan_tich: str, triage_md: str = "") -> str`: văn bản theo Phụ lục B của spec; mọi vòng có "không dùng tool, không sửa file", "tối đa 12 vấn đề" và chấm 1–5 bốn tiêu chí; vòng 2 thêm `triage_md` và câu hỏi vấn đề nặng nào chưa xử lý, có vấn đề mới không, điểm mới.
  - `main(argv: list[str], run=subprocess.run) -> int`: `vong <1|2> <thư mục video> [--conversation ID] [--triage tep.md]`; đọc `kich-ban.md`, `phong-cach/tu-cam.json`, `phong-cach/phan-tich-giong.md`; gọi `goi`; ghi `phan-bien-giong-{N}.raw.json` và `phan-bien-giong-{N}.md` (phản hồi nguyên văn, rồi `## Bảng triage` để trống); in `conversation_id: <id>` và phản hồi; trả 0. Vòng 2 thiếu `--conversation` hoặc `--triage` → in lý do, trả 2. `AgyLoi` → in `agy lỗi: <lý do>`, trả 3.

- [ ] **Step 1: Viết `tests/test_phan_bien.py`**

```python
import json, subprocess
import pytest
from tttc import phan_bien

OK = {"status": "SUCCESS", "response": "1. Câu sáo rỗng ...", "conversation_id": "abc-123"}

def _run(payload=OK, code=0, calls=None):
    def run(cmd, **kw):
        if calls is not None:
            calls.append((cmd, kw))
        return subprocess.CompletedProcess(cmd, code, stdout=json.dumps(payload), stderr="")
    return run

def test_goi_builds_safe_command():
    calls = []
    phan_bien.goi("P", run=_run(calls=calls))
    cmd = calls[0][0]
    assert cmd[:3] == ["agy", "-p", "P"] and cmd[cmd.index("--output-format") + 1] == "json"
    assert cmd[cmd.index("--print-timeout") + 1] == "600s"
    assert "--dangerously-skip-permissions" not in cmd and "--json-schema" not in cmd

def test_goi_resumes_conversation():
    calls = []
    phan_bien.goi("P", conversation_id="abc-123", run=_run(calls=calls))
    cmd = calls[0][0]
    assert cmd[cmd.index("--conversation") + 1] == "abc-123"

def test_goi_returns_status_response_and_conversation():
    assert phan_bien.goi("P", run=_run()) == OK

def test_goi_saves_raw_stdout(tmp_path):
    phan_bien.goi("P", luu=tmp_path / "raw.json", run=_run())
    assert json.loads((tmp_path / "raw.json").read_text(encoding="utf-8"))["conversation_id"] == "abc-123"

@pytest.mark.parametrize("run", [
    _run({**OK, "status": "ERROR"}), _run(code=1),
    lambda cmd, **kw: subprocess.CompletedProcess(cmd, 0, stdout="không phải json", stderr=""),
    lambda cmd, **kw: (_ for _ in ()).throw(FileNotFoundError()),
    lambda cmd, **kw: (_ for _ in ()).throw(subprocess.TimeoutExpired(cmd, 1)),
])
def test_goi_raises_agyloi_on_every_failure(run):
    with pytest.raises(phan_bien.AgyLoi):
        phan_bien.goi("P", run=run)

def test_loi_doc_drops_screen_lines_and_tags():
    md = "#### Beat 1\n[TRÊN MÀN HÌNH]: chữ lớn\n**Lời đọc:**\nGiá là chín trăm. [#p1]\nXong.\n"
    assert phan_bien.loi_doc(md) == "Giá là chín trăm.\n\nXong."

def test_prompt_round_1_and_2():
    p1 = phan_bien.dung_prompt(1, "LỜI ĐỌC", "TU-CAM", "PHÂN TÍCH")
    assert all(x in p1 for x in ("LỜI ĐỌC", "TU-CAM", "PHÂN TÍCH", "không dùng tool", "tối đa 12"))
    p2 = phan_bien.dung_prompt(2, "LỜI ĐỌC", "TU-CAM", "PHÂN TÍCH", triage_md="BẢNG TRIAGE")
    assert "BẢNG TRIAGE" in p2 and "chưa xử lý" in p2 and "BẢNG TRIAGE" not in p1

def _video(tmp_path):
    (tmp_path / "kich-ban.md").write_text("#### Beat 1\n**Lời đọc:**\nGiá là chín trăm.\n", encoding="utf-8")
    return tmp_path

def test_main_round_1_writes_md_raw_and_prints_conversation(tmp_path, capsys):
    d = _video(tmp_path)
    assert phan_bien.main(["vong", "1", str(d)], run=_run()) == 0
    assert "conversation_id: abc-123" in capsys.readouterr().out
    md = (d / "phan-bien-giong-1.md").read_text(encoding="utf-8")
    assert OK["response"] in md and "## Bảng triage" in md
    assert (d / "phan-bien-giong-1.raw.json").exists()

def test_main_round_2_needs_conversation_and_triage(tmp_path):
    assert phan_bien.main(["vong", "2", str(_video(tmp_path))], run=_run()) == 2

def test_main_returns_3_when_agy_fails(tmp_path, capsys):
    assert phan_bien.main(["vong", "1", str(_video(tmp_path))], run=_run({**OK, "status": "ERROR"})) == 3
    assert "agy lỗi" in capsys.readouterr().out
```

- [ ] **Step 2:** `uv run pytest tests/test_phan_bien.py -q`. Expected: FAIL (`ModuleNotFoundError`).
- [ ] **Step 3:** Implement các hàm theo khối Interfaces. `tu_cam_text` = nội dung thô của `phong-cach/tu-cam.json`; `main` đọc `PIPE / "phong-cach"` với `PIPE = Path(__file__).resolve().parent.parent`, thiếu `phan-tich-giong.md` thì dùng chuỗi rỗng (Task 8 tạo tệp thật). Không phân tích nội dung phản hồi của agy.
- [ ] **Step 4:** `uv run pytest tests/test_phan_bien.py -q`. Expected: PASS.
- [ ] **Step 5: Commit**

```bash
git add pipeline/tttc/phan_bien.py pipeline/tests/test_phan_bien.py
git commit -m "feat: tttc.phan_bien gọi agy theo vòng, lưu phản hồi thô, báo lỗi rõ"
```

### Task 6: Cổng trong trang duyệt 1

**Files:**
- Modify: `pipeline/tttc/duyet.py:54-63` (`render_review_1`), `pipeline/templates/duyet.html` (một quy tắc CSS `.canh-bao.do`)
- Test: `pipeline/tests/test_duyet.py`

**Interfaces:**
- Consumes: `trang_thai.load` (Task 4), `phong_cach.kiem` (Task 3).
- Produces: `render_review_1(video_dir) -> Path` ném `ValueError` nếu bước `phan-bien-giong` ≠ `xong` (thông báo chứa "phản biện giọng văn") hoặc `phong_cach.kiem` còn thông báo bắt đầu `Lỗi` (thông báo chứa "Lỗi"). Thêm khối `<div class="phan-bien">` gồm ghi chú của bước, liên kết `phan-bien-giong-1.md` / `-2.md` nếu tệp tồn tại, và `<audio controls src="nghe-thu.mp3">` nếu `nghe-thu.mp3` tồn tại. Ghi chú chứa "agy lỗi" → khối có `<div class="canh-bao do">`.

- [ ] **Step 1: Sửa và thêm test.** Trong `_video` của `test_duyet.py` thêm `tt.set_step(tmp_path, "phan-bien-giong", "xong", "vòng 1: 5 mục (nhận 4, bỏ 1); vòng 2: 1 mục")` với `from tttc import duyet, trang_thai as tt` và `import pytest`. Thêm:

```python
def test_review_1_refuses_without_voice_review(tmp_path):
    d = _video(tmp_path)
    tt.set_step(d, "phan-bien-giong", "chua-chay")
    with pytest.raises(ValueError, match="phản biện giọng văn"):
        duyet.render_review_1(d)

def test_review_1_refuses_when_style_errors_remain(tmp_path):
    d = _video(tmp_path, "#### Beat 1\n**Lời đọc:**\nĐây là bước đột phá. Giá 522.500 đồng. [#p1]\n")
    with pytest.raises(ValueError, match="Lỗi"):
        duyet.render_review_1(d)

def test_review_1_shows_voice_review_note_and_links(tmp_path):
    d = _video(tmp_path)
    (d / "phan-bien-giong-1.md").write_text("x", encoding="utf-8")
    (d / "phan-bien-giong-2.md").write_text("y", encoding="utf-8")
    html = duyet.render_review_1(d).read_text(encoding="utf-8")
    assert "vòng 1: 5 mục" in html and 'href="phan-bien-giong-1.md"' in html and 'href="phan-bien-giong-2.md"' in html

def test_review_1_flags_agy_failure_in_red(tmp_path):
    d = _video(tmp_path)
    tt.set_step(d, "phan-bien-giong", "xong", "agy lỗi, dùng subagent")
    assert 'class="canh-bao do"' in duyet.render_review_1(d).read_text(encoding="utf-8")

def test_review_1_embeds_listening_sample_when_present(tmp_path):
    d = _video(tmp_path)
    (d / "nghe-thu.mp3").write_bytes(b"x")
    assert '<audio controls src="nghe-thu.mp3"' in duyet.render_review_1(d).read_text(encoding="utf-8")
```

- [ ] **Step 2:** `uv run pytest tests/test_duyet.py -q`. Expected: các test mới FAIL; test cũ vẫn PASS nhờ `_video` đã đặt bước `xong`.
- [ ] **Step 3:** Implement theo Interfaces. Khối `phan-bien` đặt ngay trên `<h2>Chủ đề</h2>`; mọi chuỗi qua `escape`. Thêm vào CSS: `.canh-bao.do { border-color: #FF6B6B; }`.
- [ ] **Step 4:** `uv run pytest tests/test_duyet.py -q`. Expected: PASS; sau đó `uv run pytest -q` toàn bộ PASS.
- [ ] **Step 5: Commit**

```bash
git add pipeline/tttc/duyet.py pipeline/templates/duyet.html pipeline/tests/test_duyet.py
git commit -m "feat: duyệt 1 từ chối khi chưa phản biện giọng văn hoặc còn Lỗi giọng văn; hiện kết quả agy và nghe thử"
```

### Task 7: Nghe thử 60 giây

**Files:**
- Modify: `pipeline/tttc/giong_vieneu.py` (thêm `nghe_thu`, dòng lệnh `thu-60s`, cập nhật docstring đầu tệp)
- Test: `pipeline/tests/test_giong_vieneu.py` (dùng `_video`, `CFG`, `_fake_worker`, `_dur` sẵn có)

**Interfaces:**
- Produces: `giong_vieneu.nghe_thu(video_dir, so_tu: int = 210, cfg: dict | None = None, run=subprocess.run) -> Path` ghi `<video>/nghe-thu.mp3`: các câu đầu của lời đọc (theo `cau`), thêm từng câu cho đến khi tổng số từ ≥ `so_tu`, dùng đúng tên tệp wav `giong-vieneu/{_ten(câu, giọng)}.wav` như `synthesize` để câu giữ nguyên được dùng lại. CLI: `python -m tttc.giong_vieneu thu-60s <thư mục video>`.

- [ ] **Step 1: Viết test**

```python
def test_nghe_thu_reads_first_sentences_up_to_word_budget(tmp_path):
    script = "#### Beat 1\n**Lời đọc:**\n" + " ".join(f"Câu số {i} có sáu chữ nữa." for i in range(40)) + "\n"
    d, calls = _video(tmp_path, script), []
    out = giong_vieneu.nghe_thu(d, so_tu=30, cfg=CFG, run=_fake_worker([0.3], calls=calls))
    assert out == d / "nghe-thu.mp3" and out.exists()
    assert len(calls[0]) == 5 and _dur(out) > 1.0

def test_nghe_thu_wavs_are_reused_by_full_synthesis(tmp_path):
    d = _video(tmp_path)
    giong_vieneu.nghe_thu(d, so_tu=5, cfg=CFG, run=_fake_worker([0.3]))
    calls = []
    giong_vieneu.synthesize(d, cfg=CFG, run=_fake_worker([0.3], calls=calls))
    assert [j["text"] for c in calls for j in c] == ["Giá chưa gồm thuế."]
```

- [ ] **Step 2:** `uv run pytest tests/test_giong_vieneu.py -q`. Expected: FAIL (`nghe_thu` chưa có).
- [ ] **Step 3:** Implement bằng `_tao_wav`, `_cat_nghi` (ghi `nt{k:03}.wav` trong `giong-vieneu/`, tránh đè `u{k:04}.wav`) và ghép bằng ffmpeg concat ra mp3 như cuối `synthesize`.
- [ ] **Step 4:** `uv run pytest tests/test_giong_vieneu.py -q`. Expected: PASS.
- [ ] **Step 5: Commit**

```bash
git add pipeline/tttc/giong_vieneu.py pipeline/tests/test_giong_vieneu.py
git commit -m "feat: nghe thử 60 giây bằng giọng đã chọn, tái dùng wav theo câu"
```

### Task 8: Mẫu giọng, thẻ phong cách, SKILL `video-moi`

**Files:**
- Create: `pipeline/phong-cach/mau-giong/01.md`, `02.md`, `pipeline/phong-cach/phan-tich-giong.md`
- Modify: `docs/phong-cach-kich-ban.md` (mục 6 "Chống mùi máy"), `.claude/skills/video-moi/SKILL.md` (mục 3–5)

- [ ] **Step 1 (cần người dùng):** Hỏi bạn chọn mẫu giọng: mặc định đề xuất hai đoạn tự nhiên nhất từ hai kịch bản đã duyệt (ví dụ đoạn "Chú ý mấy chữ "được báo chí đưa tin"…" trong Beat 2 của `videos/2026-11-15-nvidia-siet-chip/kich-ban-v2.md`), cộng đoạn bạn tự viết nếu có. **Không** dùng lời của @MotCongNghe. Chép nguyên văn vào `mau-giong/01.md`, `02.md`. Chưa có xác nhận của bạn thì dừng ở đây.
- [ ] **Step 2:** Viết `phan-tich-giong.md` bằng đúng lệnh "Phân tích nhịp câu, độ dài câu, từ ngữ đệm và thái độ của đoạn văn bản mẫu dưới đây. Sau đó nêu quy tắc viết theo đúng phong cách đó." áp lên các mẫu. Có đúng bốn đề mục `## Nhịp câu`, `## Độ dài câu`, `## Từ đệm`, `## Thái độ`. Kiểm: `grep -c '^## ' pipeline/phong-cach/phan-tich-giong.md` in `4`.
- [ ] **Step 3:** Sửa `docs/phong-cach-kich-ban.md` mục 6: thay danh sách cụm cấm bằng dòng trỏ tới `pipeline/phong-cach/tu-cam.json`; thêm mục "Vai kể" với câu tình huống và hai ràng buộc ở spec 4 mục 3.2. Không động tới cấu trúc kịch bản (việc của kế hoạch vận hành, H0).
- [ ] **Step 4:** Sửa `video-moi/SKILL.md` mục 3–5 thành các bước: nháp bằng khung Phụ lục A của spec (chép nguyên văn khối khung); lượt 1 "Đọc lại, gạch bỏ mọi câu sáo rỗng không thêm thông tin."; lượt 2 "Viết lại sao cho đọc to thành tiếng không vấp, nghe như nói trực tiếp, không như đọc văn bản."; `uv run python -m tttc.phong_cach ../videos/<slug>` 0 Lỗi; `uv run python -m tttc.phan_bien vong 1 ../videos/<slug>` rồi điền `## Bảng triage` (cột `#, câu trích, loại, mức, nhận/bỏ, lý do`) vào `phan-bien-giong-1.md`, sửa kịch bản, chạy lại `tttc.phong_cach`; vòng 2 với `--conversation <id> --triage ../videos/<slug>/phan-bien-giong-1.md`; ghi `set_step(dir, "phan-bien-giong", "xong", "vòng 1: N mục (nhận a, bỏ b), điểm x/x/x/x; vòng 2: ...")`; sau đó `tttc.kiem`; `uv run python -m tttc.giong_vieneu thu-60s ../videos/<slug>`; render duyệt 1. Thêm: agy trả lỗi hai lần thì dùng subagent với cùng prompt (`phan_bien.dung_prompt`) và ghi note `agy lỗi, dùng subagent`; đạt khi không còn mục nặng đã nhận mà chưa sửa và bốn điểm vòng 2 ≥ 4; đúng 2 vòng.
- [ ] **Step 5:** Kiểm: `grep -n "phan_bien\|thu-60s\|phong_cach" .claude/skills/video-moi/SKILL.md` có đủ ba cụm.
- [ ] **Step 6: Commit**

```bash
git add pipeline/phong-cach docs/phong-cach-kich-ban.md .claude/skills/video-moi/SKILL.md
git commit -m "docs: mẫu giọng, vai kể, quy trình viết ba lượt và phản biện agy trong video-moi"
```

### Task 9: Nghiệm thu trên kịch bản thật

**Files:**
- Create: `docs/nghien-cuu/do-agy-2026-11-09.md`

- [ ] **Step 1:** `uv run pytest -q`. Expected: toàn bộ PASS (số test ≥ số ghi ở Task 0).
- [ ] **Step 2:** `uv run python -m tttc.phong_cach ../videos/2026-11-15-nvidia-siet-chip` và với `goi-ai-dang-tien`. Expected: `0 Lỗi, 0 cảnh báo`.
- [ ] **Step 3:** Chạy thật một vòng: `uv run python -m tttc.phan_bien vong 1 ../videos/2026-11-15-nvidia-siet-chip` (có gọi dịch vụ agy; kịch bản đã đăng nên không còn nhạy cảm trước đăng). Ghi vào `docs/nghien-cuu/do-agy-2026-11-09.md`: thời gian chạy (`duration_seconds` trong `phan-bien-giong-1.raw.json`), số vấn đề, ba mục tiêu biểu, và ý kiến của bạn về chất lượng.
- [ ] **Step 4:** Chạy `uv run python -m tttc.giong_vieneu thu-60s ../videos/2026-11-15-nvidia-siet-chip`, ghi thời gian vào cùng tệp, bạn nghe `nghe-thu.mp3`.
- [ ] **Step 5: Commit**

```bash
git add docs/nghien-cuu/do-agy-2026-11-09.md
git commit -m "docs: đo agy và nghe thử trên kịch bản thật"
```
