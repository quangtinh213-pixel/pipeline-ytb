# Nhận diện mới Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Kênh có nhận diện khác hẳn @MotCongNghe: lớp màu một nguồn (theme), bộ nhân vật 6 biểu cảm × 4 góc làm bằng TobyFlow, khung thumbnail mới, logo/avatar/banner, tên và giọng mới; đổi nhận diện sau này chỉ sửa một chỗ.

**Architecture:** `brand/theme.json` là nguồn màu duy nhất, đọc qua `tttc/theme.py`. CSS/HTML của mẫu cảnh viết `{{theme:khóa}}` và được phân giải lúc dựng (`theme.cssify`), nên với giá trị theme hiện tại đầu ra **trùng từng byte** với bây giờ (kiểm bằng test đặc trưng). `svg/ve.py`, `dung.py`, `thumb.py`, `make_brand.py` đọc hằng số từ theme. Nhân vật là PNG nền trong suốt liệt kê trong `nhan-vat/kit.json`; `canh.py` và `dung.py` đọc kit này.

**Tech Stack:** Python ≥ 3.11, pytest (`uv run`), Pillow, HyperFrames, TobyFlow MCP (Flow "Nano Banana 2.1"), CoDesign (IMG.LY) cho logo/banner.

**Spec:** `docs/superpowers/specs/2026-11-09-nhan-dien-moi-design.md`

**Thứ tự thực hiện:** sau kế hoạch giọng văn và kế hoạch vận hành (cùng sửa `trang_thai.py`/`dang.py`). Task 1–6 (lớp màu) làm trước Task 7 (quyết định của bạn). Kế hoạch hình ảnh làm phần phông và hình mới **sau** Task 6.

## Global Constraints

- Theme có tối thiểu: nền, mực, nhấn kèm 2 sắc đậm hơn, chữ-trên-nhấn, muted, đường kẻ, thanh, giấy kem (kèm sắc), 4 màu phụ `xanh`/`do`/`lam`/`tim` (mỗi màu: nhấn, bóng, bóng tối, màu chữ trên nhấn), font hiển thị. Tương phản ≥ 4,5:1 cho mực/nền, chữ-trên-nhấn/nhấn, muted/nền. Màu nhấn **không** là cặp đen–vàng và không trùng bốn màu phụ.
- Màu vật thể (cờ đỏ `#DA251D` và `#A51B15`, gỗ `#5A4426`/`#6E5430`/`#8A6A3A`, xám nền đất `#141414`…`#3A3A3A`) không thuộc theme, được viết thẳng trong `ve.py` và có trong danh sách ngoại lệ của test.
- Nhân vật: 6 biểu cảm × 4 góc (`truoc`, `nghieng-trai`, `nghieng-phai`, `ngang`) = 24 dáng, cộng 6 bản nhắm mắt cho góc `truoc`; PNG RGBA, cao 560 px (hiển thị 280×280 ở khung 1920×1080). Shorts dọc không dùng nhân vật. `dan.goc` (`phai|trai`) là vị trí trên màn hình; `dan.huong` là góc nhìn, mặc định quay vào giữa màn hình.
- Brief tạo ảnh cố định: nét viền đậm cùng độ dày với thư viện SVG, màu phẳng đúng palette, nền phẳng một màu, không chữ, không logo, không mặt người thật. TobyFlow: ảnh tham chiếu tối đa 10, 4 phương án mỗi lượt, tạo workflow tối đa 20/ngày, khoảng 150 lượt tạo ảnh; extension phải online.
- Giữ nguyên tên dịch vụ Keychain `tui-tien-cong-nghe`. Bạn tự đổi tên/handle/avatar/banner và thumbnail video cũ trong YouTube Studio.
- Chạy lệnh trong `pipeline/`. Chỉ `git add` đường dẫn cụ thể.

## Review Focus

1. Refactor sang theme không đổi một byte đầu ra khi giá trị theme bằng giá trị cũ: SVG sinh lại và `compose` giống golden (Task 1, 3, 4).
2. Đổi màu phụ theo chương: `dung.compose` thay chuỗi hex trong SVG, nên hex trong SVG phải khớp tuyệt đối bộ ba nhấn của theme (Task 4).
3. Palette mới có nhấn trùng một màu phụ hoặc tương phản thấp bị `theme.kiem` chặn (Task 2).
4. `dan` với `the`/`huong` ngoài `kit.json` bị từ chối; video cũ (không có `huong`, không có kit) vẫn dựng như trước (Task 9).
5. Ảnh nhân vật nền không phẳng, viền lẫn màu nền, hoặc ảnh hỏng: `tach_nen` báo lỗi rõ, không âm thầm xuất ảnh xấu (Task 10).

---

### Task 0: Nền sạch

