# Hệ thống Đột phá Kênh (Cluster A + Sắc hóa Bao bì + Vòng học Tự động) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Nâng cấp bao bì thumbnail kép (`ban-co-toi` + `ho-so` sắc hóa có `zoom`), áp dụng ngay cho 2 video ngày 16/11, khóa Radar vào Cluster A + Chuỗi (`chuoi.json`), mở rộng sổ theo dõi (`theo-doi.csv` + `doi-thu.csv`) và xây dựng hệ thống khám nghiệm giữ chân (`tttc.kham`) cùng báo cáo tuần tự động (`tttc.bao_cao`).

**Architecture:** Mở rộng trực tiếp các module hiện có trong `pipeline/tttc/` (`thumb.py`, `duyet.py`, `radar.py`, `theo_doi.py`, `dang.py`) với nguyên tắc tương thích ngược hoàn toàn cho các bài kiểm thử hiện hữu, đồng thời bổ sung hai module độc lập `tttc/kham.py` (khớp đường giữ chân 100 điểm từ Analytics với phụ đề `.srt` và cảnh `.json`) và `tttc/bao_cao.py` (tổng hợp số liệu tuần từ `theo-doi.csv` và `doi-thu.csv`).

**Tech Stack:** Python 3.12+, `uv`, `pytest`, Pillow (`PIL`), Google API Python Client (YouTube Data v3, YouTube Analytics v2, YouTube Reporting v1).

**Spec:** `docs/superpowers/specs/2026-11-16-dinh-huong-cluster-a-va-vong-hoc-design.md`

## Global Constraints

- Môi trường Windows: mọi lệnh chạy Python trong `pipeline/` phải đặt `PYTHONUTF8=1` và `PYTHONIOENCODING=utf-8`.
- Mọi con số trên thumbnail và tiêu đề phải lấy từ `nguon.json`. Ảnh nhân vật dùng cho thumbnail phải là ảnh thật có nguồn hợp lệ (Wikimedia Commons, cơ quan/hãng trong nguồn) và có ghi công.
- Tương thích ngược: giữ `thumb.KHUON = "ho-so"`, thêm `thumb.KHUON_HOP_LE = {"ho-so", "ban-co-toi"}`; giữ nguyên vị trí các cột cũ trong `theo_doi.EXTRA`, chỉ nối cột mới vào cuối để không làm gãy các test cắt lát cố định (`list(rows[0])[:16]`).
- Không để `dong-bo-view.py`, `kham.py` hay `bao_cao.py` tung ngoại lệ làm sập tiến trình khi YouTube Analytics trễ dữ liệu hoặc tệp phụ đề/cảnh bị thiếu.

## Review Focus

1. **Ảnh có kích thước bất thường hoặc `zoom` sát biên (`zoom <= 1.0` hoặc `tam` ở góc `(0.0, 0.0)` / `(1.0, 1.0)`):** `_crop_zoom` phải kẹp toạ độ trong khung ảnh gốc, không tạo vùng cắt rỗng hay vượt biên ảnh.
2. **Kiểm tra màu nền giấy kem ở `test_thumb.py` (`img.getpixel((3, 3))`):** Thanh nhấn đỏ của `thumb.ho_so` nếu vẽ đè lên góc `(3, 3)` sẽ làm hỏng `test_ho_so_cream_paper_photo_card_right_and_red_underline_left` và `test_ho_so_takes_colours_from_theme_and_credit_stays_left_of_badge`; vì vậy `ho_so` phải giữ nguyên màu giấy kem ở `(3, 3)` (thanh nhấn hoặc hộp đỏ đặt ở vùng chữ `x >= 40`).
3. **Thứ tự cột `theo_doi.EXTRA` trong `test_theo_doi.py` (`list(rows[0])[-2:] == ["o_lai_short", "khuon_short"]`) và `test_dang.py` (`len(dang.FIELDS) == 16`):** Các bài kiểm thử hiện hữu kiểm tra cứng độ dài và 2 cột cuối của `EXTRA`; phải cập nhật đồng bộ cả 2 bài kiểm thử đó trong cùng Task mở rộng `theo_doi.py`.
4. **Dữ liệu giữ chân Analytics rỗng hoặc ít hơn 2 điểm, hoặc video thiếu `phu-de.srt` / `canh.json`:** `kham.tim_cu_roi` và `kham.tao_kham_nghiem` phải trả về danh sách rỗng / `"—"` nhẹ nhàng thay vì báo lỗi `IndexError` hay `FileNotFoundError`.
5. **Tệp `theo-doi.csv` hoặc `doi-thu.csv` có ô trống, ký tự `%` hoặc chuỗi không phải số khi sinh báo cáo tuần (`bao_cao.py`):** Bộ tính trung vị phải lọc bỏ các ô trống/lỗi và ghi rõ `n = 0` khi chưa có mẫu nào đủ số.

---

### Task 1: Nâng cấp `tttc/thumb.py` & `tttc/duyet.py` (Khuôn `ban-co-toi`, `ho-so` sắc hóa và `zoom`)

