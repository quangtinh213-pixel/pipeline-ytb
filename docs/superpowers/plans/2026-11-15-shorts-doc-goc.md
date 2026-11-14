# Shorts dọc gốc – Kế hoạch thực hiện

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Mỗi Short có kịch bản riêng, giọng đọc mới và hình dựng bằng bộ mẫu cảnh dọc 1080×1920 phủ kín khung, thay cho sân khấu ngang thu nhỏ.

**Architecture:** Nguồn của Short nằm ở `videos/<slug>/ngan/<k>/` (kịch bản, `canh.json` có `"khuon": "doc"`, giọng), dùng chung `nguon.json` và ảnh của thư mục cha. `dung.compose` thêm một nhánh "dọc gốc" đọc mẫu từ `templates/canh-doc/`; nhánh cũ giữ nguyên. Ba máy kiểm mới (`phong_cach.kiem_short`, phần dọc của `canh.validate`, `chat_luong.kiem_short`) chặn lỗi trước khi người dùng duyệt.

**Tech Stack:** Python 3 (uv, pytest), HyperFrames + GSAP (mẫu cảnh HTML), ffmpeg/ffprobe, VieNeu TTS.

**Spec:** `docs/superpowers/specs/2026-11-15-shorts-doc-goc-design.md`

## Global Constraints

- Code, comment, thông báo lỗi, commit viết tiếng Việt; commit dạng `feat:` / `fix:` / `chore:`.
- Chạy test trong `pipeline/`: `uv run pytest -q`. Lệnh đọc tiếng Việt qua subprocess cần `PYTHONUTF8=1` và `PYTHONIOENCODING=utf-8`.
- Không đổi cách dựng video ngang. Mọi test hiện có trong `tests/test_dung.py`, `test_canh.py`, `test_chat_luong.py` phải qua mà không sửa.
- Thông báo của máy kiểm bắt đầu bằng `Lỗi: ` (phải sửa) hoặc `Cảnh báo: ` (nên xem), như các hàm kiểm hiện có.
- Mọi số trong lời và trên hình của Short phải có `[#id]` trong `nguon.json` của thư mục cha.
- Khung Short đúng 1080×1920. Vùng an toàn: 220 px trên, 380 px dưới, 140 px mép phải. Cỡ chữ tối thiểu 56 px; nguồn và ghi công 30 px.
- Thời lượng Short 30–55 giây. Quãng nghỉ giọng Shorts: `pause_cau = 0.10`, `pause_doan = 0.10`.
- Không tự chạy `duyet-short`, không tự đăng. Người dùng xem từng Short rồi mới duyệt.
- Giới hạn đã biết ghi bằng comment `shortcut: <giới hạn>, <khi nào nâng cấp>`.

## Review Focus

1. Kịch bản Short chưa có phần lời đọc (tệp rỗng hoặc chỉ có tiêu đề): `kiem_short` trả một dòng `Lỗi:` rõ ràng, không ném ngoại lệ. → Task 1.
2. `canh.json` dọc trỏ tới ảnh không có trong thư mục cha: `canh.validate` báo `Lỗi:` nêu tên tệp, không để hỏng lúc render. → Task 3.
3. `compose` gặp `"khuon": "doc"` cùng với `scene_range`: ném `ValueError` nói rõ Short dọc gốc không cắt từ video dài. → Task 4.
4. Chữ hook hoặc con số quá dài so với khung 1080 px: `canh.validate` cảnh báo khi `so` hiển thị dài hơn 12 ký tự hoặc `chu` hơn 8 từ. → Task 3.
5. Mục Short cũ trong `dong-goi.json` không có `khuon` và `mo_ta`: `dang._upload_short` vẫn chạy, dùng mô tả chung và ghi `khuon_short = cu`. → Task 7.

## Bản đồ tệp

| Tệp | Việc |
|---|---|
| `pipeline/tttc/phong_cach.py` | thêm `kiem_short` |
| `pipeline/tttc/giong_vieneu.py`, `pipeline/config.json` | cấu hình quãng nghỉ Shorts |
| `pipeline/tttc/canh.py` | nhận mẫu dọc, kiểm trường của từng mẫu |
| `pipeline/templates/canh-doc/{moc,bang-chung,anh,doi-chieu,ket}.html` | 5 mẫu cảnh dọc (mới) |
| `pipeline/tttc/dung.py` | nhánh dọc gốc của `compose`, `trich_khung` |
| `pipeline/tttc/chat_luong.py` | thêm `kiem_short` |
| `pipeline/tttc/theo_doi.py`, `pipeline/tttc/dang.py` | hai cột sổ, mô tả riêng của Short |
| `.gitignore`, `.claude/skills/video-dung/SKILL.md`, `docs/template-kich-ban.md` | quy trình mới |

---

### Task 1: Máy kiểm kịch bản Short

