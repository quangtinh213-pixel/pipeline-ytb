from tttc import nhan_vat, theme

KIT = {"the": ["chao", "nghi"], "huong": ["truoc", "nghieng-trai", "nghieng-phai", "ngang"],
       "dang": [["chao", "truoc"], ["chao", "nghieng-trai"], ["nghi", "truoc"]], "nham": [["chao", "truoc"]]}


def test_hop_le_and_default_direction_faces_screen_centre():
    assert nhan_vat.hop_le("chao", "nghieng-trai", KIT) and not nhan_vat.hop_le("nghi", "ngang", KIT)
    assert nhan_vat.huong_mac_dinh("phai") == "nghieng-trai" and nhan_vat.huong_mac_dinh("trai") == "nghieng-phai"


def test_tep_names():
    assert nhan_vat.tep("chao", "truoc") == "chao-truoc.png" and nhan_vat.tep("chao", "truoc", True) == "chao-truoc-nham.png"


def test_doc_kit_missing_file_is_none(tmp_path):
    assert nhan_vat.doc_kit(tmp_path / "khong-co.json") is None


def test_doc_kit_reads_default_path_at_call_time(tmp_path, monkeypatch):
    (tmp_path / "kit.json").write_text('{"the": ["chao"], "huong": [], "dang": [], "nham": []}', encoding="utf-8")
    monkeypatch.setattr(nhan_vat, "KIT", tmp_path / "kit.json")
    assert nhan_vat.doc_kit()["the"] == ["chao"]


def test_prompt_has_brief_expression_angle_and_palette():
    p = nhan_vat.tao_prompt("ngac-nhien", "nghieng-trai")
    assert "no text" in p and "no logo" in p and "no real person" in p and "flat" in p
    assert nhan_vat.BIEU_CAM["ngac-nhien"] in p and nhan_vat.GOC["nghieng-trai"] in p
    assert theme.TH["nhan"][0] in p and "eyes closed" not in p
    assert "eyes closed" in nhan_vat.tao_prompt("chao", "truoc", nham=True)


def test_six_expressions_and_four_angles_defined():
    assert len(nhan_vat.BIEU_CAM) == 6 and len(nhan_vat.GOC) == 4
    assert {"chao", "ngac-nhien", "nghi"} <= set(nhan_vat.BIEU_CAM)  # tên cũ giữ nguyên để cảnh cũ vẫn chạy
    assert set(nhan_vat.GOC) == {"truoc", "nghieng-trai", "nghieng-phai", "ngang"}


def test_unknown_expression_or_angle_raises():
    import pytest
    with pytest.raises(KeyError):
        nhan_vat.tao_prompt("buon", "truoc")


def test_short_prompt_relies_on_references_but_keeps_hard_rules():
    full, short = nhan_vat.tao_prompt("nghi", "ngang"), nhan_vat.tao_prompt("nghi", "ngang", ngan=True)
    assert len(short) < len(full) * 0.7
    for must in ("no text", "no logo", "no real person", "reference", nhan_vat.BIEU_CAM["nghi"], nhan_vat.GOC["ngang"], "chroma-key green"):
        assert must in short
    assert "eyes closed" in nhan_vat.tao_prompt("nghi", "truoc", nham=True, ngan=True)


def test_expressions_have_no_glow_halos_that_pick_up_the_green_background():
    for the, mo_ta in nhan_vat.BIEU_CAM.items():
        low = mo_ta.lower()
        assert not any(w in low for w in ("glow", "flaring", "pulsing", "halo", "ring", "wave", "ray")), the
    assert "no glow" in nhan_vat.tao_prompt("ngac-nhien", "truoc", ngan=True)
