import pytest

from tttc import ngon_ngu


@pytest.mark.parametrize("text", [
    "Vietnam: [D:1] National Security X; [D:3] Chemical & Biological X",
    "I was unfaithful to my wife. My actions hurt her and our children.",
    "Imposing additional export licensing requirements",
])
def test_english_text_is_detected(text):
    assert ngon_ngu.la_tieng_anh(text)


@pytest.mark.parametrize("text", [
    "Bỏ quy tắc AI Diffusion", "Chip AI và luật", "Nvidia Huawei", "GPU", "8/11", "Phần 2", "Gấp ~700 lần",
    "Quy tắc thay thế ra chưa?", "", "Hạ viện Mỹ",
])
def test_vietnamese_labels_and_short_names_are_not_flagged(text):
    assert not ngon_ngu.la_tieng_anh(text)


def test_man_hinh_lists_every_text_field_of_each_template():
    c = {"mau": "so-sanh", "trai": {"nhan": "A", "don_vi": "tỷ"}, "phai": {"nhan": "B"}, "ti_le": "gấp 3", "nhan": "X"}
    assert {t for _, t in ngon_ngu.man_hinh(c)} >= {"A", "tỷ", "B", "gấp 3", "X"}
    q = {"mau": "quy-trinh", "tieu_de": "Quy trình", "buoc": [{"nhan": "Một"}, {"nhan": "Hai"}]}
    assert {t for _, t in ngon_ngu.man_hinh(q)} == {"Quy trình", "Một", "Hai"}
    t = {"mau": "trich-bao", "trich": "English quote here", "trich_vi": "Câu trích tiếng Việt"}
    assert [x for _, x in ngon_ngu.man_hinh(t)] == ["Câu trích tiếng Việt"]  # chỉ bản hiển thị, không phải nguyên văn


def test_man_hinh_covers_map_points_and_links():
    c = {"mau": "ban-do", "tieu_de": "Đường đi", "diem": [{"nhan": "Mỹ"}, {"nhan": "Malaysia"}], "noi": [{"tu": 0, "den": 1, "nhan": "chip AI"}]}
    assert {t for _, t in ngon_ngu.man_hinh(c)} == {"Đường đi", "Mỹ", "Malaysia", "chip AI"}