**Files:**
- Modify: `pipeline/tttc/phong_cach.py`
- Test: `pipeline/tests/test_phong_cach.py`

**Interfaces:**
- Consumes: `tts.spoken_paragraphs(script_md, keep_tags=True)`, `tts.TAG`, `giong_vieneu.cau(paragraph)`, `tieu_de.TU_GIAT_GAN`, `tieu_de._co(pats, text)`, `phong_cach.uoc_tinh_phut(script_md, wpm)`.
- Produces: `phong_cach.kiem_short(script_md: str, wpm: float = 237) -> list[str]`. Hằng số: `SHORT_GIAY = (30, 55)`, `CAU_DAU_MAX_TU = 22`, `TU_NOI_DAU = ("thứ nhất", "còn", "vậy", "và", "nhưng", "tiếp theo", "ngoài ra")`, `NOI_VE_KE = re.compile(r"mình đọc lại|chi tiết lạ|một dòng nhỏ|ít ai đọc|video trước|dưới mô tả|đường dẫn", re.I)`.

- [ ] **Step 1: Viết test (chưa qua)**

Dùng cách dựng kịch bản mẫu sẵn có trong `test_phong_cach.py` (phần "Lời đọc"). Thân bài mẫu đủ khoảng 150 từ để ước 38 giây.

```python
def test_kiem_short_kich_ban_sach_khong_co_loi():
    assert [m for m in phong_cach.kiem_short(SHORT_SACH) if m.startswith("Lỗi")] == []

def test_kiem_short_cau_dau_mo_bang_tu_noi_la_loi():
    msgs = phong_cach.kiem_short(short("Thứ nhất, bản vá đã có từ tháng mười [#1]."))
    assert any(m.startswith("Lỗi") and "từ nối" in m for m in msgs)

def test_kiem_short_cau_dau_thieu_so_co_nguon_la_loi():
    msgs = phong_cach.kiem_short(short("Lệnh cấm nhập máy cũ làm nhiều người lo."))
    assert any(m.startswith("Lỗi") and "[#id]" in m for m in msgs)

def test_kiem_short_ngoai_30_55_giay_la_loi():
    assert any(m.startswith("Lỗi") and "giây" in m for m in phong_cach.kiem_short(short(CAU_DAU_TOT, so_tu_than=20)))
    assert any(m.startswith("Lỗi") and "giây" in m for m in phong_cach.kiem_short(short(CAU_DAU_TOT, so_tu_than=320)))

def test_kiem_short_tu_giat_gan_va_cham_than_la_loi():
    assert any(m.startswith("Lỗi") for m in phong_cach.kiem_short(short("Sốc, iPhone cũ còn mười lăm triệu [#1]!")))

def test_kiem_short_canh_bao():
    dai = "iPhone mười lăm cũ [#1] " + "rất " * 22 + "đắt."
    assert any(m.startswith("Cảnh báo") and "22" in m for m in phong_cach.kiem_short(short(dai)))
    assert any(m.startswith("Cảnh báo") and "câu hỏi" in m
               for m in phong_cach.kiem_short(short("Máy cũ mười lăm triệu [#1], đắt không? Có nên mua không?")))
    assert any(m.startswith("Cảnh báo") and "video trước" in m
               for m in phong_cach.kiem_short(short(CAU_DAU_TOT + " Như video trước đã nói.")))

def test_kiem_short_chua_co_loi_doc_tra_mot_loi_ro():
    assert phong_cach.kiem_short("# Tiêu đề\n\nLoại: shorts\n") == ["Lỗi: kịch bản Short chưa có phần lời đọc"]
```

- [ ] **Step 2: Chạy, xác nhận hỏng**

Run: `uv run pytest tests/test_phong_cach.py -k kiem_short -q`
Expected: FAIL, `AttributeError: ... kiem_short`.

- [ ] **Step 3: Viết `kiem_short` trong `phong_cach.py`**

Câu đầu = câu thứ nhất của đoạn lời đọc thứ nhất (tách bằng `giong_vieneu.cau`). "Hai câu đầu có hơn một câu hỏi" đếm dấu `?` trong hai câu đầu. Thời lượng ước = `uoc_tinh_phut(script_md, wpm) * 60`. Bảng luật và mức ở spec mục 4.2.

- [ ] **Step 4: Chạy, xác nhận qua**

Run: `uv run pytest tests/test_phong_cach.py -q`
Expected: PASS toàn tệp.

- [ ] **Step 5: Commit**

```bash
git add pipeline/tttc/phong_cach.py pipeline/tests/test_phong_cach.py
git commit -m "feat: máy kiểm kịch bản Short (câu đầu là hook, 30–55 giây)"
```

---

### Task 2: Quãng nghỉ giọng cho Shorts

**Files:**
- Modify: `pipeline/tttc/giong_vieneu.py`, `pipeline/config.json` (thêm `vieneu.shorts`)
- Test: `pipeline/tests/test_giong_vieneu.py`