**Files:**
- Modify: `pipeline/tttc/thumb.py:140-204`
- Modify: `pipeline/tttc/duyet.py:109-125`
- Modify: `pipeline/tests/test_thumb.py:160-191`
- Modify: `pipeline/tests/test_duyet.py:197-206`
- Modify: `.claude/skills/video-dung/SKILL.md:215-236`

**Interfaces:**
- Produces:
  - `thumb.KHUON = "ho-so"`
  - `thumb.KHUON_HOP_LE = {"ho-so", "ban-co-toi"}`
  - `thumb._crop_zoom(img: Image.Image, tam: tuple[float, float], zoom: float = 1.0) -> Image.Image`
  - `thumb.ho_so(anh: Path, nhan: str, so: str, hoi: str, out: Path, ghi_cong: str = "", tam: tuple[float, float] = (0.5, 0.4), zoom: float = 1.0) -> tuple[Path, Path]`
  - `thumb.ban_co_toi(anh: Path, nhan: str, so: str, hoi: str, out: Path, ghi_cong: str = "", tam: tuple[float, float] = (0.5, 0.35), zoom: float = 1.0) -> tuple[Path, Path]`

- [ ] **Step 1: Viết các bài kiểm thử cho `_crop_zoom`, `ho_so(..., zoom=...)`, `ban_co_toi(...)` và kiểm duyệt `KHUON_HOP_LE`**

Thêm vào cuối `pipeline/tests/test_thumb.py`:
```python
def test_crop_zoom_clamps_to_image_bounds(tmp_path):
    img = Image.new("RGB", (800, 600), (10, 20, 30))
    img.paste((250, 0, 0), (350, 250, 450, 350))
    c1 = thumb._crop_zoom(img, (0.5, 0.5), zoom=2.0)
    assert c1.size == (400, 300) and c1.getpixel((200, 150)) == (250, 0, 0)
    c_edge = thumb._crop_zoom(img, (0.0, 1.0), zoom=3.0)
    assert c_edge.size == (266, 200)
    assert thumb._crop_zoom(img, (0.5, 0.5), zoom=1.0).size == (800, 600)


def test_ban_co_toi_makes_1280x720_and_168px_with_dark_bg_and_red_banner(tmp_path):
    import pytest
    a = _anh(tmp_path, mau=(180, 120, 90), size=(1000, 800))
    big, small = thumb.ban_co_toi(a, "NVIDIA BỐC HƠI", "-190 TỶ USD", "MỸ RA TRÁT?",
                                  tmp_path / "b.png", ghi_cong="Ảnh: Wikimedia", tam=(0.5, 0.4), zoom=2.0)
    assert Image.open(big).size == (1280, 720) and Image.open(small).size == (168, 94)
    img = Image.open(big).convert("RGB")
    do = theme.rgb(theme.TH["sac"]["do"][0])
    assert img.getpixel((5, 360)) == do  # thanh nhấn đỏ mép trái
    assert max(img.getpixel((40, 30))) < 50  # nền tối sâu ở góc trên trái
    with pytest.raises(ValueError):
        thumb.ban_co_toi(a, "NVIDIA", "", "SAO?", tmp_path / "b2.png")
```

Và cập nhật `test_review_2_flags_thumbnail_not_on_locked_template` trong `pipeline/tests/test_duyet.py`:
```python
def test_review_2_flags_thumbnail_not_on_locked_template(tmp_path):
    d = _video(tmp_path)
    goi = {**GOI, "phuong_an": [
        {**GOI["phuong_an"][0], "khuon": "ban-co-toi"},
        {**GOI["phuong_an"][1], "khuon": "khung"},
        {k: v for k, v in GOI["phuong_an"][2].items() if k != "khuon"},
    ]}
    (d / "dong-goi.json").write_text(json.dumps(goi, ensure_ascii=False), encoding="utf-8")
    html = duyet.render_review_2(d).read_text(encoding="utf-8")
    assert "Phương án 1: Lỗi: thumbnail" not in html
    assert "Phương án 2: Lỗi: thumbnail không theo khuôn đã khóa" in html
    assert "Phương án 3: Lỗi: thumbnail không theo khuôn đã khóa" in html
```

- [ ] **Step 2: Chạy pytest để xác nhận các test mới báo lỗi**

Run: `PYTHONUTF8=1 uv run pytest tests/test_thumb.py tests/test_duyet.py -q` (trong `pipeline/`)
Expected: FAIL (`AttributeError: module 'tttc.thumb' has no attribute '_crop_zoom'` / `'ban_co_toi'`)

- [ ] **Step 3: Cài đặt `_crop_zoom`, nâng cấp `ho_so`, thêm `ban_co_toi` trong `pipeline/tttc/thumb.py` và cập nhật `pipeline/tttc/duyet.py`**

