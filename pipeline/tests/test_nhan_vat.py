from tttc import nhan_vat

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