- [ ] **Step 1:** `uv run pytest -q`. Expected: toàn bộ PASS (ghi số test).
- [ ] **Step 2:** `git status --short -- pipeline/tttc/dung.py pipeline/tttc/canh.py pipeline/templates/canh pipeline/svg pipeline/tttc/thumb.py brand`. Các tệp `M` là thay đổi cũ chưa commit (`dung.py`, `canh.py`, `base.css`, `minh-hoa.html`, `dong.js`). **Dừng và hỏi người dùng** commit riêng hoặc stash trước khi sửa.

### Task 1: Test đặc trưng trước khi refactor

**Files:**
- Create: `pipeline/tests/test_dac_trung.py`, `pipeline/tests/fixtures/golden-compose.sha256`

**Interfaces:**
- Produces: `golden_compose_hash(video_dir) -> str` (hàm trợ giúp trong test) = SHA-256 trên danh sách `(đường dẫn tương đối, nội dung)` đã sắp của thư mục `composition/` do `dung.compose` tạo.

- [ ] **Step 1: Viết test**

```python
def test_regenerated_svgs_are_byte_identical_to_committed(tmp_path, monkeypatch):
    import importlib.util, shutil
    from pathlib import Path
    svg_dir = Path(__file__).resolve().parents[1] / "svg"
    spec = importlib.util.spec_from_file_location("ve", svg_dir / "ve.py")
    ve = importlib.util.module_from_spec(spec); spec.loader.exec_module(ve)
    monkeypatch.setattr(ve, "OUT", tmp_path)
    for name, fn in ve.ITEMS.items():
        ve.save(name, fn())
    for f in sorted(svg_dir.glob("*.svg")):
        assert (tmp_path / f.name).read_bytes() == f.read_bytes(), f.name

def test_compose_output_is_unchanged(tmp_path):
    video = make_video(tmp_path)  # dựng thư mục video từ SCENES, TIMING, NGUON chép nguyên từ tests/test_dung.py
    assert golden_compose_hash(dung.compose(video)) == GOLDEN.read_text(encoding="utf-8").strip()
```
(`make_video` làm đúng việc của fixture `video` trong `test_dung.py`; `GOLDEN = FIX / "golden-compose.sha256"`.)

- [ ] **Step 2:** Tạo `golden-compose.sha256` bằng cách chạy hàm băm một lần trên **mã hiện tại** (trước mọi sửa đổi) và ghi giá trị vào tệp.
- [ ] **Step 3:** `uv run pytest tests/test_dac_trung.py -q`. Expected: PASS (cả hai test, trên mã chưa sửa).
- [ ] **Step 4: Commit**

```bash
git add pipeline/tests/test_dac_trung.py pipeline/tests/fixtures/golden-compose.sha256
git commit -m "test: đặc trưng hóa SVG và đầu ra compose trước khi chuyển sang theme"
```

### Task 2: `brand/theme.json` và `tttc/theme.py`

**Files:**
- Create: `brand/theme.json`, `pipeline/tttc/theme.py`, `pipeline/tests/test_theme.py`

**Interfaces:**
- Produces:
  - `THEME = brand/theme.json` (`Path`); `load(path: Path = THEME) -> dict`.
  - `cssify(text: str, th: dict | None = None) -> str`: thay mọi `{{theme:khóa}}` (khóa có thể có dấu chấm: `nhan.1`, `kem.nen`, chỉ số danh sách là số) bằng giá trị; khóa không tồn tại → `KeyError` nêu tên khóa.
  - `contrast(a: str, b: str) -> float` tỉ lệ tương phản WCAG của hai màu `#RRGGBB`.
  - `kiem(th: dict) -> list[str]`: thông báo `Lỗi:` khi mực/nền, chữ-trên-nhấn/nhấn hoặc muted/nền < 4,5; khi `nhan[0]` trùng `nhan` của bất kỳ màu phụ nào; khi `nen` = `#111111` và `nhan[0]` = `#FFC800` (cặp đen–vàng của kênh mẫu) **chỉ cảnh báo** `Cảnh báo:` nếu `th["ten"] != "hien-tai"`.
  - Hằng số dẫn xuất: `TH = load()`, `VANG: tuple[str, str, str]` = `TH["nhan"]`, `SAC: dict[str, tuple[str, str, str, str]]` từ `TH["sac"]`.
- `theme.json` phải chứa **giá trị hiện tại** đã có trong mã: `ve.py:9` (6 hằng), `dung.py:53-57` (`SAC`, `VANG`), `base.css`, các mẫu cảnh, `duyet.html`, `thumb.py:7,55`, `make_brand.py:4`. Đặt `"ten": "hien-tai"`.

- [ ] **Step 1: Viết test**