**Interfaces:**
- Consumes: `giong_vieneu._cfg(cfg)`, `DEFAULT`.
- Produces: `giong_vieneu.cfg_shorts(cfg: dict | None = None) -> dict`: cấu hình VieNeu đầy đủ, trong đó các khóa của `cfg["shorts"]` ghi đè lên cấp trên; mặc định `{"pause_cau": 0.10, "pause_doan": 0.10}`. Gọi: `synthesize(ngan_dir, cfg_shorts())`.

- [ ] **Step 1: Viết test (chưa qua)**

```python
def test_cfg_shorts_mac_dinh_nghi_0_10():
    c = giong_vieneu.cfg_shorts({})
    assert (c["pause_cau"], c["pause_doan"]) == (0.10, 0.10)
    assert c["voice"] == giong_vieneu.DEFAULT["voice"]

def test_cfg_shorts_ghi_de_tu_config_va_giu_khoa_khac():
    c = giong_vieneu.cfg_shorts({"voice": "A", "pause_cau": 0.2, "shorts": {"pause_cau": 0.08, "toc_do": 1.05}})
    assert (c["voice"], c["pause_cau"], c["pause_doan"], c["toc_do"]) == ("A", 0.08, 0.10, 1.05)

def test_cfg_thuong_khong_bi_shorts_anh_huong():
    assert giong_vieneu._cfg({"shorts": {"pause_cau": 0.08}})["pause_cau"] == giong_vieneu.DEFAULT["pause_cau"]
```

- [ ] **Step 2: Chạy, xác nhận hỏng** — `uv run pytest tests/test_giong_vieneu.py -k shorts -q` → FAIL.
- [ ] **Step 3: Viết `cfg_shorts`; thêm `"shorts": {"pause_cau": 0.10, "pause_doan": 0.10}` vào `config.json:vieneu`.**
- [ ] **Step 4: Chạy** — `uv run pytest tests/test_giong_vieneu.py -q` → PASS.
- [ ] **Step 5: Commit** — `git commit -m "feat: quãng nghỉ giọng 0,10 giây cho Shorts"`

---

### Task 3: `canh.validate` nhận mẫu dọc

**Files:**
- Modify: `pipeline/tttc/canh.py`
- Test: `pipeline/tests/test_canh.py`

**Interfaces:**
- Produces:
  - `canh.MAU_DOC = {"moc", "bang-chung", "anh", "doi-chieu", "ket"}`.
  - `validate(scenes, timing, svg_dir=SVG_DIR, nguon=(), video_dir=None, kit=DOC_KIT, goc: Path | None = None)`. `goc` là thư mục chứa `anh/`, `broll/`, `nguon/` (thư mục cha của Short); không truyền thì dùng `video_dir`.
  - Khi `scenes.get("khuon") == "doc"`: chỉ mẫu trong `MAU_DOC` hợp lệ. Khi không: mẫu trong `MAU_DOC` là lỗi "mẫu dọc chỉ dùng cho Short".
  - Trường của từng mẫu dọc (Task 4, 5 đọc đúng các tên này):

| Mẫu | Bắt buộc | Tùy chọn |
|---|---|---|
| `moc` | `chu` (≤ 8 từ) | `so` (chuỗi hiển thị), `nhan`, `nguon_id` |
| `bang-chung` | `anh` (đường dẫn tương đối trong `goc`), `vung` = `[x, y, w, h]` mỗi số trong 0–1, `tom_tat` (≤ 14 từ), `nguon_id` | |
| `anh` | đúng một trong `anh` / `video` | `diem_giu` = `[x, y]` trong 0–1 (mặc định `[0.5, 0.5]`), `nhan` |
| `doi-chieu` | `tren`, `duoi`: mỗi vế `{"nhan": str, "so": str}` | `noi_bat` ∈ `{"tren", "duoi"}`, `nguon_id` |
| `ket` | `chu` | `so`, `nguon_id` |

- [ ] **Step 1: Viết test (chưa qua)**

Dựng `canh` và `timing` bằng hàm trợ giúp sẵn có trong `test_canh.py`. Mỗi test một luật:

