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


GOI = {"phuong_an": [{"tieu_de": f"Tiêu đề {i}", "chu_thumb": ["X"], "file_thumb": f"thumbnails/{i}.png", "khuon": "ho-so"}
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
    assert "Cảnh bằng chứng" in html


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


def test_review_2_shows_do_kho_from_director_and_judge_files(tmp_path):
    d = _video2(tmp_path)
    scenes = [{"id": f"c{i}", "mau": "so-lon", "start": i * 3.0, "end": i * 3.0 + 3.0} for i in range(3)]
    (d / "canh.json").write_text(json.dumps({"scenes": scenes}), encoding="utf-8")
    (d / "giong-timing.json").write_text(json.dumps({"duration": 9.0, "words": []}), encoding="utf-8")
    (d / "dao-dien-cham.json").write_text(json.dumps({"beats": [{"y_nghia": 2, "da_dang": 2, "chieu_sau": 2, "nhip": 2}]}), encoding="utf-8")
    html = duyet.render_review_2(d).read_text(encoding="utf-8")
    assert "độ khô" in html and "điểm giám khảo trung bình 2.0" in html


def test_review_1_checks_cta_and_administrative_style_when_spoken_present(tmp_path):
    d = _video(tmp_path, "#### Beat 1\n**Lời đọc:**\nGói Plus 522.500 đồng theo thông tư số một. [#p1]\n")
    html = duyet.render_review_1(d).read_text(encoding="utf-8")
    assert "Đăng Ký" in html and "hành chính" in html

    d2 = _video(tmp_path, "#### Beat 1\n**Lời đọc:**\nGói Plus 522.500 đồng. Nhớ đăng ký kênh nhé! [#p1]\n")
    html2 = duyet.render_review_1(d2).read_text(encoding="utf-8")
    assert "Đăng Ký" not in html2


def test_review_2_shows_title_score_source_match_and_long_thumb_warning(tmp_path):
    d = _video(tmp_path)
    goi = {
        "phuong_an": [
            {
                "tieu_de": "SỐC: Ông chủ Microsoft 365 từ chức vì người dùng Việt Nam?",
                "chu_thumb": ["DÒNG CHỮ QUÁ BỐN TỪ RỒI"],
                "file_thumb": "thumbnails/1.png",
            }
        ],
        "mo_ta": "Mô tả",
        "tags": ["microsoft"],
        "shorts": [],
    }
    (d / "dong-goi.json").write_text(json.dumps(goi, ensure_ascii=False), encoding="utf-8")
    html = duyet.render_review_2(d).read_text(encoding="utf-8")
    assert "Điểm tiêu đề:" in html and "/10" in html
    assert "Chữ thumbnail dài quá 4 từ" in html
    assert "lệch nguồn" in html and "danh từ chung" in html
    assert "#NhipCongNghe #Microsoft" in html


def test_review_1_warns_when_main_script_uses_short_template_loai(tmp_path):
    d = _video(tmp_path, "# Tiêu đề\nLoại: ra-mat\n\n#### Beat 1\n**Lời đọc:**\nGói Plus 522.500 đồng. Nhớ đăng ký kênh! [#p1]\n")
    html = duyet.render_review_1(d).read_text(encoding="utf-8")
    assert "Loại: ra-mat" in html


def test_review_1_includes_kiem_thoi_luong_thuc_warning(tmp_path):
    d = _video(tmp_path, "#### Beat 1\n**Lời đọc:**\nGói Plus 522.500 đồng. Nhớ đăng ký kênh! [#p1]\n")
    html = duyet.render_review_1(d).read_text(encoding="utf-8")
    assert "Cảnh báo thời lượng" in html


def test_review_2_flags_thumbnail_not_on_locked_template(tmp_path):
    d = _video(tmp_path)
    goi = {**GOI, "phuong_an": [{**GOI["phuong_an"][0], "khuon": "ban-co-toi"}, {**GOI["phuong_an"][1], "khuon": "khung"},
                                {k: v for k, v in GOI["phuong_an"][2].items() if k != "khuon"}]}
    (d / "dong-goi.json").write_text(json.dumps(goi, ensure_ascii=False), encoding="utf-8")
    html = duyet.render_review_2(d).read_text(encoding="utf-8")
    assert "Phương án 1: Lỗi: thumbnail" not in html
    assert "Phương án 2: Lỗi: thumbnail không theo khuôn đã khóa" in html
    assert "Phương án 3: Lỗi: thumbnail không theo khuôn đã khóa" in html


def test_review_2_bao_loi_video_dai_duoi_7_phut(tmp_path, monkeypatch):
    from tttc import dang
    d = _video2(tmp_path)
    (d / "final.mp4").write_bytes(b"x")
    monkeypatch.setattr(dang, "thoi_luong", lambda _p: 141.0)
    html = duyet.render_review_2(d).read_text(encoding="utf-8")
    assert "Lỗi: Video dài 2:21" in html and "Shorts" in html
    monkeypatch.setattr(dang, "thoi_luong", lambda _p: 600.0)
    assert "Lỗi: Video dài" not in duyet.render_review_2(d).read_text(encoding="utf-8")


def test_review_1_hien_canh_bao_40_giay_dau(tmp_path):
    d = _video(tmp_path, script="**Lời đọc:**\nGói Plus 522.500 đồng. [#p1] Mình đọc lại văn bản gốc thì thấy lạ. Ai mua? Ai bán?\n")
    html = duyet.render_review_1(d).read_text(encoding="utf-8")
    assert "nói về việc kể chuyện" in html and "câu hỏi" in html


def test_review_2_canh_bao_tieu_de_lech_15_giay_dau(tmp_path):
    d = _video(tmp_path, script="**Lời đọc:**\nGói Plus 522.500 đồng. [#p1] Google cũng bán gói AI.\n")
    goi = {**GOI, "phuong_an": [{**GOI["phuong_an"][0], "tieu_de": "Nvidia mất 190 tỷ USD: Việt Nam mua chip khó hơn?"}]}
    (d / "dong-goi.json").write_text(json.dumps(goi, ensure_ascii=False), encoding="utf-8")
    html = duyet.render_review_2(d).read_text(encoding="utf-8")
    assert "tiêu đề nhắc «Nvidia»" in html and "tiêu đề có số «190 tỷ»" in html