```python
def test_cssify_resolves_nested_and_indexed_keys():
    th = {"nen": "#111111", "nhan": ["#FFC800", "#E0B000"], "kem": {"nen": "#FBF6EC"}}
    assert theme.cssify("a {{theme:nen}} b {{theme:nhan.1}} c {{theme:kem.nen}}", th) == "a #111111 b #E0B000 c #FBF6EC"

def test_cssify_unknown_key_names_it():
    with pytest.raises(KeyError, match="khong_co"):
        theme.cssify("{{theme:khong_co}}", {"nen": "#111111"})

def test_contrast_known_values():
    assert theme.contrast("#000000", "#FFFFFF") == pytest.approx(21.0, abs=0.01)
    assert theme.contrast("#111111", "#FFC800") > 4.5

def test_current_theme_passes_its_own_check():
    assert [m for m in theme.kiem(theme.load()) if m.startswith("Lỗi")] == []

def test_kiem_rejects_accent_equal_to_semantic_colour_and_low_contrast():
    th = theme.load(); th["nhan"] = list(th["sac"]["lam"][:3])
    assert any("trùng" in m for m in theme.kiem(th))
    th = theme.load(); th["chu_tren_nhan"] = th["nhan"][0]
    assert any("tương phản" in m for m in theme.kiem(th))

def test_derived_constants_match_current_code():
    assert theme.VANG == ("#FFC800", "#E0B000", "#C79C00") and theme.SAC["xanh"][0] == "#00D084"
```

- [ ] **Step 2:** `uv run pytest tests/test_theme.py -q`. Expected: FAIL.
- [ ] **Step 3:** Liệt kê mọi hex hiện có: `grep -rIoh --exclude-dir=.venv -E '#[0-9A-Fa-f]{6}' tttc templates svg/ve.py ../brand | sort | uniq -c`. Điền `theme.json` và `theme.py` theo Interfaces; hex không thuộc thương hiệu (vật thể, trung tính) ghi vào danh sách ngoại lệ ở Task 6, không vào theme.
- [ ] **Step 4:** `uv run pytest tests/test_theme.py -q`. Expected: PASS.
- [ ] **Step 5: Commit**

```bash
git add brand/theme.json pipeline/tttc/theme.py pipeline/tests/test_theme.py
git commit -m "feat: theme.json và tttc.theme (cssify, contrast, kiem) với giá trị màu hiện tại"
```

### Task 3: `svg/ve.py` đọc theme

**Files:** Modify `pipeline/svg/ve.py:9` và mọi chỗ viết thẳng `"#E0B000"`, `"#C79C00"`, `"#FFC800"`; Test: `tests/test_dac_trung.py`, `tests/test_svg.py`.

**Interfaces:** Consumes `theme.TH`. `ve.INK, WHITE, LIGHT, MID, DARK` lấy từ `TH["ve"]`; `Y`, `Y2`, `Y3` từ `TH["nhan"]`; mọi `"#E0B000"` → `Y2`, `"#C79C00"` → `Y3`. Màu vật thể giữ nguyên.

- [ ] **Step 1:** Đổi `tests/test_svg.py::BRAND` thành tập sinh từ theme: `BRAND = set(theme.brand_colors())` — thêm vào `theme.py` hàm `brand_colors() -> set[str]` trả mọi màu hex (viết hoa) trong `TH["ve"]` và `TH["nhan"]`; chạy `uv run pytest tests/test_svg.py -q`. Expected: FAIL (`brand_colors` chưa có).
- [ ] **Step 2:** Implement `brand_colors`, sửa `ve.py`. Chạy `uv run pytest tests/test_svg.py tests/test_dac_trung.py tests/test_theme.py -q`. Expected: PASS (SVG sinh lại trùng byte).
- [ ] **Step 3: Commit**

```bash
git add pipeline/svg/ve.py pipeline/tttc/theme.py pipeline/tests/test_svg.py
git commit -m "refactor: ve.py đọc màu từ theme, SVG không đổi một byte"
```

### Task 4: `dung.py`, CSS và mẫu cảnh đọc theme

**Files:** Modify `pipeline/tttc/dung.py:52-57,351-352,_scene_file,compose`, `pipeline/templates/canh/base.css`, `pipeline/templates/canh/{trich-bao,b-roll,trang-nguon,nhan-vat}.html`, `pipeline/templates/duyet.html`; Test: `tests/test_dac_trung.py`, `tests/test_dung.py`.

**Interfaces:** Consumes `theme.cssify`, `theme.SAC`, `theme.VANG`. `dung.SAC`/`VANG` import từ theme. Mọi hex thương hiệu trong `base.css` và các mẫu thành `{{theme:...}}`; `compose` chạy `cssify` trên `base.css` và trên nội dung `_scene_file`; hex trong chuỗi CSS nhúng của `compose` lấy từ `TH`. `duyet.py` chạy `cssify` trên `templates/duyet.html` trước khi thay `$title...`.

- [ ] **Step 1:** Thêm test: sửa một giá trị trong bản sao theme (nhấn → `#00AAFF`) và `monkeypatch` `theme.TH`; `dung.compose` phải cho `index.html` chứa `#00AAFF` và không còn `#FFC800` ngoài danh sách ngoại lệ. Chạy `uv run pytest tests/test_dung.py -q`. Expected: FAIL.
- [ ] **Step 2:** Implement. Giữ nguyên `data-composition-id`, thứ tự và khoảng trắng để golden không đổi.
- [ ] **Step 3:** `uv run pytest tests/test_dac_trung.py tests/test_dung.py tests/test_duyet.py -q`. Expected: PASS, golden compose **không đổi**.
- [ ] **Step 4: Commit**