Trong `pipeline/tttc/thumb.py`:
- Đặt `KHUON = "ho-so"` và `KHUON_HOP_LE = {"ho-so", "ban-co-toi"}`.
- Viết `_crop_zoom(img: Image.Image, tam: tuple[float, float], zoom: float = 1.0) -> Image.Image`.
- Trong `ho_so(...)`: thêm tham số `zoom: float = 1.0`; giữ nguyên màu nền giấy kem ở `(3, 3)` để các test hiện hữu xanh; áp dụng `_crop_zoom` và `ImageEnhance.Contrast(1.15)` cho ảnh thẻ bên phải; ở tầng `so`, vẽ hộp tem đỏ bo góc (`radius=12`, màu `do = theme.rgb(theme.TH["sac"]["do"][0])`) tại `[x + b[0] - 12, y - 10, x + b[2] + 16, y + b[3] - b[1] + 12]` với chữ số màu trắng `(255, 255, 255)` (hoặc viền mực tối ở lề dưới để vẫn có cả điểm ảnh màu `do` và điểm ảnh tối `< 40` trong vùng `(40, 150, 700, 420)`).
- Viết hàm `ban_co_toi(anh: Path, nhan: str, so: str, hoi: str, out: Path, ghi_cong: str = "", tam: tuple[float, float] = (0.5, 0.35), zoom: float = 1.0) -> tuple[Path, Path]` theo đúng thông số mục 5.1.D của Spec (thanh trái màu `theme.rgb(theme.TH["sac"]["do"][0])`, nền `theme.rgb(theme.TH["nen"])`, ảnh tràn viền phải rộng 720 px có gradient hòa trộn 220 px, pill `nhan` màu `theme.TH["nhan"][0]`, băng đỏ `so` chữ trắng viền đen, câu hỏi `hoi` màu `theme.TH["pill"]["vang"][0]` viền đen).
- Trong `pipeline/tttc/duyet.py`: kiểm tra `o.get("khuon") not in thumb.KHUON_HOP_LE` thì báo `"Phương án {i}: Lỗi: thumbnail không theo khuôn đã khóa «ho-so / ban-co-toi»..."`. Cập nhật `.claude/skills/video-dung/SKILL.md` mục 5.2 hướng dẫn dựng bộ 3 ảnh gồm `ban-co-toi` và `ho-so` có `zoom`.

- [ ] **Step 4: Chạy lại pytest để xác nhận toàn bộ `test_thumb.py` và `test_duyet.py` đều PASS**

Run: `PYTHONUTF8=1 uv run pytest tests/test_thumb.py tests/test_duyet.py -q`
Expected: PASS

- [ ] **Step 5: Commit Task 1**

```bash
git add pipeline/tttc/thumb.py pipeline/tttc/duyet.py pipeline/tests/test_thumb.py pipeline/tests/test_duyet.py .claude/skills/video-dung/SKILL.md
git commit -m "feat: thêm khuôn thumbnail ban-co-toi, sắc hóa ho-so và hỗ trợ zoom mặt nhân vật"
```

---

### Task 2: Nâng cấp ngay bộ 3 Thumbnail cho 2 video ngày 16/11 (`meta-phat-anh-facebook` & `starship-starlink-vn`) và cập nhật lên YouTube

**Files:**
- Modify: `videos/2026-11-16-meta-phat-anh-facebook/dong-goi.json`
- Modify: `videos/2026-11-16-meta-phat-anh-facebook/trang-thai.json`
- Modify: `videos/2026-11-16-meta-phat-anh-facebook/thumbnails/1.png` (và `2.png`, `3.png`, `*-168px.png`)
- Modify: `videos/2026-11-16-starship-starlink-vn/dong-goi.json`
- Modify: `videos/2026-11-16-starship-starlink-vn/trang-thai.json`
- Modify: `videos/2026-11-16-starship-starlink-vn/thumbnails/1.png` (và `2.png`, `3.png`, `*-168px.png`)

**Interfaces:**
- Consumes: `thumb.ban_co_toi`, `thumb.ho_so`, `duyet.render_review_2`, `trang_thai._review_files`, `dang.client`

- [ ] **Step 1: Tải ảnh chân dung Mark Zuckerberg từ Wikimedia Commons cho bài `meta-phat-anh-facebook`**

Dùng `tttc.anh.search("Mark Zuckerberg")` (hoặc tải ảnh thật CC-BY/Public Domain của Mark Zuckerberg trên Wikimedia Commons) lưu vào `videos/2026-11-16-meta-phat-anh-facebook/anh/mark-zuckerberg.jpg` và ghi công vào `anh/ghi-cong.json`.

- [ ] **Step 2: Dựng lại bộ 3 thumbnail mới (Khuôn `ban-co-toi` + Khuôn `ho-so` sắc hóa có `zoom`) cho `meta-phat-anh-facebook` và `starship-starlink-vn`**

Chạy script Python sử dụng `thumb.ban_co_toi` và `thumb.ho_so`:
- Với `2026-11-16-meta-phat-anh-facebook`:
  - `1.png`: `ban-co-toi` (ảnh Mark Zuckerberg `zoom=1.8`, `["META BỊ PHẠT", "805 TRIỆU EURO", "VIỆT NAM PHẠT?"]`)
  - `2.png`: `ho-so` (cùng ảnh `zoom=1.8`, `["META BỊ PHẠT", "805 TRIỆU EURO", "VIỆT NAM PHẠT?"]`)
  - `3.png`: `ban-co-toi` (cùng ảnh `zoom=1.8`, `["79 TRIỆU NGƯỜI", "805 TRIỆU EURO", "CẦN TẮT GÌ?"]`)
