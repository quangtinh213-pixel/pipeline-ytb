# Định vị đối đầu và vận hành 1 video/ngày Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Pipeline đo được giờ từng bước, có radar chọn đề và theo dõi đối thủ, có kho dự trữ, có cổng chạy khô kiểm được bằng lệnh, sẵn sàng cho ba ngày chạy khô rồi chạy thật 1 video/ngày.

**Architecture:** Mở rộng `trang_thai.py` (giờ, thứ tự bước, kho), thêm `radar.py`, `theo_doi.py`, `canh_remap.py`, `chay_kho.py`; phần còn lại là cấu hình, SKILL và tài liệu. Việc phần cơ học của `canh.json` (H2) và bước đạo diễn nằm ở kế hoạch hình ảnh; giọng văn (H3 phần giọng văn) ở kế hoạch giọng văn.

**Tech Stack:** Python ≥ 3.11, pytest (`uv run`), `requests`, `xml.etree`, `csv`, `difflib`; ffmpeg.

**Spec:** `docs/superpowers/specs/2026-11-09-dinh-vi-doi-dau-van-hanh-design.md`

**Thứ tự thực hiện:** sau Task 4 của kế hoạch giọng văn (`2026-11-09-giong-van-kich-ban.md`, vì cùng sửa `STEPS`). Task 7 (`chay_kho`) đọc kết quả của kế hoạch giọng văn và kế hoạch hình ảnh nhưng không phụ thuộc mã của chúng.

## Global Constraints

- Radar chấm đề: điểm = `soc` + `so_lon` + 2 × `goc_vn`, mỗi thành phần 0–2, tối đa 8; đạt khi ≥ 4; cùng điểm thì đề có `goc_vn` > 0 xếp trước, rồi đề mới hơn. Câu `goc_vn` = 0 **không** tự động loại.
- Radar chỉ dùng **tiêu đề, giờ đăng, số view** của đối thủ; không lấy lời, kịch bản, hình.
- RSS đối thủ: `https://www.youtube.com/feeds/videos.xml?channel_id=UC91zSg_iPgJZZL6KB91BewQ` (15 video gần nhất, có giờ đăng và `media:statistics views`).
- Giờ đăng mục tiêu 15:00–16:30 giờ Việt Nam; `config.json:gio_dang_mac_dinh` = `15:30`. Đồng hồ ngày và mọi mốc giờ trong spec là mục tiêu chưa đo.
- Cổng chạy khô: 3 ngày liên tiếp (2 evergreen + 1 đề nóng), mỗi ngày đạt đủ 7 tiêu chí ở spec mục 7. Kho dự trữ ≥ 3 video evergreen khi chạy thật.
- Ngưỡng tốc độ đọc 180–230 từ/phút (`chat_luong.MUC_TIEU["toc_do"]`).
- Chạy lệnh trong `pipeline/`. Chỉ `git add` đường dẫn cụ thể.

## Review Focus

1. RSS đối thủ trống, hỏng XML, hoặc thiếu `media:statistics` → radar báo lỗi rõ hoặc bỏ mục đó, không làm sập cả vòng quét (Task 4).
2. Giờ đăng luôn tính theo giờ Việt Nam (UTC+7); `chenh_gio` âm nghĩa là mình sớm hơn (Task 5).
3. `theo-doi.csv` hiện có 1 dòng ở định dạng 8 cột: di trú thêm 4 cột không mất dữ liệu và không đổi thứ tự cột cũ (Task 5).
4. Video đã có `trang-thai.json` cũ (không có `bat_dau`/`ket_thuc`, không có `loai`) vẫn tải và chạy bình thường (Task 1, 2).
5. Kịch bản đổi sau khi đã có cảnh: cảnh nào khớp kém được báo để xem lại, không đoán ngầm (Task 3).

---

### Task 0: Nền sạch

- [ ] **Step 1:** `uv run pytest -q`. Expected: toàn bộ PASS (ghi số test).
- [ ] **Step 2:** `git status --short -- pipeline/tttc/dang.py pipeline/tttc/kiem.py pipeline/tttc/canh.py pipeline/tttc/dung.py pipeline/tests/test_dang.py pipeline/tests/test_kiem.py theo-doi.csv`. Các tệp ở trạng thái `M` là thay đổi chưa commit từ trước. **Dừng và hỏi người dùng** commit riêng hoặc stash trước khi sửa `dang.py` ở Task 5.

### Task 1: Giờ từng bước (H1)

**Files:**
- Modify: `pipeline/tttc/trang_thai.py` (`STATUSES`, `set_step`, thêm `gio` và dòng lệnh)
- Test: `pipeline/tests/test_trang_thai.py`