```bash
git add pipeline/tttc/dung.py pipeline/templates pipeline/tttc/duyet.py pipeline/tests
git commit -m "refactor: compose, base.css, mẫu cảnh và trang duyệt đọc màu từ theme"
```

### Task 5: `thumb.py` và `make_brand.py` đọc theme

**Files:** Modify `pipeline/tttc/thumb.py:7,55`, `brand/make_brand.py:4`; Test: `tests/test_thumb.py`.

**Interfaces:** `thumb.BG`, `COLORS`, `YELLOW`, `INK` suy từ `TH` (giữ tên để hàm hiện có chạy); `make_brand.py` đọc `BG, YELLOW, WHITE` từ theme. Hành vi không đổi với theme hiện tại.

- [ ] **Step 1:** Thêm test: với `theme.TH` bị `monkeypatch` đổi nền, `thumb.make([("A", "white")], out)` cho ảnh có pixel (0,0) bằng màu nền mới. Chạy `uv run pytest tests/test_thumb.py -q`. Expected: FAIL.
- [ ] **Step 2:** Implement; `uv run pytest tests/test_thumb.py -q`. Expected: PASS.
- [ ] **Step 3: Commit** `git add pipeline/tttc/thumb.py brand/make_brand.py pipeline/tests/test_thumb.py && git commit -m "refactor: thumb và make_brand đọc màu từ theme"`.

### Task 6: `tttc.theme ap-dung` và hai test chặn quay lại

**Files:** Modify `pipeline/tttc/theme.py` (thêm `ap_dung`, `main`); Create `pipeline/tests/test_theme_guard.py`, `pipeline/tests/fixtures/mau-vat-the.json`.

**Interfaces:** `ap_dung() -> list[str]`: chạy `svg/ve.py` (sinh lại toàn bộ SVG), `brand/make_brand.py` (logo), `theme.kiem(TH)`, rồi `svg/sheet.sheet(SVG_DIR, svg/thu-vien.png)`; trả các thông báo `Lỗi:`/`Cảnh báo:`. Dòng lệnh `python -m tttc.theme ap-dung` in chúng và thoát 1 nếu có `Lỗi:`.

- [ ] **Step 1: Viết test chặn**

```python
def test_no_brand_hex_hardcoded_outside_theme():
    allow = json.loads((FIX / "mau-vat-the.json").read_text(encoding="utf-8"))  # {"đường dẫn": ["#RRGGBB", ...]}
    bad = {}
    for p in SOURCES:  # tttc/*.py, templates/**/*.{html,css,js}, svg/ve.py, ../brand/make_brand.py
        for hx in set(re.findall(r"#[0-9A-Fa-f]{6}\b", p.read_text(encoding="utf-8"))):
            if hx.upper() not in {a.upper() for a in allow.get(rel(p), [])}:
                bad.setdefault(rel(p), []).append(hx)
    assert bad == {}

```
Test thứ hai (SVG trong repo khớp theme hiện tại) chính là `test_regenerated_svgs_are_byte_identical_to_committed` ở Task 1; giữ nguyên, không viết lại.

- [ ] **Step 2:** `uv run pytest tests/test_theme_guard.py -q`. Expected: FAIL (còn hex chưa phân loại).
- [ ] **Step 3:** Với mỗi hex báo lỗi: thay bằng khóa theme, hoặc thêm vào `mau-vat-the.json` kèm lý do trong khóa `"_ly_do"` (cờ, gỗ, xám nền đất, trung tính như `#000`, `#222`, màu thanh trình duyệt giả trong `trang-nguon.html`). Implement `ap_dung`/`main`.
- [ ] **Step 4:** `uv run pytest -q`. Expected: PASS toàn bộ. Chạy `uv run python -m tttc.theme ap-dung`: thoát 0, tạo `svg/thu-vien.png`.
- [ ] **Step 5: Commit**

```bash
git add pipeline/tttc/theme.py pipeline/tests/test_theme_guard.py pipeline/tests/fixtures/mau-vat-the.json
git commit -m "feat: tttc.theme ap-dung và test chặn hex thương hiệu viết cứng"
```

### Task 7: Quyết định của bạn (tên, palette, tính cách nhân vật, giọng)

**Files:** Create `docs/nghien-cuu/nhan-dien-ung-vien.md`; Modify `brand/theme.json`, `pipeline/config.json` (`vieneu.voice`).

