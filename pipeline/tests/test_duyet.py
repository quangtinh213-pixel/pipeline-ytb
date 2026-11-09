import json
from tttc import duyet

NGUON = [
    {"id": "p1", "gia_tri": "522.500 đ", "trich_dan": "Plus <script>alert(1)</script>",
     "url": "https://chatgpt.com/vi-VN/pricing", "ngay_truy_cap": "2026-11-07",
     "anh_chup": "nguon/p1.png", "trang_thai": "xac-minh"},
    {"id": "g1", "gia_tri": "489.000 đ", "trich_dan": "AI Pro", "url": "https://one.google.com",
     "ngay_truy_cap": "2026-11-07", "anh_chup": "", "trang_thai": "so-bo"},
]


def _video(tmp_path, script="Gói Plus 522.500 đồng. [#p1]"):
    (tmp_path / "nguon.json").write_text(json.dumps(NGUON, ensure_ascii=False), encoding="utf-8")
    (tmp_path / "kich-ban.md").write_text(script, encoding="utf-8")
    (tmp_path / "chu-de.md").write_text("## Đề 1\nGói AI", encoding="utf-8")
    return tmp_path


def test_review_1_lists_every_source_id(tmp_path):
    html = duyet.render_review_1(_video(tmp_path)).read_text(encoding="utf-8")
    for n in NGUON:
        assert n["id"] in html and n["url"] in html


def test_review_1_shows_kiem_errors(tmp_path):
    html = duyet.render_review_1(_video(tmp_path, "Giá 999.999 đồng.")).read_text(encoding="utf-8")
    assert 'class="canh-bao"' in html and "999.999" in html


def test_review_1_no_warning_block_when_clean(tmp_path):
    html = duyet.render_review_1(_video(tmp_path)).read_text(encoding="utf-8")
    assert 'class="canh-bao"' not in html


def test_review_1_escapes_html(tmp_path):
    html = duyet.render_review_1(_video(tmp_path)).read_text(encoding="utf-8")
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


def test_review_1_written_to_video_dir(tmp_path):
    assert duyet.render_review_1(_video(tmp_path)) == tmp_path / "duyet-1.html"


GOI = {"phuong_an": [{"tieu_de": f"Tiêu đề {i}", "chu_thumb": ["X"], "file_thumb": f"thumbnails/{i}.png"}
                     for i in (1, 2, 3)],
       "mo_ta": "Mô tả <b>video</b>", "tags": ["a"],
       "shorts": [{"file": "shorts/1.mp4", "tieu_de": "S1", "ngay": "14/11/2026", "gio": "12:00"}]}


def _video2(tmp_path):
    d = _video(tmp_path)
    (d / "dong-goi.json").write_text(json.dumps(GOI, ensure_ascii=False), encoding="utf-8")
    return d


def test_review_2_lists_three_options(tmp_path):
    html = duyet.render_review_2(_video2(tmp_path)).read_text(encoding="utf-8")
    for i in (1, 2, 3):
        assert f"Tiêu đề {i}" in html and f'src="thumbnails/{i}.png"' in html
    assert "&lt;b&gt;video" in html


def test_review_2_links_video_and_shorts(tmp_path):
    html = duyet.render_review_2(_video2(tmp_path)).read_text(encoding="utf-8")
    assert '<video controls src="final.mp4"' in html and 'src="shorts/1.mp4"' in html
    assert "14/11/2026 12:00" in html


def test_review_2_shows_remaining_warnings(tmp_path):
    html = duyet.render_review_2(_video2(tmp_path)).read_text(encoding="utf-8")
    assert 'class="canh-bao"' in html and "g1" in html and "sơ bộ" in html


def test_review_2_shows_quality_warnings(tmp_path):
    d = _video2(tmp_path)
    scenes = [{"id": f"c{i}", "mau": "so-lon", "start": i * 6.0, "end": i * 6.0 + 6.0} for i in range(3)]
    (d / "canh.json").write_text(json.dumps({"scenes": scenes}), encoding="utf-8")
    (d / "giong-timing.json").write_text(json.dumps({"duration": 18.0, "words": []}), encoding="utf-8")
    html = duyet.render_review_2(d).read_text(encoding="utf-8")
    assert "Độ dài trung bình" in html


def test_sources_table_shows_formula_for_tu_tinh(tmp_path):
    d = _video(tmp_path)
    tt = {"id": "t1", "gia_tri": "15 năm", "trang_thai": "tu-tinh", "cong_thuc": "2026 − 2011", "dau_vao": ["p1"]}
    (d / "nguon.json").write_text(json.dumps(NGUON + [tt], ensure_ascii=False), encoding="utf-8")
    html = duyet.render_review_1(d).read_text(encoding="utf-8")
    assert "#t1" in html and "2026 − 2011" in html


def test_review_1_shows_style_warnings(tmp_path):
    d = _video(tmp_path, "#### Beat 1\n**Lời đọc:**\nChào các bạn.\n")
    html = duyet.render_review_1(d).read_text(encoding="utf-8")
    assert 'class="canh-bao"' in html and "90 từ đầu" in html