**Interfaces:**
- Produces: `STATUSES` thêm `"dang-chay"` (vẫn được `next_step` coi là bước chưa xong). `set_step(video_dir, step, status, note="", now: datetime | None = None)` giữ các trường cũ của bước (gộp, không thay cả dict); ghi `bat_dau` (ISO, UTC+7) khi `status == "dang-chay"` và chưa có; ghi `ket_thuc` khi `status` ∈ {`xong`, `da-duyet`, `cho-duyet`, `loi`}. `gio(video_dir) -> {"buoc": {step: giây}, "tong": giây | None}`: mỗi bước có cả `bat_dau` và `ket_thuc`; `tong` = `ket_thuc` của `duyet-2` − `bat_dau` của `chu-de` (None nếu thiếu). Dòng lệnh `python -m tttc.trang_thai gio <thư mục>` in từng bước dạng `mm:ss` và tổng.

- [ ] **Step 1: Viết test**

```python
from datetime import datetime, timedelta, timezone
VN = timezone(timedelta(hours=7))
def at(h, m=0): return datetime(2026, 11, 10, h, m, tzinfo=VN)

def test_set_step_records_start_and_end(tmp_path):
    tt.set_step(tmp_path, "giong", "dang-chay", now=at(11, 0))
    tt.set_step(tmp_path, "giong", "xong", "ok", now=at(11, 12))
    s = tt.load(tmp_path)["steps"]["giong"]
    assert (s["status"], s["note"]) == ("xong", "ok")
    assert s["bat_dau"] == at(11, 0).isoformat() and s["ket_thuc"] == at(11, 12).isoformat()

def test_gio_reports_seconds_per_step_and_total(tmp_path):
    tt.set_step(tmp_path, "chu-de", "dang-chay", now=at(6, 30)); tt.set_step(tmp_path, "chu-de", "xong", now=at(6, 45))
    tt.set_step(tmp_path, "duyet-2", "dang-chay", now=at(14, 0)); tt.set_step(tmp_path, "duyet-2", "da-duyet", now=at(14, 20))
    g = tt.gio(tmp_path)
    assert g["buoc"]["chu-de"] == 900 and g["buoc"]["duyet-2"] == 1200 and g["tong"] == 28200

def test_gio_total_is_none_without_both_ends(tmp_path):
    tt.set_step(tmp_path, "chu-de", "xong", now=at(6, 45))
    assert tt.gio(tmp_path)["tong"] is None

def test_running_step_is_still_pending(tmp_path):
    for s in ["chu-de", "nguon", "kich-ban", "phan-bien-giong", "kiem", "duyet-1"]:
        tt.set_step(tmp_path, s, "xong" if s != "duyet-1" else "da-duyet")
    tt.set_step(tmp_path, "giong", "dang-chay")
    assert tt.next_step(tmp_path) == "giong"
```

- [ ] **Step 2:** `uv run pytest tests/test_trang_thai.py -q`. Expected: FAIL.
- [ ] **Step 3:** Implement theo Interfaces. Thời điểm mặc định là `datetime.now(timezone(timedelta(hours=7)))`. Các test cũ của tệp phải PASS.
- [ ] **Step 4:** `uv run pytest tests/test_trang_thai.py -q`. Expected: PASS.
- [ ] **Step 5: Commit**

```bash
git add pipeline/tttc/trang_thai.py pipeline/tests/test_trang_thai.py
git commit -m "feat: ghi giờ bắt đầu/kết thúc từng bước và lệnh gio"
```

### Task 2: Shorts sau khi đăng (H6) và kho dự trữ (H8)

**Files:**
- Modify: `pipeline/tttc/trang_thai.py` (`STEPS`, thêm `kho`)
- Test: `pipeline/tests/test_trang_thai.py`

**Interfaces:**
- Produces: `STEPS` đặt `"shorts"` **sau** `"dang"` (còn `... "render", "dong-goi", "duyet-2", "dang", "shorts"`). `kho(videos_root) -> list[Path]`: thư mục con có `trang-thai.json` với `loai == "evergreen"`, `duyet-2` = `da-duyet`, `dang` ≠ `xong`, sắp theo tên. Trường `loai` ghi bằng `set_field(dir, "loai", "evergreen")`.

- [ ] **Step 1: Viết test**

```python
def test_shorts_come_after_publishing():
    assert tt.STEPS.index("shorts") > tt.STEPS.index("dang") > tt.STEPS.index("duyet-2")

def test_next_step_after_review_2_is_dang_not_shorts(tmp_path):
    for s in tt.STEPS[: tt.STEPS.index("duyet-2")]:
        tt.set_step(tmp_path, s, "xong")
    tt.set_step(tmp_path, "duyet-1", "da-duyet"); tt.set_step(tmp_path, "duyet-2", "da-duyet")
    assert tt.next_step(tmp_path) == "dang"

def test_kho_lists_approved_unpublished_evergreen_only(tmp_path):
    def mk(name, loai, duyet2, dang):
        d = tmp_path / name; d.mkdir()
        tt.set_field(d, "loai", loai); tt.set_step(d, "duyet-2", duyet2); tt.set_step(d, "dang", dang)
    mk("a-ok", "evergreen", "da-duyet", "chua-chay")
    mk("b-da-dang", "evergreen", "da-duyet", "xong")
    mk("c-nong", "nong", "da-duyet", "chua-chay")
    mk("d-chua-duyet", "evergreen", "cho-duyet", "chua-chay")
    (tmp_path / "e-khong-so").mkdir()
    assert [p.name for p in tt.kho(tmp_path)] == ["a-ok"]
```