- [ ] **Step 1: Tên + handle.** Đề xuất 8–10 tên nói được "tin nóng công nghệ–kinh tế, góc Việt Nam", không chứa "Mọt", không còn mã hóa góc túi tiền. Với mỗi tên kiểm handle: `curl -s -o /dev/null -w '%{http_code}' https://www.youtube.com/@<handle>` (404 = chưa ai dùng; kiểm lại trong Studio khi đổi). Ghi bảng vào tài liệu. **Bạn chọn một.**
- [ ] **Step 2: Palette.** Lấy thumbnail của 8–10 kênh công nghệ/kinh tế tiếng Việt (`vidiq_similar_channels` với `channelId` `UC91zSg_iPgJZZL6KB91BewQ`, cộng 3 thumbnail top của @MotCongNghe) và dựng bảng so sánh một ảnh có 3 palette ứng viên đặt cạnh. **Bạn chọn một.** Không dùng cặp đen–vàng.
- [ ] **Step 3: Tính cách nhân vật.** Bạn cho ảnh hoặc mô tả "Mọt"; tôi viết brief nhân vật (hình dạng, tính cách, điểm khác Mọt cụ thể). **Bạn xác nhận brief.**
- [ ] **Step 4: Giọng.** Chạy `uv run python -m tttc.giong_vieneu nghe-thu videos/thu-nghiem/giong "<giọng 1>" "<giọng 2>" "<giọng 3>"`; bạn nghe cả giọng của họ và các giọng này, chọn giọng khác rõ. Ghi `vieneu.voice`; nghe thử danh sách từ đệm với giọng này (kế hoạch giọng văn).
- [ ] **Step 5:** Cập nhật `brand/theme.json` với palette đã chọn (đặt `"ten"` = tên kênh), chạy `uv run python -m tttc.theme ap-dung`. Expected: không `Lỗi:`. Chạy `uv run pytest -q` (golden compose sẽ đổi: sinh lại `golden-compose.sha256` có chủ đích và ghi lý do vào commit). Bạn xem `svg/thu-vien.png` một lần.
- [ ] **Step 6: Commit** `git add brand docs/nghien-cuu/nhan-dien-ung-vien.md pipeline/config.json pipeline/svg pipeline/tests/fixtures && git commit -m "feat: palette, tên và giọng mới của kênh"`.

### Task 8: Dựng thử 10 cảnh bằng palette mới

- [ ] **Step 1:** Dựng `videos/thu-nghiem` bằng `uv run python pipeline/scripts/thu-render.py` (xem `docs/nghien-cuu/do-render-2026-11-09.md`) hoặc `dung.compose` một đoạn 10 cảnh; render `draft` bằng `scripts/render.sh <comp> <out.mp4> draft`.
- [ ] **Step 2:** `dung.contact_sheet(...)` và xem ảnh: hình, chữ, nền chương, màu phụ theo chương đều theo palette mới, không sót màu cũ. Sai thì sửa theme hoặc mẫu, không sửa tay SVG.
- [ ] **Step 3: Commit** nếu có sửa: `git add brand pipeline && git commit -m "fix: màu còn sót khi áp palette mới"`.

### Task 9: `kit.json` và nhân vật trong `canh`/`compose`

**Files:**
- Create: `pipeline/tttc/nhan_vat.py`, `pipeline/tests/test_nhan_vat.py`
- Modify: `pipeline/tttc/canh.py:15,103-109`, `pipeline/tttc/dung.py:299-321`, `pipeline/tests/test_canh.py`, `pipeline/tests/test_dung.py`

**Interfaces:**
- Produces (`nhan_vat.py`): `KIT = PIPE/"nhan-vat"/"kit.json"`; `doc_kit(path: Path = KIT) -> dict | None` (None nếu không có tệp); `hop_le(the: str, huong: str, kit: dict) -> bool` (cặp nằm trong `kit["dang"]`); `huong_mac_dinh(goc: str) -> str` (`phai` → `nghieng-trai`, `trai` → `nghieng-phai`); `tep(the: str, huong: str, nham: bool = False) -> str` = `"{the}-{huong}.png"` hoặc `"{the}-{huong}-nham.png"`. Định dạng kit: `{"the": [...], "huong": [...], "dang": [["chao","truoc"], ...], "nham": [["chao","truoc"], ...]}`.
- `canh._check_dan`: có kit thì yêu cầu `the` ∈ `kit["the"]`, `huong` (mặc định `huong_mac_dinh(goc)`) hợp lệ; không có kit thì giữ luật cũ (`DAN_THE`, `DAN_GOC`). `dung.compose`: có kit thì chép `nhan-vat/*.png` vào `assets/nv/` và dựng `<img src="assets/nv/{tep}">` kèm ảnh `-nham` nếu `nham` có cặp đó; không có kit thì như cũ (`assets/svg/tui-{the}.svg`).

- [ ] **Step 1: Viết test**