- Với `2026-11-16-starship-starlink-vn`:
  - `1.png`: `ban-co-toi` (ảnh `thumbnails/khung-bat-tau.png` `zoom=1.5`, `["STARLINK CHÀO", "566 NGHÌN", "RẺ CHƯA?"]`)
  - `2.png`: `ho-so` (ảnh `nguon/b1.jpg` `zoom=1.3`, `["STARLINK CHÀO", "566 NGHÌN", "RẺ CHƯA?"]`)
  - `3.png`: `ban-co-toi` (ảnh `nguon/c1.jpg` ông Nguyễn Thành Chung `zoom=1.6`, `["STARLINK 566K", "CÁP QUANG 195K", "RẺ CHƯA?"]`)

- [ ] **Step 3: Cập nhật `dong-goi.json`, render lại `duyet-2.html`, cập nhật biên nhận `trang-thai.json` cho cả 2 video và đẩy thumbnail mới lên YouTube cho video `Gsvyy5eGh70`**

- Cập nhật trường `"khuon"` và `"chu_thumb"` trong `dong-goi.json` của cả 2 video.
- Gọi `duyet.render_review_2` cho cả 2 video; kiểm tra không có dòng `Lỗi:` nào trong `duyet-2.html`.
- Cập nhật `ban_duyet` trong `trang-thai.json` của cả 2 video khớp sha256 mới (`trang_thai.review_current(d, "duyet-2") == True`).
- Đẩy thumbnail phương án đang chọn (`thumbnails/3.png`) của `2026-11-16-meta-phat-anh-facebook` lên YouTube cho `videoId="Gsvyy5eGh70"` qua `dang.client().thumbnails().set(...)`.

- [ ] **Step 4: Kiểm tra ảnh `-168px` và trạng thái `review_current` của cả 2 video**

Run: `PYTHONUTF8=1 uv run python -c "from tttc import trang_thai as tt; assert tt.review_current('../videos/2026-11-16-meta-phat-anh-facebook', 'duyet-2'); assert tt.review_current('../videos/2026-11-16-starship-starlink-vn', 'duyet-2'); print('OK')"`
Expected: `OK`

- [ ] **Step 5: Commit Task 2**

```bash
git add videos/2026-11-16-meta-phat-anh-facebook videos/2026-11-16-starship-starlink-vn
git commit -m "chore: nâng cấp bộ 3 thumbnail ban-co-toi/ho-so cho video Meta và Starlink"
```

---

### Task 3: Khóa Radar vào Cluster A, Quản lý Chuỗi (`chuoi.json`) và Sổ Đối thủ (`doi-thu.csv`)

**Files:**
- Create: `chuoi.json`
- Modify: `pipeline/config.json`
- Modify: `pipeline/tttc/radar.py`
- Modify: `pipeline/tttc/dang.py:100-106,258-265`
- Modify: `pipeline/tests/test_radar.py`
- Modify: `pipeline/tests/test_dang.py`

**Interfaces:**
- Produces:
  - `radar.THUC_THE_CLUSTER_A: list[str]`
  - `radar.la_cluster_a(text: str) -> bool`
  - `radar.khuyen_nghi_dinh_dang(de: dict) -> str` (`"dai-tang-1"` | `"dai-tang-2"` | `"shorts"` | `"bo"`)
  - `radar.khop_chuoi(text: str, chuoi_path: Path = ...) -> dict | None`
  - `radar.cap_nhat_so_doi_thu(csv_path: Path, rss_items: list[dict], now: datetime, kenh: str = "@MotCongNghe") -> int`

- [ ] **Step 1: Viết các bài kiểm thử cho `la_cluster_a`, `khuyen_nghi_dinh_dang`, `khop_chuoi`, `cap_nhat_so_doi_thu` và gắn link chuỗi lúc đăng**

