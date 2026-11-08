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