- [ ] **Step 2:** `uv run pytest tests/test_trang_thai.py -q`. Expected: FAIL.
- [ ] **Step 3:** Implement. Video cũ có `shorts` đã `xong` thì không bị ảnh hưởng.
- [ ] **Step 4:** Sửa `.claude/skills/video-dung/SKILL.md`: chuyển mục 5 (shorts) thành "sau khi đăng, buổi tối" và ghi giờ đăng Short là sáng hôm sau; `.claude/skills/video-dang/SKILL.md` nhắc dựng và đăng Shorts sau video dài. Chạy `uv run pytest -q`. Expected: PASS.
- [ ] **Step 5: Commit**

```bash
git add pipeline/tttc/trang_thai.py pipeline/tests/test_trang_thai.py .claude/skills/video-dung/SKILL.md .claude/skills/video-dang/SKILL.md
git commit -m "feat: Shorts tách khỏi đường găng, kho dự trữ evergreen"
```

### Task 3: Ánh xạ lại cảnh khi kịch bản đổi (H5)

**Files:**
- Create: `pipeline/tttc/canh_remap.py`, `pipeline/tests/test_canh_remap.py`

**Interfaces:**
- Produces: `remap(canh: dict, old_timing: dict, new_timing: dict) -> tuple[dict, list[str]]`. `canh = {"scenes": [{"id","start","end",...}]}`; `*_timing = {"duration": float, "words": [{"w","start","end"}]}`. Với mỗi cảnh cũ lấy dãy từ của `old_timing` nằm trong `[start, end)`, so khớp với từ của `new_timing` bằng `difflib.SequenceMatcher` trên từ đã hạ chữ thường; `start`/`end` mới là mốc từ khớp đầu/cuối của dãy. Cảnh cũ có < 60% từ khớp được nội suy mốc và ghi vào danh sách thông báo `Cảnh báo: cảnh {id} chỉ khớp {x:.0%} lời, cần xem lại`. Kết quả luôn liền mạch: cảnh đầu `start` = 0, `end` mỗi cảnh = `start` cảnh sau, cảnh cuối `end` = `new_timing["duration"]`. Mọi trường khác của cảnh giữ nguyên. `main(video_dir: str, old_timing_path: str) -> int`: sao lưu `canh.json` thành `canh-truoc-remap.json`, ghi `canh.json` mới, in thông báo, trả 0.

- [ ] **Step 1: Viết test**

```python
from tttc import canh_remap

def T(words, step=1.0):
    ws = [{"w": w, "start": i * step, "end": (i + 1) * step} for i, w in enumerate(words)]
    return {"duration": len(words) * step, "words": ws}

OLD = T("một hai ba bốn năm sáu bảy tám chín mười".split())
CANH = {"scenes": [{"id": "c1", "start": 0.0, "end": 5.0, "mau": "so-lon"},
                   {"id": "c2", "start": 5.0, "end": 10.0, "mau": "minh-hoa", "nhan": "X"}]}

def test_remap_shifts_scenes_when_words_are_inserted():
    new = T("một hai THÊM THÊM ba bốn năm sáu bảy tám chín mười".split())
    out, notes = canh_remap.remap(CANH, OLD, new)
    s = out["scenes"]
    assert s[0]["start"] == 0.0 and s[0]["end"] == s[1]["start"] == 7.0 and s[1]["end"] == new["duration"]
    assert s[1]["mau"] == "minh-hoa" and s[1]["nhan"] == "X" and notes == []

def test_remap_flags_scene_whose_words_were_rewritten():
    new = T("một hai ba bốn năm AAA BBB CCC DDD EEE".split())
    _, notes = canh_remap.remap(CANH, OLD, new)
    assert len(notes) == 1 and "c2" in notes[0] and "cần xem lại" in notes[0]

def test_remap_keeps_scenes_contiguous_when_text_is_shorter():
    new = T("một hai ba bốn năm sáu bảy".split())
    out, _ = canh_remap.remap(CANH, OLD, new)
    s = out["scenes"]
    assert s[0]["start"] == 0.0 and s[-1]["end"] == new["duration"] and s[0]["end"] == s[1]["start"]
```

- [ ] **Step 2:** `uv run pytest tests/test_canh_remap.py -q`. Expected: FAIL (`ModuleNotFoundError`).
- [ ] **Step 3:** Implement `remap` và `main`; thêm khối `__main__` (`python -m tttc.canh_remap <thư mục video> <timing cũ.json>`).
- [ ] **Step 4:** `uv run pytest tests/test_canh_remap.py -q`. Expected: PASS.
- [ ] **Step 5: Commit**

```bash
git add pipeline/tttc/canh_remap.py pipeline/tests/test_canh_remap.py
git commit -m "feat: canh_remap chuyển cảnh cũ sang mốc mới khi kịch bản đổi"
```

### Task 4: Radar chọn đề và RSS đối thủ (H7)