```python
def test_khuon_doc_chap_nhan_nam_mau_doc(tmp_path): ...        # không có dòng "Lỗi"
def test_khuon_doc_tu_choi_mau_ngang(): ...                    # "so-lon" trong khuon doc → Lỗi "mẫu không có"
def test_mau_doc_ngoai_khuon_doc_la_loi(): ...                 # "moc" khi không có khuon → Lỗi "chỉ dùng cho Short"
def test_moc_chu_qua_8_tu_canh_bao(): ...                      # Cảnh báo có "8 từ"
def test_moc_so_dai_hon_12_ky_tu_canh_bao(): ...               # so="15.890.000 đồng" → Cảnh báo có "12"
def test_bang_chung_thieu_anh_trong_thu_muc_cha_la_loi(tmp_path): ...   # goc=tmp_path, anh="nguon/x.png" không có → Lỗi có "nguon/x.png"
def test_bang_chung_vung_ngoai_0_1_la_loi(): ...               # vung=[0.2, 0.2, 1.3, 0.1]
def test_anh_phai_co_dung_mot_trong_anh_video(): ...           # cả hai hoặc không cái nào → Lỗi
def test_doi_chieu_thieu_ve_la_loi(): ...
def test_so_tren_hinh_doc_phai_khop_nguon(): ...               # moc so="16,5 triệu", nguồn [#1] ghi 15,89 triệu → Lỗi như so-lon
```

- [ ] **Step 2: Chạy, xác nhận hỏng** — `uv run pytest tests/test_canh.py -k "doc or moc or bang_chung or doi_chieu" -q` → FAIL.
- [ ] **Step 3: Sửa `canh.py`**: thêm `MAU_DOC`, tham số `goc`, hàm `_check_doc(c, goc) -> list[str]`; mở rộng `_check_values` để `so` của `moc`/`ket` và `tren.so`/`duoi.so` của `doi-chieu` được đối chiếu với nguồn `nguon_id` theo cùng cách với `so-lon`.
- [ ] **Step 4: Chạy** — `uv run pytest tests/test_canh.py tests/test_canh_moi.py tests/test_canh_remap.py -q` → PASS.
- [ ] **Step 5: Commit** — `git commit -m "feat: canh.validate nhận 5 mẫu cảnh dọc của Short"`

---

### Task 4: Nhánh dọc gốc của `compose` và mẫu `moc`

**Files:**
- Create: `pipeline/templates/canh-doc/moc.html`
- Modify: `pipeline/tttc/dung.py`
- Test: `pipeline/tests/test_dung.py`

**Interfaces:**
- Consumes: tên trường mẫu ở Task 3.
- Produces:
  - `dung.TPL_DOC = PIPE / "templates" / "canh-doc"`.
  - `PREFIX` thêm: `"moc": "mc-"`, `"bang-chung": "bc-"`, `"anh": "ad-"`, `"doi-chieu": "dc-"`, `"ket": "kc-"`.
  - `dung.AN_TOAN = {"tren": 220, "duoi": 380, "phai": 140}`; ở chế độ dọc gốc, `#root` của trang ghép có `--at-tren:220px; --at-duoi:380px; --at-phai:140px`. Mẫu dọc chỉ lấy vùng an toàn qua ba biến này.
  - `compose(video_dir, w=1920, h=1080, scene_range=None, out="composition", short_hook=None, short_cta=..., goc=None) -> Path`. Chế độ dọc gốc bật khi `canh.json` có `"khuon": "doc"`; khi đó khung là 1080×1920 bất kể `w`, `h`; `goc` (mặc định `video_dir`) là nơi đọc `nguon.json`, `anh/`, `broll/`, `nguon/` và hai tệp `ghi-cong.json`.

Hành vi chế độ dọc gốc (spec mục 4.5):
- Mỗi cảnh: `data-width="1080" data-height="1920"`, mẫu đọc từ `TPL_DOC`.
- Không có `#san-khau`, `#short-hook`, `#short-cta`, không có phần tử `id="tr-…"`. Mỗi đường nối cảnh chỉ thêm tiếng `whoosh-short` âm lượng 0,25. Mẫu dọc không có tiếng riêng theo mẫu.
- Phụ đề: `phu_de(..., doc=True)` như nhánh dọc cũ, `.cap` đặt `bottom: 420px`.
- Nhãn `boi`: tọa độ nhân 1080 và 1920.
- `scene_range` khác `None` → `ValueError("Short dọc gốc có canh.json riêng, không cắt từ video dài (bỏ scene_range)")`.
- Nhạc nền, hạt nhiễu, viền tối như hiện có.

Mẫu `moc.html`: khung 1080×1920; `chu` là khối chữ lớn, `so` là con số lớn nhất khung, `nhan` dòng dưới, dòng nguồn 30 px. Chữ và số **không** đi từ trong suốt: hiệu ứng vào chỉ là phóng từ 1,08 về 1. Số dài tự co cỡ chữ để vừa bề rộng trừ vùng an toàn (cách làm như `so-lon.html`).

- [ ] **Step 1: Viết test (chưa qua)**

Thêm fixture `ngan(video)` trong `test_dung.py`: tạo `video/ngan/1/` với `canh.json` = `{"khuon": "doc", "scenes": [moc 0–3 s, moc 3–6 s]}`, `giong.mp3` và `giong-timing.json` (dùng `_tone` và cách tạo timing của fixture `video`); `nguon.json` và `anh/` chỉ có ở thư mục cha.