Thêm vào `pipeline/tests/test_radar.py`:
```python
def test_la_cluster_a_va_khuyen_nghi_dinh_dang():
    assert radar.la_cluster_a("Nvidia bốc hơi 190 tỷ USD vì chip AI")
    assert not radar.la_cluster_a("Grab giảm phí 2.000 đồng mỗi cuốc xe")
    assert radar.khuyen_nghi_dinh_dang({"tieu_de": "Nvidia mất 190 tỷ USD", "soc": 2, "so_lon": 2, "goc_vn": 1}) == "dai-tang-1"
    assert radar.khuyen_nghi_dinh_dang({"tieu_de": "Nvidia mất 190 tỷ USD", "soc": 2, "so_lon": 2, "goc_vn": 1,
                                        "ho_da_dang": True, "chenh_gio_ho": 3.5}) == "dai-tang-2"
    assert radar.khuyen_nghi_dinh_dang({"tieu_de": "Grab giảm phí 2.000 đồng", "soc": 2, "so_lon": 1, "goc_vn": 2}) == "shorts"
    assert radar.khuyen_nghi_dinh_dang({"tieu_de": "Nvidia ra mắt cáp sạc", "soc": 1, "so_lon": 0, "goc_vn": 0}) == "bo"


def test_khop_chuoi_va_cap_nhat_so_doi_thu(tmp_path):
    chuoi_p = tmp_path / "chuoi.json"
    chuoi_p.write_text(json.dumps({"chuoi": [{"ma": "nvidia-ai", "ten": "Nvidia", "playlist_id": "PL1",
                                              "tu_khoa": ["nvidia", "jensen huang"],
                                              "tap": [{"slug": "s1", "video_id": "v1", "ngay": "2026-11-13"}]}]}), encoding="utf-8")
    assert radar.khop_chuoi("Jensen Huang điều trần ở Hạ viện", chuoi_p)["ma"] == "nvidia-ai"
    assert radar.khop_chuoi("Grab tăng phí", chuoi_p) is None

    dt_csv = tmp_path / "doi-thu.csv"
    rss = [
        {"id": "v_nv", "tieu_de": "Nvidia mất 190 tỷ đô", "dang_luc": datetime(2026, 11, 15, 17, 0, tzinfo=VN), "view": 80000},
        {"id": "v_gr", "tieu_de": "Mẹo tiết kiệm pin điện thoại", "dang_luc": datetime(2026, 11, 10, 17, 0, tzinfo=VN), "view": 10000},
    ]
    now = datetime(2026, 11, 16, 21, 0, tzinfo=VN)
    assert radar.cap_nhat_so_doi_thu(dt_csv, rss, now) == 2
    txt = dt_csv.read_text(encoding="utf-8")
    assert "v_nv" in txt and "cluster-a" in txt and "80000" in txt
```

- [ ] **Step 2: Chạy pytest để xác nhận các test mới báo lỗi**

Run: `PYTHONUTF8=1 uv run pytest tests/test_radar.py -q`
Expected: FAIL (`AttributeError: module 'tttc.radar' has no attribute 'la_cluster_a'`)

- [ ] **Step 3: Tạo `chuoi.json`, cập nhật `pipeline/tttc/radar.py` và `pipeline/tttc/dang.py`**

- Tạo `c:\Projects\Youtube\chuoi.json` theo mục 5.3.B của Spec.
- Trong `pipeline/tttc/radar.py`:
  - Thêm `THUC_THE_CLUSTER_A`, `la_cluster_a(text: str) -> bool`, `khuyen_nghi_dinh_dang(de: dict) -> str`, `khop_chuoi(text: str, chuoi_path: Path = ...) -> dict | None`, và `cap_nhat_so_doi_thu(csv_path: Path, rss_items: list[dict], now: datetime, kenh: str = "@MotCongNghe") -> int`.
  - Cập nhật `ghi_chu_de` để nếu mục đề trong `top` có trường `"dinh_dang"` hoặc `"chuoi"` thì in thêm dòng `- Định dạng khuyến nghị: ...` / `- Chuỗi: ...` (không làm thay đổi đầu ra khi mục đề không có các trường đó).
- Trong `pipeline/tttc/dang.py`:
  - Trong `build_body(video_dir, when)`: nếu `goi.get("tap_truoc")` có video ID, tự chèn dòng `"👉 Xem tập trước trong chuỗi: https://youtu.be/<id>\n\n"` vào đầu mô tả (nếu chưa có).

- [ ] **Step 4: Chạy lại pytest để xác nhận PASS**

Run: `PYTHONUTF8=1 uv run pytest tests/test_radar.py tests/test_dang.py -q`
Expected: PASS

- [ ] **Step 5: Commit Task 3**

```bash
git add chuoi.json pipeline/tttc/radar.py pipeline/tttc/dang.py pipeline/tests/test_radar.py pipeline/tests/test_dang.py
git commit -m "feat: khóa radar Cluster A, quản lý chuỗi chuoi.json và sổ đối thủ doi-thu.csv"
```

---

### Task 4: Mở rộng `theo-doi.csv` (`hien_thi_7d`, `khuon_thumb`, `goc`, `chuoi`, `roi_lon_nhat`) & Nâng cấp `dong-bo-view.py`

**Files:**
- Modify: `pipeline/tttc/theo_doi.py:10-15`
- Modify: `pipeline/tttc/dang.py:260-265`
- Modify: `pipeline/scripts/dong-bo-view.py:148-181,226-245`
- Modify: `pipeline/tests/test_theo_doi.py:66-72`
- Modify: `pipeline/tests/test_dang.py:287-296`
- Modify: `pipeline/tests/test_dong_bo_view.py:112-133`

**Interfaces:**
- Produces:
  - `theo_doi.EXTRA = ["trung_de_ho", "chenh_gio", "radar_hang", "view_ho_24h", "avd_pct", "con_50pct", "o_lai_short", "khuon_short", "hien_thi_7d", "khuon_thumb", "goc", "chuoi", "roi_lon_nhat"]`
  - `reach.hien_thi(ngay_csv: list[dict[str, tuple[float, float]]], video_id: str) -> int`

- [ ] **Step 1: Cập nhật và bổ sung kiểm thử trong `test_theo_doi.py`, `test_dang.py` và `test_dong_bo_view.py`**

