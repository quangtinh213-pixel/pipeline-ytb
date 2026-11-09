import unicodedata
from tttc.kiem import check

NGUON = [
    {"id": "p1", "gia_tri": "522.500 đ", "trich_dan": "Plus 522.500 ₫/tháng",
     "url": "https://chatgpt.com/vi-VN/pricing", "ngay_truy_cap": "2026-11-07",
     "anh_chup": "nguon/p1.png", "trang_thai": "xac-minh"},
    {"id": "s1", "gia_tri": "159 tỷ USD", "trich_dan": "...", "url": "https://x",
     "ngay_truy_cap": "2026-11-07", "anh_chup": "", "trang_thai": "so-bo"},
    {"id": "u1", "gia_tri": "80 tỷ USD", "trich_dan": "...", "url": "https://y",
     "ngay_truy_cap": "2026-11-07", "anh_chup": "", "trang_thai": "chua-xac-minh"},
]


def test_number_without_source():
    errs = check("Giá 522.500 đồng mỗi tháng.", NGUON)
    assert len(errs) == 1 and "không có nguồn" in errs[0]


def test_sourced_number_ok():
    assert check("Gói Plus giá 522.500 đồng mỗi tháng. [#p1]", NGUON) == []


def test_unknown_source_id():
    errs = check("Giá 522.500 đồng. [#x9]", NGUON)
    assert any("x9" in e for e in errs)


def test_value_mismatch():
    errs = check("Giá 522.000 đồng. [#p1]", NGUON)
    assert len(errs) == 1 and "522.000" in errs[0]


def test_placeholder_left():
    errs = check("Khoảng [ĐỔI TỶ GIÁ NGÀY QUAY: 20 USD = ... đ] mỗi tháng.", NGUON)
    assert any("giữ chỗ" in e for e in errs)


def test_screen_marker_is_not_placeholder():
    assert check("[TRÊN MÀN HÌNH]: Bảng giá.", NGUON) == []


def test_so_bo_needs_warning():
    errs = check("Hàng Việt bán sang Mỹ 159 tỷ đô. [#s1]", NGUON)
    assert any("sơ bộ" in e for e in errs)
    assert check("Theo số sơ bộ, hàng Việt bán sang Mỹ 159 tỷ đô. [#s1]", NGUON) == []


def test_unverified_source_blocked():
    errs = check("Công ty lỗ 80 tỷ đô. [#u1]", NGUON)
    assert any("chưa xác minh" in e for e in errs)


def test_number_words_ok():
    assert check("Gói Plus giá năm trăm hai mươi hai nghìn đồng. [#p1]", NGUON) == []


def test_dates_times_and_small_counts_ignored():
    assert check("Ngày 07/11/2026 lúc 19:00, mình so 3 hãng.", NGUON) == []


def test_check_handles_nfd_text():
    script = unicodedata.normalize("NFD", "Theo số sơ bộ, hàng Việt bán sang Mỹ 159 tỷ đô. [#s1]")
    assert check(script, NGUON) == []


def test_headings_skipped():
    assert check("#### Beat 70: Giá 2026", NGUON) == []


SRC = [{"id": "a", "gia_tri": "35 triệu USD", "trich_dan": "", "url": "u", "ngay_truy_cap": "2026-11-07",
        "anh_chup": "", "trang_thai": "xac-minh"}]


def test_small_number_with_unit_needs_source():
    assert check("Lợi nhuận 7 triệu.", NGUON) and check("Thị phần tăng 8%.", NGUON)
    assert check("Giá 5 đô mỗi tháng.", NGUON)


def test_space_grouped_thousands_detected():
    assert check("Giá 1 000 000 đồng.", NGUON)


def test_wrong_scale_rejected():
    assert check("Công ty có 35 tỷ USD. [#a]", SRC)
    assert check("Công ty có 3,5 triệu USD. [#a]", SRC)
    assert check("Công ty có 35 triệu USD. [#a]", SRC) == []


def test_spoken_number_words_need_source():
    errs = check("Apple mất ba nghìn tỷ đô.", NGUON)
    assert errs and "chữ" in errs[0]
    assert check("Apple mất ba nghìn tỷ đô. [#p1]", NGUON) == []


def test_english_decimal_with_unit_flagged():
    errs = check("Giá chip là 2.5 USD.", NGUON)
    assert any("2,5" in e for e in errs)
    assert check("Gemini 2.5 Pro ra mắt.", NGUON) == []


TT = {"id": "t1", "gia_tri": "15 năm", "trich_dan": "", "url": "", "ngay_truy_cap": "2026-11-09",
      "anh_chup": "", "trang_thai": "tu-tinh", "cong_thuc": "2026 − 2011", "dau_vao": ["s1"]}


def test_tu_tinh_requires_formula_and_inputs():
    line = "Đã 15 năm, mình tự tính. [#t1]"
    no_formula = dict(TT, cong_thuc="")
    bad_input = dict(TT, dau_vao=["zz"])
    assert any("cong_thuc" in e for e in check(line, NGUON + [no_formula]))
    assert any("zz" in e for e in check(line, NGUON + [bad_input]))
    assert check(line, NGUON + [TT]) == []


def test_tu_tinh_requires_label_phrase():
    errs = check("Đã 15 năm rồi. [#t1]", NGUON + [TT])
    assert len(errs) == 1 and "tự tính" in errs[0]
    assert check("Phép tính này là mình tự ướm, tròn 15 năm. [#t1]", NGUON + [TT]) == []


def test_tu_tinh_value_still_matched():
    errs = check("Đã 16 năm, mình tự tính. [#t1]", NGUON + [TT])
    assert len(errs) == 1 and "không khớp" in errs[0]