```python
def test_compose_doc_khong_co_san_khau_thu_nho(ngan, video):
    html = (dung.compose(ngan, goc=video) / "index.html").read_text(encoding="utf-8")
    assert 'id="san-khau"' not in html and 'id="short-hook"' not in html and 'id="short-cta"' not in html
    assert 'data-width="1080" data-height="1920"' in html and 'data-width="1920"' not in html
    assert 'id="tr-' not in html
    assert "--at-tren:220px" in html and "--at-duoi:380px" in html and "--at-phai:140px" in html

def test_compose_doc_doc_nguon_va_anh_tu_thu_muc_cha(ngan, video):
    out = dung.compose(ngan, goc=video)
    assert (out / "assets" / "anh").is_dir()
    assert "Nguồn:" in _host_vals((out / "index.html").read_text(encoding="utf-8"))[0]["nguon"]

def test_compose_doc_co_whoosh_o_duong_noi(ngan, video):
    html = (dung.compose(ngan, goc=video) / "index.html").read_text(encoding="utf-8")
    assert 'src="assets/sfx/whoosh-short.mp3" data-start="2.7"' in html

def test_compose_doc_tu_choi_scene_range(ngan, video):
    with pytest.raises(ValueError, match="scene_range"):
        dung.compose(ngan, goc=video, scene_range=(0, 1))

def test_mau_moc_khung_0_da_du_chu():
    t = (dung.TPL_DOC / "moc.html").read_text(encoding="utf-8")
    assert 'data-width="1080" data-height="1920"' in t
    assert not re.search(r'fromTo\("#mc-(?:chu|so)"[^)]*?\{[^}]*opacity:\s*0', t)
    assert all(v in t for v in ("var(--at-tren)", "var(--at-duoi)", "var(--at-phai)"))

def test_compose_vertical_cu_van_thu_nho(video):   # nhánh cũ không đổi
    html = (dung.compose(video, w=1080, h=1920, scene_range=(0, 2), out="short-1") / "index.html").read_text(encoding="utf-8")
    assert 'id="san-khau"' in html
```

(Nếu dòng nguồn của fixture không bắt đầu bằng "Nguồn:", khẳng định bằng chuỗi mà `_source_line` trả cho nguồn `[#1]` của fixture.)

- [ ] **Step 2: Chạy, xác nhận hỏng** — `uv run pytest tests/test_dung.py -k "doc or moc" -q` → FAIL.
- [ ] **Step 3: Viết `moc.html`; sửa `dung.py`** (`TPL_DOC`, `PREFIX`, `AN_TOAN`, `DEFAULT_STEPS["moc"] = []`, `_scene_file` nhận thư mục mẫu, `_vars` cho `moc`, nhánh dọc gốc trong `compose`). Ghi `# shortcut: Short dọc gốc chưa có nhân vật và thanh chương; thêm khi tỉ lệ ở lại đã vượt 40%`.
- [ ] **Step 4: Chạy** — `uv run pytest tests/test_dung.py -q` → PASS toàn tệp.
- [ ] **Step 5: Kiểm bằng HyperFrames** — dựng một `ngan/1` thử trong `videos/thu-nghiem/` (đã nằm trong `.gitignore`), chạy `scripts/render.sh` ở chế độ nháp, mở khung t = 0: chữ và số đã hiện đủ.
- [ ] **Step 6: Commit** — `git commit -m "feat: compose dựng Short dọc gốc 1080×1920, mẫu moc"`

---

### Task 5: Bốn mẫu dọc còn lại

**Files:**
- Create: `pipeline/templates/canh-doc/bang-chung.html`, `anh.html`, `doi-chieu.html`, `ket.html`
- Modify: `pipeline/tttc/dung.py` (`_vars`, `DEFAULT_STEPS`)
- Test: `pipeline/tests/test_dung.py`

**Interfaces:**
- Consumes: `TPL_DOC`, `PREFIX`, biến `--at-*`, chế độ dọc gốc của `compose` (Task 4); tên trường (Task 3).
- Produces: biến truyền vào từng mẫu (tên khóa trong `data-variable-values`):
  - `bang-chung`: `anh`, `vx`, `vy`, `vw`, `vh` (từ `vung`), `tom_tat`, `nguon`.
  - `anh`: `anh` hoặc `video`, `gx`, `gy` (từ `diem_giu`, đơn vị %), `nhan`, `ghi_cong`.
  - `doi-chieu`: `tren_nhan`, `tren_so`, `duoi_nhan`, `duoi_so`, `noi_bat`, `nguon`.
  - `ket`: `chu`, `so`, `nguon`.

Yêu cầu hình (spec mục 4.4): `bang-chung` cắt phóng vào `vung` cho đầy bề rộng, viền quanh vùng, một dòng `tom_tat` bên dưới, không chiếu nguyên trang; `anh` phủ kín khung bằng `object-fit: cover` với `object-position: gx% gy%`, ghi công 30 px trong vùng an toàn; `doi-chieu` hai khối trên–dưới, khối `noi_bat` đậm, khối kia mờ; `ket` chữ lớn giữa khung.

