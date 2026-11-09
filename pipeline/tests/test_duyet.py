import json

import pytest

from tttc import duyet, trang_thai as tt

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
    tt.set_step(tmp_path, "phan-bien-giong", "xong", "vòng 1: 5 mục (nhận 4, bỏ 1); vòng 2: 1 mục")
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


def test_review_page_takes_colours_from_theme(tmp_path, monkeypatch):
    from tttc import theme
    monkeypatch.setattr(theme, "TH", {**theme.TH, "nen": "#0A0B0C", "nhan": ["#00AAFF", "#0088CC", "#006699"]})
    html = duyet.render_review_1(_video(tmp_path)).read_text(encoding="utf-8")
    assert "--bg:#0A0B0C" in html and "--accent:#00AAFF" in html and "#FFC800" not in html