**Files:**
- Create: `pipeline/tttc/radar.py`, `pipeline/tests/test_radar.py`, `pipeline/tests/fixtures/rss-doi-thu.xml`
- Modify: `pipeline/config.json` (thêm `"doi_thu": {"ten": "@MotCongNghe", "kenh_id": "UC91zSg_iPgJZZL6KB91BewQ"}`)

**Interfaces:**
- Produces:
  - `doc_rss(channel_id: str, get=requests.get) -> list[dict]`: mỗi mục `{"id": str, "tieu_de": str, "dang_luc": datetime (có múi giờ, đổi sang UTC+7), "view": int | None}`; bỏ qua mục hỏng; ném `RuntimeError("RSS đối thủ không đọc được: ...")` khi HTTP lỗi hoặc XML không phân tích được. Không gửi tiêu đề, giờ, view đi đâu khác.
  - `cham_diem(soc: int, so_lon: int, goc_vn: int) -> int` = `soc + so_lon + 2 * goc_vn`; `ValueError` nếu thành phần ngoài 0–2.
  - `xep_hang(de: list[dict], toi_thieu: int = 4) -> list[dict]`: mỗi đề có `tieu_de, soc, so_lon, goc_vn, link, moi_luc (datetime)`; trả đề đạt điểm, thêm khóa `diem`, sắp theo (điểm giảm, `goc_vn > 0` trước, `moi_luc` mới trước).
  - `ghi_chu_de(video_dir, top: list[dict], ho_da_dang: dict[str, bool] | None = None) -> Path` ghi `chu-de.md` với tối đa 3 đề: `## Đề {n}: {tieu_de}`, dòng `- Điểm: {diem} (sốc {soc}, số lớn {so_lon}, góc Việt Nam {goc_vn}×2)`, `- Tin gốc: {link}`, `- Họ đã đăng cùng sự kiện: có|không|chưa rõ` (theo `ho_da_dang[tieu_de]`).
  - Dòng lệnh `python -m tttc.radar rss` in mỗi video của đối thủ dạng `dd/mm HH:MM · {view} view · {tiêu đề}`.

- [ ] **Step 1: Viết test.** Tạo `fixtures/rss-doi-thu.xml` là Atom thu nhỏ với 2 `<entry>` hợp lệ (có `yt:videoId`, `title`, `published`, `media:group/media:community/media:statistics views="11180"`) và 1 `<entry>` thiếu `published`. Namespace: Atom `http://www.w3.org/2005/Atom`, yt `http://www.youtube.com/xml/schemas/2015`, media `http://search.yahoo.com/mrss/`.

```python
from datetime import datetime, timedelta, timezone
import pytest
from tttc import radar
VN = timezone(timedelta(hours=7))

class Resp:
    def __init__(self, text, code=200): self.text, self.status_code = text, code
    def raise_for_status(self):
        if self.status_code != 200: raise RuntimeError(self.status_code)

def test_doc_rss_parses_entries_in_vietnam_time_and_skips_broken(fixture_rss):
    items = radar.doc_rss("UCx", get=lambda url, **kw: Resp(fixture_rss))
    assert len(items) == 2 and items[0]["view"] == 11180
    assert items[0]["dang_luc"].utcoffset() == timedelta(hours=7)

def test_doc_rss_raises_on_http_error_or_bad_xml():
    with pytest.raises(RuntimeError):
        radar.doc_rss("UCx", get=lambda url, **kw: Resp("", 500))
    with pytest.raises(RuntimeError):
        radar.doc_rss("UCx", get=lambda url, **kw: Resp("<not-xml"))

def test_cham_diem_weights_vietnam_angle_double_and_validates():
    assert radar.cham_diem(2, 2, 2) == 8 and radar.cham_diem(2, 2, 0) == 4 and radar.cham_diem(0, 0, 2) == 4
    with pytest.raises(ValueError):
        radar.cham_diem(3, 0, 0)

def _de(t, soc, sl, vn, moi=10):
    return {"tieu_de": t, "soc": soc, "so_lon": sl, "goc_vn": vn, "link": "u", "moi_luc": datetime(2026, 11, 9, moi, tzinfo=VN)}

def test_xep_hang_drops_below_threshold_and_orders_ties_by_vietnam_angle_then_recency():
    top = radar.xep_hang([_de("thấp", 1, 1, 0), _de("A không VN", 2, 2, 0, moi=12),
                          _de("B có VN", 1, 1, 1, moi=8), _de("C có VN mới", 1, 1, 1, moi=9)])
    assert [d["tieu_de"] for d in top] == ["C có VN mới", "B có VN", "A không VN"] and top[0]["diem"] == 4

def test_ghi_chu_de_writes_three_ranked_ideas(tmp_path):
    top = radar.xep_hang([_de(f"Đề {i}", 2, 2, 1, moi=i + 1) for i in range(5)])
    p = radar.ghi_chu_de(tmp_path, top, {"Đề 4": True})
    txt = p.read_text(encoding="utf-8")
    assert txt.count("## Đề ") == 3 and "Họ đã đăng cùng sự kiện: có" in txt and "góc Việt Nam 1×2" in txt
```
(`fixture_rss` là pytest fixture đọc tệp XML.)