- [ ] **Step 1: Viết test (chưa qua)**

```python
@pytest.mark.parametrize("mau", ["moc", "bang-chung", "anh", "doi-chieu", "ket"])
def test_mau_doc_dung_khung_va_vung_an_toan(mau):
    t = (dung.TPL_DOC / f"{mau}.html").read_text(encoding="utf-8")
    assert 'data-width="1080" data-height="1920"' in t
    assert all(v in t for v in ("var(--at-tren)", "var(--at-duoi)", "var(--at-phai)"))
    co = [int(n) for n in re.findall(r"font:\s*\d+\s+(\d+)px", t)]
    assert co and min(co) >= 30                      # nguồn/ghi công 30 px, không chữ nào nhỏ hơn

def test_compose_doc_truyen_bien_cho_bon_mau(ngan_du_mau, video):
    vals = {v_id: v for v_id, v in zip(["bc", "an", "dc", "kc"], _host_vals(
        (dung.compose(ngan_du_mau, goc=video) / "index.html").read_text(encoding="utf-8")))}
    assert (vals["bc"]["vx"], vals["bc"]["vw"], vals["bc"]["tom_tat"]) == (0.1, 0.5, "Giá niêm yết 15,89 triệu")
    assert (vals["an"]["gx"], vals["an"]["gy"]) == (30, 60)
    assert (vals["dc"]["tren_so"], vals["dc"]["noi_bat"]) == ("15,89 triệu", "duoi")
    assert vals["kc"]["chu"] == "Vậy máy cũ còn rẻ không"

def test_mau_bang_chung_khong_chieu_nguyen_trang():
    t = (dung.TPL_DOC / "bang-chung.html").read_text(encoding="utf-8")
    assert "vw" in t and "vh" in t and "scale" in t     # phóng theo vùng, không đặt ảnh nguyên cỡ
```

Fixture `ngan_du_mau`: như `ngan`, bốn cảnh theo thứ tự `bang-chung` (`vung=[0.1, 0.2, 0.5, 0.1]`), `anh` (`diem_giu=[0.3, 0.6]`), `doi-chieu` (`noi_bat="duoi"`), `ket`.

- [ ] **Step 2: Chạy, xác nhận hỏng** — `uv run pytest tests/test_dung.py -k "mau_doc or bon_mau or bang_chung" -q` → FAIL.
- [ ] **Step 3: Viết bốn mẫu và phần `_vars` tương ứng.**
- [ ] **Step 4: Chạy** — `uv run pytest tests/test_dung.py tests/test_theme_guard.py tests/test_tuong_phan.py -q` → PASS (hai tệp sau canh màu và tương phản của mẫu).
- [ ] **Step 5: Kiểm bằng HyperFrames** — render nháp một Short thử đủ 5 mẫu, xem từng cảnh: không chữ nào nằm trong vùng bị che.
- [ ] **Step 6: Commit** — `git commit -m "feat: mẫu dọc bang-chung, anh, doi-chieu, ket"`

---

### Task 6: Cổng chất lượng Short

**Files:**
- Modify: `pipeline/tttc/chat_luong.py`
- Test: `pipeline/tests/test_chat_luong.py`

**Interfaces:**
- Produces: `chat_luong.kiem_short(canh: dict, timing: dict, mp4: Path | None = None, do_mp4=None) -> list[str]`. `do_mp4(path) -> tuple[float, int, int]` trả (giây, rộng, cao); mặc định đo bằng ffprobe. `mp4 is None` thì bỏ các luật về tệp. Hằng số: `SHORT_GIAY = (30.0, 55.0)`, `SHORT_CANH_MAX = 6.0`, `SHORT_CANH_TB = 3.5`, `SHORT_NGHI_MAX = 0.25`.

- [ ] **Step 1: Viết test (chưa qua)** — mỗi luật ở spec mục 4.6 một test, `do_mp4` giả:

```python
def test_kiem_short_sach(): assert chat_luong.kiem_short(CANH_OK, TIMING_OK, Path("x.mp4"), lambda p: (42.0, 1080, 1920)) == []
def test_canh_dau_khong_phai_moc_la_loi(): ...          # "Lỗi" có "moc"
def test_canh_dau_thieu_so_hoac_chu_qua_8_tu_la_loi(): ...
def test_thoi_luong_ngoai_30_55_la_loi(): ...            # do_mp4 trả 61.0 → Lỗi có "61"
def test_khung_khong_phai_1080x1920_la_loi(): ...        # (40.0, 1920, 1080)
def test_canh_dai_hon_6_giay_canh_bao(): ...
def test_trung_binh_canh_hon_3_5_giay_canh_bao(): ...
def test_nghi_giua_hai_tu_qua_0_25_canh_bao(): ...
def test_timing_khong_co_words_khong_nem_loi(): assert isinstance(chat_luong.kiem_short(CANH_OK, {"duration": 40.0}), list)
```