- Trong `pipeline/tests/test_theo_doi.py`: cập nhật `test_migrate_them_hai_cot_short_giu_du_lieu_cu` kiểm tra các cột mới ở cuối (`"hien_thi_7d", "khuon_thumb", "goc", "chuoi", "roi_lon_nhat"`).
- Trong `pipeline/tests/test_dang.py`: cập nhật `len(dang.FIELDS) == 21` và kiểm tra khi `upload` video dài sẽ tự ghi `khuon_thumb` (từ phương án đã chọn) và `chuoi` / `goc` (nếu có trong `dong-goi.json`) vào `theo-doi.csv`.
- Trong `pipeline/tests/test_dong_bo_view.py`: cập nhật `test_cap_nhat_ctr_can_du_7_ngay_va_khong_ghi_de` kiểm tra `rows[0]["hien_thi_7d"] == "7000"` được điền cùng lúc với `ctr`, và khi video mới chỉ có 1–6 ngày báo cáo thì in dòng `CTR tạm tính` ra stdout.

- [ ] **Step 2: Chạy pytest để xác nhận các test báo lỗi**

Run: `PYTHONUTF8=1 uv run pytest tests/test_theo_doi.py tests/test_dang.py tests/test_dong_bo_view.py -q`
Expected: FAIL

- [ ] **Step 3: Cài đặt mở rộng cột trong `theo_doi.py`, `reach.py`, `dang.py` và `dong-bo-view.py`**

- Trong `pipeline/tttc/theo_doi.py`: nối `"hien_thi_7d", "khuon_thumb", "goc", "chuoi", "roi_lon_nhat"` vào cuối `EXTRA`.
- Trong `pipeline/tttc/reach.py`: thêm hàm `hien_thi(ngay_csv: list[dict[str, tuple[float, float]]], video_id: str) -> int` trả tổng `impr` làm tròn `int(round(impr))`.
- Trong `pipeline/tttc/dang.py`: khi gọi `_track` ở `_upload`, truyền `them={"khuon_thumb": _chosen(d).get("khuon", ""), "goc": _goi(d).get("goc", ""), "chuoi": _goi(d).get("chuoi", "")}`.
- Trong `pipeline/scripts/dong-bo-view.py`:
  - Trong `cap_nhat_ctr`: nếu cả 7 ngày đã có trong `ngay_url`, điền cả `r["ctr"]` và `r["hien_thi_7d"] = str(reach.hien_thi([cache[d] for d in cac_ngay], v))` (nếu `hien_thi_7d` còn trống). Nếu chỉ có một phần ngày (`1 <= len(co_ngay) < 7`), tải vào `cache` và in dòng `CTR tạm tính {v} ({len(co_ngay)}/7 ngày): {c*100:.1f}% ({impr} hiển thị)`.
  - Trong `dong_bo()`: khi đồng bộ RSS đối thủ, gọi thêm `radar.cap_nhat_so_doi_thu(ROOT / "doi-thu.csv", rss_items, now)`.

- [ ] **Step 4: Chạy lại pytest để xác nhận PASS**

Run: `PYTHONUTF8=1 uv run pytest tests/test_theo_doi.py tests/test_dang.py tests/test_dong_bo_view.py -q`
Expected: PASS

- [ ] **Step 5: Commit Task 4**

```bash
git add pipeline/tttc/theo_doi.py pipeline/tttc/reach.py pipeline/tttc/dang.py pipeline/scripts/dong-bo-view.py pipeline/tests/test_theo_doi.py pipeline/tests/test_dang.py pipeline/tests/test_dong_bo_view.py
git commit -m "feat: mở rộng cột theo-doi.csv, tự điền hien_thi_7d và in CTR tạm tính"
```

---

### Task 5: Xây dựng Module Khám nghiệm Giữ chân Tự động (`tttc/kham.py`)

**Files:**
- Create: `pipeline/tttc/kham.py`
- Create: `pipeline/tests/test_kham.py`
- Modify: `pipeline/scripts/dong-bo-view.py`

**Interfaces:**
- Produces:
  - `kham.tim_cu_roi(pts: list[tuple[float, float]], thoi_luong: float, nguong_diem: float = 5.0) -> list[dict]`
  - `kham.khop_boi_canh(video_dir: Path, giay: float) -> dict` (`{"thoai": str, "canh_id": str, "mau": str}`)
  - `kham.tao_kham_nghiem(video_dir: Path, pts: list[tuple[float, float]], thoi_luong: float, ctr: str = "", hien_thi: str = "") -> Path`
  - `kham.cap_nhat_kham(rows: list[dict], thoi_luong: dict[str, float], analytics, now: datetime, videos_root: Path = ...) -> int`

- [ ] **Step 1: Viết kiểm thử đầy đủ trong `pipeline/tests/test_kham.py` (gồm cả trường hợp dữ liệu rỗng và thiếu tệp `.srt`/`.json`)**