- [ ] **Step 2:** `uv run pytest tests/test_radar.py -q`. Expected: FAIL.
- [ ] **Step 3:** Implement bằng `xml.etree.ElementTree` và `datetime.fromisoformat`; `requests.get(url, timeout=20)`. Thêm khóa `doi_thu` vào `config.json`.
- [ ] **Step 4:** `uv run pytest tests/test_radar.py -q`. Expected: PASS. Chạy thật `uv run python -m tttc.radar rss`. Expected: in ≥ 10 dòng video của đối thủ.
- [ ] **Step 5: Commit**

```bash
git add pipeline/tttc/radar.py pipeline/tests/test_radar.py pipeline/tests/fixtures/rss-doi-thu.xml pipeline/config.json
git commit -m "feat: radar chọn đề (chấm điểm, xếp hạng) và đọc RSS đối thủ"
```

### Task 5: Sổ theo dõi có cột so sánh với đối thủ

**Files:**
- Create: `pipeline/tttc/theo_doi.py`, `pipeline/tests/test_theo_doi.py`
- Modify: `pipeline/tttc/dang.py:16-17,72-79` (`FIELDS`, `_track`)
- Test: `pipeline/tests/test_dang.py`

**Interfaces:**
- Produces: `theo_doi.EXTRA = ["trung_de_ho", "chenh_gio", "radar_hang", "view_ho_24h"]`; `theo_doi.migrate(path: Path) -> None`: nếu tệp tồn tại và thiếu cột `EXTRA` thì thêm vào cuối header, mỗi dòng cũ giữ nguyên giá trị và điền rỗng; `chenh_gio(gio_minh: datetime, gio_ho: datetime) -> float` = (giờ mình − giờ họ) tính bằng giờ, âm là sớm hơn; `ty_so_trung_vi(rows: list[dict]) -> float | None`: trung vị của `view_24h / view_ho_24h` trên tối đa 10 dòng cuối có cả hai giá trị là số dương, None nếu không có dòng nào. `dang.FIELDS` = các cột cũ + `EXTRA`; `dang._track` gọi `migrate` trước khi ghi và ghi các cột mới rỗng.

- [ ] **Step 1: Viết test**

```python
import csv
from datetime import datetime, timedelta, timezone
from tttc import theo_doi
VN = timezone(timedelta(hours=7))
OLD = "ngay,tieu_de,gio_dang,link,view_24h,view_7d,ctr,giu_chan_30s\n09/11/2026,Tiêu đề,09/11/2026 20:45,https://youtu.be/x,,,,\n"

def test_migrate_adds_columns_without_losing_data(tmp_path):
    p = tmp_path / "theo-doi.csv"; p.write_text(OLD, encoding="utf-8")
    theo_doi.migrate(p)
    rows = list(csv.DictReader(p.open(encoding="utf-8")))
    assert list(rows[0])[:8] == ["ngay", "tieu_de", "gio_dang", "link", "view_24h", "view_7d", "ctr", "giu_chan_30s"]
    assert list(rows[0])[8:] == theo_doi.EXTRA and rows[0]["tieu_de"] == "Tiêu đề" and rows[0]["chenh_gio"] == ""

def test_migrate_is_idempotent_and_ignores_missing_file(tmp_path):
    p = tmp_path / "theo-doi.csv"; p.write_text(OLD, encoding="utf-8")
    theo_doi.migrate(p); first = p.read_text(encoding="utf-8"); theo_doi.migrate(p)
    assert p.read_text(encoding="utf-8") == first
    theo_doi.migrate(tmp_path / "khong-co.csv")

def test_chenh_gio_negative_when_earlier():
    a = datetime(2026, 11, 10, 15, 30, tzinfo=VN); b = datetime(2026, 11, 10, 18, 0, tzinfo=VN)
    assert theo_doi.chenh_gio(a, b) == -2.5

def test_ty_so_trung_vi_uses_last_ten_complete_rows():
    rows = [{"view_24h": "100", "view_ho_24h": "1000"}, {"view_24h": "", "view_ho_24h": "500"},
            {"view_24h": "300", "view_ho_24h": "1000"}, {"view_24h": "200", "view_ho_24h": "0"}]
    assert theo_doi.ty_so_trung_vi(rows) == 0.2 and theo_doi.ty_so_trung_vi([]) is None
```
Trong `test_dang.py` thêm: khi `theo-doi.csv` cũ 8 cột đã tồn tại, `dang._track(tracker, "T", "10/11/2026 15:30", "vid")` để lại header có 12 cột và dòng cũ còn nguyên.

- [ ] **Step 2:** `uv run pytest tests/test_theo_doi.py tests/test_dang.py -q`. Expected: FAIL.
- [ ] **Step 3:** Implement `theo_doi.py`; sửa `FIELDS` và `_track` trong `dang.py`.
- [ ] **Step 4:** `uv run pytest tests/test_theo_doi.py tests/test_dang.py -q`. Expected: PASS. Chạy `uv run python -c "from tttc import theo_doi, dang; theo_doi.migrate(dang.TRACKER)"` rồi `head -2 ../theo-doi.csv`: header đủ 12 cột, dòng video nvidia còn nguyên.
- [ ] **Step 5: Commit** (chỉ sau khi Task 0 đã xử lý các thay đổi cũ của `dang.py`)