- [ ] **Step 2: Chạy, xác nhận hỏng** — `uv run pytest tests/test_chat_luong.py -k short -q` → FAIL.
- [ ] **Step 3: Viết `kiem_short`.**
- [ ] **Step 4: Chạy** — `uv run pytest tests/test_chat_luong.py -q` → PASS.
- [ ] **Step 5: Commit** — `git commit -m "feat: cổng chất lượng cho Short dọc gốc"`

---

### Task 7: Sổ theo dõi và mô tả riêng của Short

**Files:**
- Modify: `pipeline/tttc/theo_doi.py`, `pipeline/tttc/dang.py`
- Test: `pipeline/tests/test_theo_doi.py`, `pipeline/tests/test_dang.py`

**Interfaces:**
- Produces:
  - `theo_doi.EXTRA` thêm `"o_lai_short"`, `"khuon_short"` (cuối danh sách).
  - Mục Short trong `dong-goi.json` nhận thêm hai khóa tùy chọn: `"khuon": "doc"` và `"mo_ta": str`.
  - `dang._track(tracker, title, when_vn, vid, them: dict | None = None)`: các khóa của `them` ghi vào dòng mới.
  - `dang._upload_short`: mô tả = `s.get("mo_ta") or goi["mo_ta"]`; dòng trỏ về video dài giữ nguyên; gọi `_track(..., them={"khuon_short": s.get("khuon", "cu")})`.
  - `o_lai_short` do người dùng nhập tay; mã không điền.

`trang_thai._short_snapshot` đã băm cả mục Short nên `mo_ta` và `khuon` tự nằm trong biên nhận duyệt; không sửa `trang_thai.py`, chỉ thêm test khẳng định.

- [ ] **Step 1: Viết test (chưa qua)**

```python
def test_migrate_them_hai_cot_short_giu_du_lieu_cu(tmp_path): ...   # header có o_lai_short, khuon_short; ô cũ nguyên vẹn
def test_upload_short_dung_mo_ta_rieng(...): ...        # body gửi đi chứa mo_ta của Short, vẫn có dòng youtu.be/<video dài>
def test_upload_short_cu_khong_co_khuon_ghi_cu(...): ... # mục chỉ có file/tieu_de/ngay/gio → sổ ghi khuon_short == "cu", mô tả chung
def test_upload_short_doc_ghi_khuon_doc(...): ...       # "khuon": "doc" → sổ ghi "doc"
def test_doi_mo_ta_sau_khi_duyet_thi_phai_duyet_lai(...): ...  # tests/test_trang_thai.py: approve_short rồi sửa mo_ta → short_current False
```

Dùng YouTube giả và fixture sẵn có của `test_dang.py`.

- [ ] **Step 2: Chạy, xác nhận hỏng** — `uv run pytest tests/test_theo_doi.py tests/test_dang.py tests/test_trang_thai.py -k "short or cot" -q` → FAIL (trừ test `trang_thai`, có thể qua ngay).
- [ ] **Step 3: Sửa `theo_doi.py`, `dang.py`.**
- [ ] **Step 4: Chạy** — `uv run pytest tests/test_theo_doi.py tests/test_dang.py tests/test_trang_thai.py tests/test_dong_bo_view.py -q` → PASS.
- [ ] **Step 5: Chạy `theo_doi.migrate` trên `theo-doi.csv` thật**, xem `git diff theo-doi.csv`: chỉ header thêm hai cột.
- [ ] **Step 6: Commit** — `git commit -m "feat: cột o_lai_short, khuon_short và mô tả riêng cho Short"`

---

### Task 8: Trích khung, `.gitignore`, quy trình trong skill

**Files:**
- Modify: `pipeline/tttc/dung.py`, `.gitignore`, `.claude/skills/video-dung/SKILL.md` (mục 7), `docs/template-kich-ban.md` (mục 7)
- Test: `pipeline/tests/test_dung.py`

**Interfaces:**
- Consumes: mọi hàm ở Task 1–7.
- Produces: `dung.trich_khung(mp4, out_dir, moc: tuple[float, ...] = (0.0, 3.0)) -> list[Path]`: ghi `khung-0.png`, `khung-3.png` (tên theo phần nguyên của mốc giây) vào `out_dir` bằng ffmpeg.

- [ ] **Step 1: Viết test (chưa qua)**

```python
def test_trich_khung_ghi_hai_anh(tmp_path):
    mp4 = tmp_path / "s.mp4"; _tone(mp4, 5, video=True)
    out = dung.trich_khung(mp4, tmp_path)
    assert [p.name for p in out] == ["khung-0.png", "khung-3.png"] and all(p.stat().st_size > 0 for p in out)
```