Tạo `pipeline/tests/test_kham.py`:
```python
import json
from pathlib import Path
from tttc import kham


def test_tim_cu_roi_ignores_first_2pct_and_sorts_by_drop_size():
    pts = [(0.01, 1.00), (0.02, 0.90), (0.05, 0.82), (0.10, 0.70), (0.20, 0.68), (0.50, 0.40)]
    # 0.01->0.02 (-10pt) bị bỏ qua vì <= 0.02; 0.02->0.05 (-8pt tại giây 25); 0.05->0.10 (-12pt tại giây 50); 0.20->0.50 (-28pt tại giây 250)
    roi = kham.tim_cu_roi(pts, thoi_luong=500.0, nguong_diem=5.0)
    assert [r["roi_diem"] for r in roi] == [28.0, 12.0, 8.0]
    assert roi[1]["giay"] == 50.0 and roi[1]["mmss"] == "0:50"
    assert kham.tim_cu_roi([], 500.0) == [] and kham.tim_cu_roi([(0.1, 0.9)], 0.0) == []


def test_khop_boi_canh_and_tao_kham_nghiem(tmp_path):
    (tmp_path / "phu-de.srt").write_text(
        "1\n00:00:00,000 --> 00:00:20,000\nCâu mở đầu chuẩn.\n\n"
        "2\n00:00:20,000 --> 00:00:35,000\nTrong thông tư có một chi tiết lạ.\n",
        encoding="utf-8",
    )
    (tmp_path / "canh.json").write_text(json.dumps({
        "scenes": [
            {"id": "c001", "mau": "so-lon", "start": 0.0, "end": 20.0},
            {"id": "c002", "mau": "trang-nguon", "start": 20.0, "end": 35.0},
        ]
    }), encoding="utf-8")
    ctx = kham.khop_boi_canh(tmp_path, 25.0)
    assert "chi tiết lạ" in ctx["thoai"] and ctx["canh_id"] == "c002" and ctx["mau"] == "trang-nguon"

    pts = [(0.02, 0.95), (0.05, 0.80), (0.10, 0.72), (0.50, 0.42), (1.0, 0.25)]
    out = kham.tao_kham_nghiem(tmp_path, pts, thoi_luong=500.0, ctr="6.3%", hien_thi="7855")
    txt = out.read_text(encoding="utf-8")
    assert out == tmp_path / "kham-nghiem.md"
    assert "0:25" in txt and "chi tiết lạ" in txt and "trang-nguon" in txt


def test_khop_boi_canh_handles_missing_files_gracefully(tmp_path):
    ctx = kham.khop_boi_canh(tmp_path, 10.0)
    assert ctx == {"thoai": "—", "canh_id": "—", "mau": "—"}
```

- [ ] **Step 2: Chạy pytest để xác nhận `test_kham.py` báo lỗi chưa có module**

Run: `PYTHONUTF8=1 uv run pytest tests/test_kham.py -q`
Expected: FAIL (`ImportError: cannot import name 'kham' from 'tttc'`)

- [ ] **Step 3: Cài đặt `pipeline/tttc/kham.py`, tích hợp vào `dong-bo-view.py` và chạy khám nghiệm cho các video đã có dữ liệu**

- Viết `pipeline/tttc/kham.py` cung cấp:
  - `tim_cu_roi`, `khop_boi_canh`, `tao_kham_nghiem`, `lay_duong_giu_chan(analytics, video_id, start_date, end_date)`, `tim_thu_muc_video(videos_root, video_id)`, `cap_nhat_kham(...)` và hàm `main()` hỗ trợ CLI `python -m tttc.kham <thư mục video> [--som]`.
  - Khi `cap_nhat_kham` tạo xong `kham-nghiem.md` cho một dòng trong `theo-doi.csv` (mà `roi_lon_nhat` còn trống), điền `r["roi_lon_nhat"] = f"{roi[0]['mmss']} -{roi[0]['roi_diem']:.0f}pt"` nếu có cú rơi.
- Gọi `kham.cap_nhat_kham` trong `pipeline/scripts/dong-bo-view.py`.

- [ ] **Step 4: Chạy pytest xác nhận PASS**

Run: `PYTHONUTF8=1 uv run pytest tests/test_kham.py tests/test_dong_bo_view.py -q`
Expected: PASS

- [ ] **Step 5: Commit Task 5**

```bash
git add pipeline/tttc/kham.py pipeline/tests/test_kham.py pipeline/scripts/dong-bo-view.py
git commit -m "feat: module khám nghiệm giữ chân tự động tttc.kham"
```

---

### Task 6: Xây dựng Module Báo cáo Tuần (`tttc/bao_cao.py`) và Đồng bộ Sổ Thực tế

**Files:**
- Create: `pipeline/tttc/bao_cao.py`
- Create: `pipeline/tests/test_bao_cao.py`
- Modify: `theo-doi.csv`
- Create: `doi-thu.csv`
- Create: `docs/bao-cao/2026-W46.md`

**Interfaces:**
- Produces:
  - `bao_cao.tao_bao_cao(rows: list[dict], doi_thu_rows: list[dict], now: datetime, out_dir: Path = ...) -> Path`