```bash
git add pipeline/tttc/theo_doi.py pipeline/tests/test_theo_doi.py pipeline/tttc/dang.py pipeline/tests/test_dang.py theo-doi.csv
git commit -m "feat: sổ theo dõi thêm cột so sánh với đối thủ, di trú không mất dữ liệu"
```

### Task 6: Tốc độ đọc và ước tính độ dài (H3, H4)

**Files:**
- Modify: `pipeline/config.json` (`vieneu.toc_do`, thêm `vieneu.wpm_co_so`), `pipeline/tttc/phong_cach.py` (thêm `uoc_tinh_phut`, `main` in ước tính)
- Test: `pipeline/tests/test_phong_cach.py`
- Create: `docs/nghien-cuu/toc-do-vieneu-2026-11-09.md`

**Interfaces:**
- Produces: `phong_cach.uoc_tinh_phut(script_md: str, wpm: float) -> float` = số từ lời đọc (không tính thẻ `[#id]`) / `wpm`; `main` in thêm dòng `ước tính {x:.1f} phút ở {wpm:.0f} từ/phút` với `wpm = vieneu.wpm_co_so / vieneu.toc_do` đọc từ `config.json`.

- [ ] **Step 1: Viết test**

```python
def test_uoc_tinh_phut_counts_spoken_words_only():
    md = _long(head=OK_HEAD, n=2300)
    assert abs(phong_cach.uoc_tinh_phut(md, 230) - 2300 / 230) < 0.05
    assert phong_cach.uoc_tinh_phut("Chỉ ghi chú.", 230) == 0.0
```

- [ ] **Step 2:** `uv run pytest tests/test_phong_cach.py -q`. Expected: FAIL.
- [ ] **Step 3:** Implement `uoc_tinh_phut` (dùng `_split` có sẵn) và dòng in trong `main`.
- [ ] **Step 4: Đo thật, không sửa video đã đăng.** Tạo `videos/thu-nghiem/toc-do/`, chép `kich-ban.md` của `2026-11-15-nvidia-siet-chip` và các tệp wav gốc (tên 10 ký tự hex, không phải `u*.wav`) trong `giong-vieneu/` vào đó. Với `vieneu.toc_do` lần lượt 1.0 rồi 0.92, chạy `uv run python -m tttc.giong_vieneu videos/thu-nghiem/toc-do` (wav gốc dùng lại, chỉ áp `atempo` và ghép), rồi đo tốc độ bằng `len(words) / (duration / 60)` từ `giong-timing.json` của thư mục thử. Ghi bảng vào `docs/nghien-cuu/toc-do-vieneu-2026-11-09.md`. Chọn `toc_do` đưa tốc độ vào 180–230 từ/phút; nếu không giá trị nào đạt thì nêu lý do và đề xuất ngưỡng mới trong tài liệu, không tự sửa ngưỡng. Đặt `vieneu.wpm_co_so` = tốc độ đo ở `toc_do` 1.0.
- [ ] **Step 5:** `uv run pytest -q`. Expected: PASS.
- [ ] **Step 6: Commit**

```bash
git add pipeline/config.json pipeline/tttc/phong_cach.py pipeline/tests/test_phong_cach.py docs/nghien-cuu/toc-do-vieneu-2026-11-09.md
git commit -m "feat: ước tính phút đọc, hiệu chỉnh toc_do VieNeu theo số đo"
```

### Task 7: Cổng chạy khô `chay_kho`

**Files:**
- Create: `pipeline/tttc/chay_kho.py`, `pipeline/tests/test_chay_kho.py`

**Interfaces:**
- Consumes: `trang_thai.gio/load` (Task 1), `phong_cach.kiem`, `kiem.check`, `chat_luong.do/kiem`, `dung.check_av`.
- Produces: `kiem(video_dir) -> list[str]` trả các tiêu chí **chưa đạt**, mỗi mục bắt đầu bằng `Chưa đạt {n}:` với n = 1–7 theo thứ tự: (1) `duyet-2` xong sau 15:00 giờ Việt Nam hoặc chưa xong; (2) `trang-thai.json` có `can_thiep_tay` (danh sách) không rỗng; (3) `tttc.kiem` có lỗi, `chat_luong` có `Lỗi`, hoặc thiếu `final.mp4`/`giong.mp3`, hoặc `check_av` không rỗng; (4) tốc độ đọc ngoài 180–230; (5) bước nào từ `chu-de` đến `duyet-2` thiếu `ket_thuc`; (6) có thông báo `chat_luong` chứa "độ khô" (tiêu chí của kế hoạch hình ảnh; chưa có thì bỏ qua); (7) `phong_cach.kiem` còn `Lỗi`, hoặc thiếu `phan-bien-giong-1.md` / `phan-bien-giong-2.md`. Dòng lệnh `python -m tttc.chay_kho <thư mục>` in từng mục, `Đạt cả 7 tiêu chí` hoặc `{k} tiêu chí chưa đạt`, trả 1 nếu còn mục chưa đạt.