```python
KIT = {"the": ["chao", "nghi"], "huong": ["truoc", "nghieng-trai", "nghieng-phai", "ngang"],
       "dang": [["chao", "truoc"], ["chao", "nghieng-trai"], ["nghi", "truoc"]], "nham": [["chao", "truoc"]]}

def test_hop_le_and_default_direction_faces_screen_centre():
    assert nhan_vat.hop_le("chao", "nghieng-trai", KIT) and not nhan_vat.hop_le("nghi", "ngang", KIT)
    assert nhan_vat.huong_mac_dinh("phai") == "nghieng-trai" and nhan_vat.huong_mac_dinh("trai") == "nghieng-phai"

def test_tep_names():
    assert nhan_vat.tep("chao", "truoc") == "chao-truoc.png" and nhan_vat.tep("chao", "truoc", True) == "chao-truoc-nham.png"

def test_doc_kit_missing_file_is_none(tmp_path):
    assert nhan_vat.doc_kit(tmp_path / "khong-co.json") is None
```
Trong `test_canh.py`: với `kit` (truyền qua tham số `validate(..., kit=KIT)` hoặc `monkeypatch` `nhan_vat.doc_kit`) `dan: {"the": "chao", "huong": "ngang"}` → `Lỗi:` chứa "huong"; `dan: {"the": "chao"}` ở `goc: "phai"` → không lỗi; không có kit và `the: "chao"` → như cũ. Trong `test_dung.py`: có kit và PNG giả trong thư mục tạm → `index.html` chứa `assets/nv/chao-nghieng-trai.png` và tệp được chép; không có kit → vẫn `assets/svg/tui-chao.svg`.

- [ ] **Step 2:** `uv run pytest tests/test_nhan_vat.py tests/test_canh.py tests/test_dung.py -q`. Expected: FAIL.
- [ ] **Step 3:** Implement. Cho `canh.validate` nhận kiểm kit qua `nhan_vat.doc_kit()` mặc định (có tham số `kit` để test). Cập nhật docstring đầu `dung.py` ghi `dan.huong`.
- [ ] **Step 4:** `uv run pytest -q`. Expected: PASS.
- [ ] **Step 5: Commit**

```bash
git add pipeline/tttc/nhan_vat.py pipeline/tests pipeline/tttc/canh.py pipeline/tttc/dung.py
git commit -m "feat: nhân vật dẫn chuyện đọc từ kit.json với biểu cảm và góc nhìn"
```

### Task 10: Công cụ tách nền và bảng soi 30 dáng

**Files:** Create `pipeline/tttc/tach_nen.py`, `pipeline/tests/test_tach_nen.py`

**Interfaces:**
- Produces: `tach_nen(src: Path, out: Path, nguong: int = 28, mem: int = 24, cao: int = 560) -> Path`: màu nền = trung vị 4 góc; alpha 0 khi khoảng cách màu ≤ `nguong`, tăng tuyến tính đến 255 ở `nguong + mem`; cắt sát vùng alpha > 8 cộng lề 8 px; đổi cỡ về chiều cao `cao` (LANCZOS); ghi PNG RGBA. `ValueError` khi bốn góc chênh nhau quá 30 (nền không phẳng) hoặc không còn điểm ảnh đối tượng. `bang_soi(thu_muc: Path, out: Path, cot: int = 6) -> Path`: lưới các PNG, mỗi ô vẽ trên nền ca-rô và ghi tên tệp.

- [ ] **Step 1: Viết test** với ảnh tổng hợp:

```python
def _img(tmp_path, bg=(10, 200, 10), corners=None):
    im = Image.new("RGB", (200, 300), bg)
    ImageDraw.Draw(im).ellipse([60, 80, 140, 220], fill=(255, 200, 0), outline=(17, 17, 17), width=6)
    p = tmp_path / "a.png"; im.save(p); return p

def test_tach_nen_makes_background_transparent_and_crops_and_resizes(tmp_path):
    out = tach_nen.tach_nen(_img(tmp_path), tmp_path / "o.png", cao=560)
    im = Image.open(out)
    assert im.mode == "RGBA" and im.height == 560
    assert im.getpixel((0, 0))[3] == 0 and im.getpixel((im.width // 2, im.height // 2))[3] == 255

def test_tach_nen_rejects_non_flat_background(tmp_path):
    im = Image.new("RGB", (100, 100), (0, 0, 0))
    for xy in [(99, 99), (0, 99), (99, 0)]:  # ba góc trắng, một góc đen: nền không phẳng
        im.putpixel(xy, (255, 255, 255))
    im.save(tmp_path / "b.png")
    with pytest.raises(ValueError, match="nền"):
        tach_nen.tach_nen(tmp_path / "b.png", tmp_path / "o.png")

def test_tach_nen_rejects_empty_subject(tmp_path):
    Image.new("RGB", (100, 100), (5, 5, 5)).save(tmp_path / "c.png")
    with pytest.raises(ValueError, match="đối tượng"):
        tach_nen.tach_nen(tmp_path / "c.png", tmp_path / "o.png")

def test_bang_soi_one_tile_per_png(tmp_path):
    for n in ("chao-truoc", "nghi-ngang"):
        Image.new("RGBA", (50, 80), (255, 0, 0, 255)).save(tmp_path / f"{n}.png")
    assert Image.open(tach_nen.bang_soi(tmp_path, tmp_path / "bang.png", cot=2)).width > 100
```