- [ ] **Step 1: Viết kiểm thử cho `tttc/bao_cao.py` trong `pipeline/tests/test_bao_cao.py` (bao gồm cả dữ liệu trống/không phải số)**

Tạo `pipeline/tests/test_bao_cao.py`:
```python
from datetime import datetime, timezone, timedelta
from tttc import bao_cao

VN = timezone(timedelta(hours=7))


def test_tao_bao_cao_separates_long_and_shorts_and_handles_empty_cells(tmp_path):
    rows = [
        {"ngay": "09/11/2026", "tieu_de": "CEO Nvidia xin lỗi", "gio_dang": "09/11/2026 20:45",
         "link": "https://youtu.be/E17SceQLG9I", "view_24h": "3100", "view_7d": "3208",
         "ctr": "6.3%", "giu_chan_30s": "72%", "avd_pct": "35%", "con_50pct": "32%",
         "khuon_thumb": "ban-co-toi", "goc": "tang-2", "chuoi": "nvidia-de-che-ai"},
        {"ngay": "10/11/2026", "tieu_de": "Cấm bán iPhone cũ", "gio_dang": "10/11/2026 18:50",
         "link": "https://youtu.be/w60qG6ipY1s", "view_24h": "", "view_7d": "93",
         "ctr": "1.3%", "giu_chan_30s": "68%", "avd_pct": "42%", "con_50pct": "40%",
         "khuon_thumb": "ho-so", "goc": "tang-1", "chuoi": ""},
        {"ngay": "12/11/2026", "tieu_de": "iPhone 15 Plus cũ #shorts", "gio_dang": "12/11/2026 08:00",
         "link": "https://youtu.be/1g_MjV4nwTY", "view_24h": "940", "view_7d": "",
         "ctr": "", "giu_chan_30s": "", "o_lai_short": "10%", "khuon_short": "cu"},
    ]
    dt_rows = [
        {"kenh": "@MotCongNghe", "video_id": "siGdK7U9ea4", "tieu_de": "Jensen rời ghế CEO Nvidia",
         "gio_dang": "13/11/2026 17:00", "view_moi_nhat": "98633", "nhom_de": "cluster-a", "breakout": "5.6"},
    ]
    now = datetime(2026, 11, 16, 10, 0, tzinfo=VN)
    p = bao_cao.tao_bao_cao(rows, dt_rows, now, out_dir=tmp_path)
    txt = p.read_text(encoding="utf-8")
    assert p.name == "2026-W46.md"
    assert "Video dài" in txt and "Shorts" in txt
    assert "ban-co-toi" in txt and "cluster-a" in txt and "1.3% < 3%" in txt


def test_tao_bao_cao_with_empty_inputs(tmp_path):
    now = datetime(2026, 11, 16, 10, 0, tzinfo=VN)
    p = bao_cao.tao_bao_cao([], [], now, out_dir=tmp_path)
    assert "n = 0" in p.read_text(encoding="utf-8")
```

- [ ] **Step 2: Chạy pytest để xác nhận `test_bao_cao.py` báo lỗi chưa có module**

Run: `PYTHONUTF8=1 uv run pytest tests/test_bao_cao.py -q`
Expected: FAIL (`ImportError: cannot import name 'bao_cao' from 'tttc'`)

- [ ] **Step 3: Cài đặt `pipeline/tttc/bao_cao.py`, chạy đồng bộ dữ liệu thật và sinh bản khám nghiệm + báo cáo tuần đầu tiên**

- Viết `pipeline/tttc/bao_cao.py` với `tao_bao_cao(...)` và CLI `python -m tttc.bao_cao`.
- Chạy `PYTHONUTF8=1 uv run python scripts/dong-bo-view.py` để di trú `theo-doi.csv` sang bộ cột mới, tạo `doi-thu.csv` từ RSS thực tế của `@MotCongNghe`.
- Chạy `PYTHONUTF8=1 uv run python -m tttc.kham ../videos/<slug> --som` cho các video đã có dữ liệu giữ chân trên Analytics (`2026-11-11-nvidia-ceo-gian-diep`, `2026-11-11-cam-nhap-may-cu`, `2026-11-11-grab-giam-phi`, `2026-11-15-nvidia-siet-chip`) và điền cột `roi_lon_nhat`, `khuon_thumb`, `chuoi`, `goc` vào `theo-doi.csv`.
- Chạy `PYTHONUTF8=1 uv run python -m tttc.bao_cao` để sinh `docs/bao-cao/2026-W46.md`.

- [ ] **Step 4: Chạy toàn bộ bộ kiểm thử của dự án (`uv run pytest -q`) để xác nhận 100% xanh**

Run: `PYTHONUTF8=1 uv run pytest -q`
Expected: Tất cả các test trong `pipeline/tests/` đều PASS, 0 lỗi.

- [ ] **Step 5: Commit Task 6**

```bash
git add pipeline/tttc/bao_cao.py pipeline/tests/test_bao_cao.py theo-doi.csv doi-thu.csv docs/bao-cao/ docs/superpowers/
git commit -m "feat: báo cáo tuần tttc.bao_cao và đồng bộ dữ liệu khám nghiệm thực tế"
```