- [ ] **Step 1: Viết test** cho tiêu chí 1, 2, 5, 7 bằng sổ và tệp giả trong `tmp_path`; ví dụ:

```python
def test_criterion_1_duyet_2_after_15h_is_unmet(tmp_path):
    tt.set_step(tmp_path, "duyet-2", "da-duyet", now=datetime(2026, 11, 10, 15, 20, tzinfo=VN))
    assert any(m.startswith("Chưa đạt 1:") for m in chay_kho.kiem(tmp_path))
    tt.set_step(tmp_path, "duyet-2", "da-duyet", now=datetime(2026, 11, 10, 14, 50, tzinfo=VN))
    assert not any(m.startswith("Chưa đạt 1:") for m in chay_kho.kiem(tmp_path))

def test_criterion_2_manual_interventions(tmp_path):
    tt.set_field(tmp_path, "can_thiep_tay", ["sửa canh c012"])
    assert any(m.startswith("Chưa đạt 2:") and "1" in m for m in chay_kho.kiem(tmp_path))

def test_criterion_7_needs_both_review_rounds(tmp_path):
    (tmp_path / "phan-bien-giong-1.md").write_text("x", encoding="utf-8")
    assert any(m.startswith("Chưa đạt 7:") for m in chay_kho.kiem(tmp_path))

def test_empty_video_reports_unmet_criteria(tmp_path):
    got = {m[:10] for m in chay_kho.kiem(tmp_path)}
    assert {"Chưa đạt 1", "Chưa đạt 3", "Chưa đạt 4", "Chưa đạt 5", "Chưa đạt 7"} <= got
    assert "Chưa đạt 2" not in got  # tiêu chí 2 chỉ báo khi can_thiep_tay không rỗng
```

- [ ] **Step 2:** `uv run pytest tests/test_chay_kho.py -q`. Expected: FAIL.
- [ ] **Step 3:** Implement: mỗi tiêu chí là một hàm nhỏ trả `str | None`; tiêu chí cần tệp thiếu thì trả thông báo "thiếu ...", không ném lỗi.
- [ ] **Step 4:** `uv run pytest tests/test_chay_kho.py -q`. Expected: PASS.
- [ ] **Step 5: Commit**

```bash
git add pipeline/tttc/chay_kho.py pipeline/tests/test_chay_kho.py
git commit -m "feat: chay_kho kiểm 7 tiêu chí của cổng chạy khô"
```

### Task 8: Cấu hình, thẻ phong cách (công thức), SKILL (H0)

**Files:**
- Modify: `docs/phong-cach-kich-ban.md`, `pipeline/config.json:gio_dang_mac_dinh`, `.claude/skills/video-moi/SKILL.md` (mục 1), `.claude/skills/video-moi|video-dung|video-dang/SKILL.md` (mô tả)
- Modify: `ke-hoach-nhan-ban-MotCongNghe.md`, `lich-4-tuan-dinh-vi-A.md` (đầu tệp thêm dòng "Đã thay thế bởi `docs/superpowers/specs/2026-11-09-dinh-vi-doi-dau-van-hanh-design.md`")

- [ ] **Step 1:** Viết lại `docs/phong-cach-kich-ban.md` mục 1 (người dẫn), 3 (cấu trúc), 7 (nhịp và hình) theo công thức kênh mẫu: mở bằng sự kiện + cặp số + câu hỏi; 3 phần có chương; ví dụ đời thường mỗi 1–2 phút; nói nguồn ngay trong lời; kết trả lời câu hỏi tiêu đề và mời bình luận một con số. Giữ nguyên mục 2 và các luật an toàn (không nhận định suông, nguồn tận gốc, nhãn "mình tự tính", không khuyên đầu tư, không phán xét hãng, nói rõ cái chưa kiểm). "Phán quyết túi tiền" và "điều kiện đổi ý" chuyển thành tùy chọn. Mục 6 và mục "Vai kể" do kế hoạch giọng văn sửa; không đụng ở đây.
- [ ] **Step 2:** `video-moi/SKILL.md` mục 1 (chu-de): thay luật 3 câu cũ bằng bảng chấm của radar (soc, so_lon, goc_vn×2; đạt ≥ 4; goc_vn = 0 không tự loại); bước quét: chạy `uv run python -m tttc.radar rss`, chấm điểm, ghi `chu-de.md` bằng `radar.ghi_chu_de`, đặt cờ `ho_da_dang` theo RSS. Bỏ tham chiếu `lich-4-tuan-dinh-vi-A.md`. Đổi chữ "Túi Tiền Công Nghệ" trong ba mô tả SKILL thành "kênh" (tên mới do kế hoạch nhận diện đặt).
- [ ] **Step 3:** Đặt `gio_dang_mac_dinh` = `"15:30"`. Kiểm: `grep -n gio_dang_mac_dinh pipeline/config.json` in `15:30`; `uv run pytest -q` PASS.
- [ ] **Step 4:** Tạo `docs/quy-tac-quyet-dinh.md` chép nguyên mục 9 của spec (hai thước đo, mốc G+14/G+30, luật dừng và đổi hướng với các ngưỡng đánh dấu là đề xuất) để người dùng tra khi xem `theo-doi.csv`.
- [ ] **Step 5: Commit**