- [ ] **Step 2:** `uv run pytest tests/test_tach_nen.py -q`. Expected: FAIL.
- [ ] **Step 3:** Implement bằng Pillow (`ImageChops`/vòng lặp pixel; ảnh ≤ 2K nên đủ nhanh).
- [ ] **Step 4:** `uv run pytest tests/test_tach_nen.py -q`. Expected: PASS.
- [ ] **Step 5: Commit** `git add pipeline/tttc/tach_nen.py pipeline/tests/test_tach_nen.py && git commit -m "feat: tách nền phẳng và bảng soi nhân vật"`.

### Task 11: Tạo bộ nhân vật bằng workflow TobyFlow (có bạn duyệt)

**Files:** Modify `pipeline/tttc/nhan_vat.py` (thêm `tao_prompt`), Test `pipeline/tests/test_nhan_vat.py`; Create `pipeline/nhan-vat/*.png`, `pipeline/nhan-vat/kit.json`, `docs/nghien-cuu/nhan-vat-tobyflow.md`.

**Interfaces:** `BIEU_CAM: dict[str, str]` (6 biểu cảm → mô tả tiếng Anh), `GOC: dict[str, str]` (4 góc → mô tả), `BRIEF: str` (brief cố định bằng tiếng Anh, có chỗ chèn palette); `tao_prompt(the: str, huong: str, nham: bool = False) -> str` ghép nhân vật + biểu cảm + góc + `BRIEF` với các mã màu của `theme.TH`; `nham=True` thêm "eyes closed".

- [ ] **Step 1: Viết test**

```python
def test_prompt_has_brief_expression_angle_and_palette():
    p = nhan_vat.tao_prompt("ngac-nhien", "nghieng-trai")
    assert "no text" in p and "no logo" in p and "no real person" in p and "flat" in p
    assert nhan_vat.BIEU_CAM["ngac-nhien"] in p and nhan_vat.GOC["nghieng-trai"] in p
    assert theme.TH["nhan"][0] in p and "eyes closed" not in p
    assert "eyes closed" in nhan_vat.tao_prompt("chao", "truoc", nham=True)

def test_six_expressions_and_four_angles_defined():
    assert len(nhan_vat.BIEU_CAM) == 6 and len(nhan_vat.GOC) == 4
```

- [ ] **Step 2:** `uv run pytest tests/test_nhan_vat.py -q`. Expected: FAIL. Implement; Expected: PASS. Commit `git add pipeline/tttc/nhan_vat.py pipeline/tests/test_nhan_vat.py && git commit -m "feat: tao_prompt cho bộ nhân vật"`.
- [ ] **Step 3 (cần bạn):** Mở sidebar TobyFlow và đăng nhập. Kiểm bằng `get_provider_status` (provider `flow`, `media_type` `image`) rồi `get_job` đến khi `completed`; `EXTENSION_OFFLINE` thì dừng, nhờ bạn bật lại.
- [ ] **Step 4: Dựng workflow ba pha** bằng `create_workflow` (mẫu node lấy từ `list_workflow_templates`, ghi trong tệp kết quả công cụ đã lưu; các loại node: `text`, `image`, `generate`, `download`): (a) **concept:** 4–6 prompt chữ từ brief nhân vật ở Task 7, ảnh 1:1, 4 phương án mỗi prompt; **bạn chọn một concept**; (b) **bản xoay** 4 góc dùng concept làm ảnh tham chiếu; (c) **24 dáng + 6 bản nhắm mắt** với `tao_prompt`, concept và bản xoay làm ảnh tham chiếu (tối đa 10), 4 phương án mỗi lượt. Chạy bằng `run_workflow`, theo dõi `get_job`, giữ kết quả thành công khi một lượt thất bại, không phát lại lượt không rõ trạng thái.
- [ ] **Step 5:** Tải ảnh về `videos/thu-nghiem/nhan-vat-tho/`, chọn mỗi dáng một phương án (Claude đề xuất theo độ nhất quán; **bạn duyệt**), chạy `tach_nen` từng ảnh vào `pipeline/nhan-vat/`, dựng `bang_soi`, ghi `kit.json` chỉ gồm các dáng đã duyệt. Dáng lệch nhân vật thì bỏ hoặc tạo lại, không giữ dáng lỗi. Ghi số lượt tạo, thời gian, các dáng bỏ vào `docs/nghien-cuu/nhan-vat-tobyflow.md`.
- [ ] **Step 6:** Dựng thử một cảnh mỗi biểu cảm × góc (`dung.compose` trên canh thử có `dan`), xem nhân vật hiện đúng lúc nói `tu`, nhấp nhô, chớp mắt ở góc `truoc`. `uv run pytest -q`. Expected: PASS.
- [ ] **Step 7: Commit** `git add pipeline/nhan-vat docs/nghien-cuu/nhan-vat-tobyflow.md && git commit -m "feat: bộ nhân vật 6×4 từ TobyFlow"`. Gỡ 6 tệp `svg/tui-*.svg` và mục tương ứng trong `ve.py:ITEMS` **chỉ sau khi bạn duyệt bộ mới**, rồi `uv run python -m tttc.theme ap-dung`, `uv run pytest -q`, commit riêng.