- [ ] **Step 2: Chạy, xác nhận hỏng; viết `trich_khung`; chạy lại** — `uv run pytest tests/test_dung.py -k trich_khung -q` → PASS.
- [ ] **Step 3: `.gitignore`** — thêm:

```
videos/*/ngan/*/*.mp3
videos/*/ngan/*/giong-vieneu/
videos/*/ngan/*/composition/
videos/*/ngan/*/khung-*.png
```

- [ ] **Step 4: Viết lại mục 7 của `SKILL.md`** theo sáu bước ở spec mục 4.7, với đúng lệnh:

```
phong_cach.kiem_short(kich_ban) + kiem.check(kich_ban, nguon của V)      → sửa hết "Lỗi"
giong_vieneu.synthesize('V/ngan/k', giong_vieneu.cfg_shorts())
canh.validate(canh, timing, nguon=nguon của V, video_dir='V/ngan/k', goc='V')
dung.compose('V/ngan/k', goc='V')  →  scripts/render.sh V/ngan/k/composition V/shorts/k.mp4 delivery
chat_luong.kiem_short(canh, timing, 'V/shorts/k.mp4')  →  dung.trich_khung('V/shorts/k.mp4', 'V/ngan/k')
dong-goi.json:shorts thêm {"file","tieu_de","ngay","gio","khuon":"doc","mo_ta"?}
```

Tiêu đề Short chấm bằng `tieu_de.kiem` và `tieu_de.kiem_khop_nguon` như video dài. Ghi luật đo của spec mục 4.8: mỗi lứa chỉ đổi một biến; lứa đầu 6 Shorts chỉ đổi cách dựng, giữ loại đề tiêu dùng có giá cụ thể; sau 6 Shorts mà trung vị `o_lai_short` dưới 25% thì dừng thêm mẫu cảnh và xem lại hook, chọn đề; nhắc người dùng nhập `o_lai_short` từ Studio sau 48 giờ.

Ghi rõ: 2 Shorts mỗi video, mỗi Short một góc tự đứng được; kết bằng vòng lặp; không dùng giọng phụ; gửi người dùng mp4 + hai khung + tiêu đề + giờ rồi **dừng**; `duyet-short` chỉ chạy khi người dùng nói "ok". Bỏ đoạn hướng dẫn `scene_range` + `short_hook`.

- [ ] **Step 5: `docs/template-kich-ban.md` mục 7** — sửa đoạn [40–50s]: kết mặc định là vòng lặp; bỏ "Cách 1" khỏi mặc định (ghi "dùng lại khi tỉ lệ ở lại đã vượt 40%"). Sửa câu mẫu ở [0–4s] cho khớp luật: có con số gắn nguồn, không "!".
- [ ] **Step 6: Chạy toàn bộ** — `uv run pytest -q` → PASS toàn bộ.
- [ ] **Step 7: Commit** — `git commit -m "feat: quy trình Short dọc gốc trong skill video-dung"`

---

### Task 9: Dựng thử một Short thật và đối chiếu với bản cũ

**Files:** chỉ tạo trong `videos/2026-11-15-lo-hong-7zip-ai/ngan/1/`; tệp ra đặt tên `shorts/doc-1.mp4`. Không đụng `shorts/1.mp4`, `shorts/2.mp4` và `dong-goi.json` (hai Short kiểu cũ đã duyệt, hẹn 16/11 và 17/11). Chọn video này vì máy còn đủ `nguon/`, `broll/` và hai Short kiểu cũ để so; thư mục "cấm nhập máy cũ" không còn tệp media.

- [ ] **Step 1:** Viết lại Short 1 của video 7-Zip (bản cũ mở bằng "Thứ nhất,") theo quy trình mới ở mục 7 của skill (kịch bản riêng, giọng mới, `canh.json` dọc đủ ít nhất 4 trong 5 mẫu).
- [ ] **Step 2:** Mọi máy kiểm không còn dòng `Lỗi:`. Ghi lại các `Cảnh báo:` còn lại.
- [ ] **Step 3:** Đặt `khung-0.png`, `khung-3.png` của bản mới cạnh hai khung cùng mốc của bản cũ (`shorts/1.mp4`, trích bằng `trich_khung` vào thư mục tạm).
- [ ] **Step 4:** Gửi người dùng: tệp mp4 mới, bốn khung, danh sách cảnh báo. Nhờ xem trên điện thoại để chỉnh `AN_TOAN` nếu chữ bị giao diện Shorts che. **Dừng. Không đăng, không chạy `duyet-short`.**
- [ ] **Step 5:** Nếu người dùng yêu cầu đổi vùng an toàn: sửa `dung.AN_TOAN` và test khẳng định giá trị ở Task 4, render lại, commit `fix: chỉnh vùng an toàn Short theo máy thật`.
