import pytest

from tttc import theme


def test_cssify_resolves_nested_and_indexed_keys():
    th = {"nen": "#111111", "nhan": ["#FFC800", "#E0B000"], "kem": {"nen": "#FBF6EC"}}
    assert theme.cssify("a {{theme:nen}} b {{theme:nhan.1}} c {{theme:kem.nen}}", th) == "a #111111 b #E0B000 c #FBF6EC"


def test_cssify_unknown_key_names_it():
    with pytest.raises(KeyError, match="khong_co"):
        theme.cssify("{{theme:khong_co}}", {"nen": "#111111"})


def test_cssify_leaves_plain_css_untouched():
    assert theme.cssify("a { color: red; } b {{ x }}", {"nen": "#111111"}) == "a { color: red; } b {{ x }}"


def test_contrast_known_values():
    assert theme.contrast("#000000", "#FFFFFF") == pytest.approx(21.0, abs=0.01)
    assert theme.contrast("#111111", "#FFC800") > 4.5


def test_current_theme_passes_its_own_check():
    assert [m for m in theme.kiem(theme.load()) if m.startswith("Lỗi")] == []


def test_kiem_rejects_accent_equal_to_semantic_colour_and_low_contrast():
    th = theme.load()
    th["nhan"] = list(th["sac"]["lam"][:3])
    assert any("trùng" in m for m in theme.kiem(th))
    th = theme.load()
    th["chu_tren_nhan"] = th["nhan"][0]
    assert any("tương phản" in m for m in theme.kiem(th))


def test_kiem_warns_black_yellow_pair_only_for_a_new_identity():
    th = theme.load()
    assert not any("đen–vàng" in m for m in theme.kiem(th))  # nhận diện Nhịp Công Nghệ không còn cặp đen–vàng
    th = {**th, "nen": "#111111", "nhan": ["#FFC800", "#E0B000", "#C79C00"], "ten": "hien-tai"}
    assert not any("đen–vàng" in m for m in theme.kiem(th))  # bản cũ tên hien-tai được miễn
    th["ten"] = "kenh-moi"
    assert any(m.startswith("Cảnh báo") and "đen–vàng" in m for m in theme.kiem(th))


def test_derived_constants_match_current_code():
    assert theme.VANG == ("#22D3EE", "#10A8C4", "#0B7F96") and theme.SAC["xanh"][0] == "#00D084"  # nhấn ngọc lam của Nhịp Công Nghệ


def test_brand_colors_are_the_svg_palette():
    assert theme.brand_colors() == {"#08181C", "#FFFFFF", "#BDBDBD", "#6E6E6E", "#2A2A2A", "#22D3EE", "#10A8C4", "#0B7F96"}


def test_ap_dung_runs_generators_then_checks_theme():
    from pathlib import Path
    calls = []
    out = theme.ap_dung(run=lambda cmd, **kw: calls.append(Path(cmd[1]).name))
    assert calls == ["ve.py", "make_brand.py", "sheet.py"]
    assert [m for m in out if m.startswith("Lỗi")] == []


def test_main_ap_dung_exit_code_follows_theme_errors(monkeypatch):
    noop = lambda *a, **k: None
    assert theme.main(["ap-dung"], run=noop) == 0
    monkeypatch.setattr(theme, "TH", {**theme.TH, "chu_tren_nhan": theme.TH["nhan"][0]})
    assert theme.main(["ap-dung"], run=noop) == 1
    assert theme.main(["khac"], run=noop) == 2