### Task 12: Khung thumbnail mới

**Files:** Modify `pipeline/tttc/thumb.py` (thay `chia_doi`), `pipeline/tests/test_thumb.py`, `.claude/skills/video-dung/SKILL.md` (mục 6).

- [ ] **Step 1 (cần bạn):** Dùng CoDesign (nạp `codesign:handbook`, `codesign:api`, `codesign:judge` trước `edit` đầu tiên) dựng 3 bố cục thumbnail 1280×720 **khác hẳn** khuôn của họ (không chia đôi răng cưa, không hai hộp chữ vàng, không vòng "VS"), dùng palette mới. Đặt cạnh 3 thumbnail top của @MotCongNghe và thumbnail 8–10 kênh khác ở 168 px. **Bạn chọn một bố cục** và xác nhận nhìn là phân biệt được ngay.
- [ ] **Step 2: Viết test** cho hàm mới `thumb.khung(anh_chinh: Path | None, anh_phu: Path, dong: list[str], out: Path, ghi_cong: str = "") -> tuple[Path, Path]`:

```python
def test_khung_makes_1280x720_and_168px_and_validates_lines(tmp_path):
    a = tmp_path / "a.png"; Image.new("RGB", (800, 800), (40, 40, 40)).save(a)
    big, small = thumb.khung(None, a, ["MỘT", "HAI"], tmp_path / "t.png", "Ảnh: X")
    assert Image.open(big).size == (1280, 720) and Image.open(small).size == (168, 94)
    with pytest.raises(ValueError):
        thumb.khung(None, a, ["A", "B", "C"], tmp_path / "t2.png")
```
Chạy `uv run pytest tests/test_thumb.py -q`. Expected: FAIL.
- [ ] **Step 3:** Implement theo bố cục đã chọn, màu từ `theme.TH`. Xóa `_zigzag`, `chia_doi`, `TEETH`, `TOOTH_AMP` và test cũ của chúng. Cập nhật mục 6 của `video-dung/SKILL.md`: thay phương án chia đôi bằng `thumb.khung`.
- [ ] **Step 4:** `uv run pytest -q`. Expected: PASS. Mở bản `-168px`: đọc ra chữ.
- [ ] **Step 5: Commit** `git add pipeline/tttc/thumb.py pipeline/tests/test_thumb.py .claude/skills/video-dung/SKILL.md && git commit -m "feat: khung thumbnail mới, bỏ khuôn chia đôi răng cưa"`.

### Task 13: Logo, avatar, banner

**Files:** Create `brand/logo-<tên>.png`, `brand/avatar-800.png`, `brand/banner-2560x1440.png`; Modify `brand/make_brand.py`.

- [ ] **Step 1 (cần bạn):** Dùng CoDesign (hoặc TobyFlow) tạo logo/avatar đọc rõ ở 98 px, banner có tên kênh và câu định vị; palette mới. Cỡ theo hiểu biết của tôi, chưa kiểm lại: avatar 800×800, banner 2560×1440 với vùng an toàn 1546×423 ở giữa. **Bạn duyệt**; sai cỡ thì theo bảng YouTube hiện hành.
- [ ] **Step 2:** Cập nhật `make_brand.py` ghi ra tên mới và cỡ 98 px của logo; chạy `uv run python ../brand/make_brand.py`. Expected: tệp tồn tại, ảnh 98 px đọc rõ.
- [ ] **Step 3: Commit** `git add brand && git commit -m "feat: logo, avatar, banner của nhận diện mới"`.

### Task 14: Áp lên kênh và dọn tên cũ

- [ ] **Step 1:** Đổi chuỗi tên ở `pipeline/pyproject.toml` (`description`), `pipeline/tttc/anh.py:11` (`UA`) và `pipeline/tests/test_anh.py:36`, ba mô tả SKILL (nếu còn); giữ `KR = "tui-tien-cong-nghe"` trong `dang.py`. `uv run pytest -q`. Expected: PASS.
- [ ] **Step 2 (bạn làm trong YouTube Studio):** đổi tên, handle, avatar, banner; đổi thumbnail video nvidia đã đăng. YouTube giới hạn số lần đổi tên/handle trong một khoảng thời gian (tôi chưa kiểm giới hạn hiện hành): kiểm trước khi bấm.
- [ ] **Step 3:** Cập nhật `svg/README.md` (bảng màu, nhóm hình) và `docs/phong-cach-kich-ban.md` mục 7 (bảng màu) theo palette mới. Commit: `git add pipeline docs && git commit -m "chore: đổi tên kênh và tài liệu theo nhận diện mới"`.