```bash
git add docs/phong-cach-kich-ban.md docs/quy-tac-quyet-dinh.md pipeline/config.json .claude/skills ke-hoach-nhan-ban-MotCongNghe.md lich-4-tuan-dinh-vi-A.md
git commit -m "docs: thẻ phong cách theo công thức kênh mẫu, radar trong video-moi, giờ đăng 15:30, quy tắc quyết định"
```

### Task 9: Hạn mức YouTube (H9) — cần bạn

**Files:** Create `docs/nghien-cuu/han-muc-youtube-2026-11-09.md`.

- [ ] **Step 1 (bạn làm):** Mở Google Cloud Console → dự án đã cấp OAuth → APIs & Services → YouTube Data API v3 → Quotas. Chép con số "Queries per day" và mức đã dùng hôm nay vào tệp.
- [ ] **Step 2:** Từ số đó và các lời gọi trong `dang.py` (`videos.insert` cho video dài và từng Short, `thumbnails.set`, `captions.insert`, `playlistItems.insert`), ghi vào tệp: số lượt tải lên tối đa mỗi ngày và quyết định (giữ 3 Shorts, giảm Shorts, hoặc xin tăng hạn mức). Số 1.600 đơn vị mỗi `videos.insert` và hạn mức mặc định 10.000/ngày là hiểu biết chưa kiểm của tôi, phải thay bằng số trong bảng của chính Google.
- [ ] **Step 3: Commit** `git add docs/nghien-cuu/han-muc-youtube-2026-11-09.md && git commit -m "docs: hạn mức YouTube thực tế và quyết định số Shorts mỗi ngày"`.

### Task 10: Tác vụ định kỳ 06:30 — cần bạn xác nhận

Đây là cấu hình bền vững ngoài repo nên **phải có xác nhận của bạn** trước khi tạo.

- [ ] **Step 1:** Hỏi bạn: giờ chạy (đề xuất 06:30 giờ Việt Nam, hằng ngày), chấp nhận máy phải mở và không ngủ, và chấp nhận thông báo khi kịch bản chờ duyệt.
- [ ] **Step 2:** Sau khi bạn đồng ý, tạo bằng công cụ tác vụ định kỳ (`mcp__scheduled-tasks__create_scheduled_task`) với lời nhắc: "Trong `/Users/quangtinh/Documents/Youtube`, chạy quy trình `video-moi` cho đề 1 của radar tới điểm duyệt 1 (gồm phản biện giọng văn 2 vòng với agy). Không tự duyệt. Khi `duyet-1.html` sẵn sàng thì gửi thông báo." Kiểm: tác vụ xuất hiện trong `mcp__scheduled-tasks__list_scheduled_tasks`; chạy thử một lần bằng `run_scheduled_task` và ghi kết quả.

### Task 11: Ba ngày chạy khô và mở G

**Yêu cầu trước:** kế hoạch giọng văn, nhận diện (lớp màu, bộ nhân vật, khung thumbnail) và hình ảnh (cấu hình render, đạo diễn, mẫu cảnh, độ khô) đã xong.

- [ ] **Step 1:** Mỗi ngày trong 3 ngày liên tiếp (2 đề evergreen đặt `set_field(dir, "loai", "evergreen")`, 1 đề nóng thật từ radar): chạy tới `duyet-2`, không đăng. Mọi can thiệp tay ghi vào `can_thiep_tay` bằng `set_field`.
- [ ] **Step 2:** Mỗi ngày chạy `uv run python -m tttc.chay_kho ../videos/<slug>` và `uv run python -m tttc.trang_thai gio ../videos/<slug>`. Expected: `Đạt cả 7 tiêu chí` cho cả ba ngày liên tiếp. Trượt một ngày thì sửa chỗ vỡ và làm lại đủ ba ngày.
- [ ] **Step 3:** Ghi số giờ thật từng bước vào `docs/nghien-cuu/chay-kho-2026-11-XX.md`; hiệu chỉnh các ngưỡng đánh dấu "đề xuất" (giờ đăng, 45 phút đạo diễn, ngưỡng giọng văn) dựa trên số đó.
- [ ] **Step 4:** Quyết định cùng bạn về video `goi-ai-dang-tien` (đã duyệt, dựng bằng nhận diện cũ): render lại bằng nhận diện mới (khoảng 25 phút) để đăng, hoặc bỏ. Ghi quyết định vào tài liệu chạy khô.
- [ ] **Step 5:** Điều kiện mở **G**: ba ngày đạt, `uv run python -c "from tttc import trang_thai as t; from pathlib import Path; print(len(t.kho(Path('../videos'))))"` in số ≥ 3, tệp hạn mức ở Task 9 đã quyết, và bạn xác nhận. Commit tài liệu: `git add docs/nghien-cuu && git commit -m "docs: kết quả ba ngày chạy khô"`.
