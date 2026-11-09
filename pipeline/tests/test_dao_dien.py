import json

import pytest

from tttc import canh, dao_dien

KHUNG = {"scenes": [{"id": "c1", "start": 0.0, "end": 4.0, "loi": "một hai ba bốn năm sáu bảy tám chín mười"},
                    {"id": "c2", "start": 4.0, "end": 8.0, "loi": "a b c d e f g h"}]}
TIMING = {"duration": 8.0, "words": [{"w": w, "start": i * 0.4, "end": i * 0.4 + 0.3}
                                     for i, w in enumerate((KHUNG["scenes"][0]["loi"] + " " + KHUNG["scenes"][1]["loi"]).split())]}


@pytest.fixture
def svg_dir(tmp_path):
    d = tmp_path / "svg"
    d.mkdir()
    for n in ("nen-dat", "chip", "cay", "dong-xu"):
        (d / f"{n}.svg").write_text("<svg/>", encoding="utf-8")
    return d


def _dd(**over):
    s1 = {"id": "c1", "y": "mở", "nhip_cam_xuc": "mo", "trong_diem": True, "an_du": "cái cân", "san_khau": "nen-dat",
          "vat_chinh": "chip", "dao_cu": ["cay", "dong-xu"], "may_quay": "day-vao",
          "canh": {"mau": "minh-hoa", "nhan": "Chip"}}
    s2 = {"id": "c2", "y": "chốt", "nhip_cam_xuc": "chot", "trong_diem": False,
          "canh": {"mau": "so-lon", "so": 5, "nhan": "X", "nguon_id": "p1"}}
    return {"scenes": [{**s1, **over.get("s1", {})}, {**s2, **over.get("s2", {})}]}


def test_validate_clean_director_file(svg_dir):
    assert [m for m in dao_dien.validate(_dd(), KHUNG, svg_dir) if m.startswith("Lỗi")] == []


@pytest.mark.parametrize("over,key", [
    ({"s1": {"y": ""}}, "thiếu y"), ({"s1": {"an_du": ""}}, "an_du"), ({"s1": {"may_quay": "dung"}}, "may_quay"),
    ({"s1": {"nhip_cam_xuc": "la"}}, "nhip_cam_xuc"), ({"s1": {"san_khau": "mars"}}, "san_khau"),
    ({"s1": {"trong_diem": "co"}}, "trong_diem"), ({"s2": {"canh": {"mau": "khong-co"}}}, "mau"),
    ({"s1": {"dao_cu": ["cay"] * 5}}, "dao_cu")])
def test_validate_flags_each_director_rule(over, key, svg_dir):
    assert any(m.startswith("Lỗi") and key in m for m in dao_dien.validate(_dd(**over), KHUNG, svg_dir))


def test_validate_flags_missing_and_unknown_scenes(svg_dir):
    dd = _dd()
    dd["scenes"].pop()
    assert any(m.startswith("Lỗi") and "c2" in m for m in dao_dien.validate(dd, KHUNG, svg_dir))
    dd = _dd()
    dd["scenes"][1]["id"] = "c9"
    assert any(m.startswith("Lỗi") and "c9" in m for m in dao_dien.validate(dd, KHUNG, svg_dir))


def test_undrawn_props_warn_and_are_queued(svg_dir):
    dd = _dd(s1={"dao_cu": ["chua-ve", "chua-ve"]})
    assert any(m.startswith("Cảnh báo") and "chua-ve" in m for m in dao_dien.validate(dd, KHUNG, svg_dir))
    assert dao_dien.hinh_thieu(dd, svg_dir) == ["chua-ve"]


def test_sinh_canh_keeps_timing_contiguous_and_builds_layout_and_nhip():
    out = dao_dien.sinh_canh(_dd(), KHUNG, TIMING)["scenes"]
    assert [(s["id"], s["start"], s["end"]) for s in out] == [("c1", 0.0, 4.0), ("c2", 4.0, 8.0)]
    s = out[0]
    assert s["mau"] == "minh-hoa" and s["svg"] == "chip" and s["san_khau"] == "nen-dat" and s["may_quay"] == "day-vao"
    assert [b["svg"] for b in s["bo_cuc"]] == ["cay", "dong-xu"]
    assert (s["bo_cuc"][0]["x"], s["bo_cuc"][0]["y"]) == dao_dien.SLOT[0]
    assert len(s["nhip"]) == 3 and all(canh.phrase_time(TIMING["words"], p, s["start"], s["end"]) is not None for p in s["nhip"])
    assert len(out[1]["nhip"]) == 2 and out[1]["so"] == 5


def test_sinh_canh_respects_explicit_fields_and_dan(svg_dir):
    dd = _dd(s1={"canh": {"mau": "minh-hoa", "svg": "laptop", "phu": ["cay"], "nhip": [None, "ba bốn", None]},
                 "dan": {"the": "chao", "goc": "phai"}})
    s = dao_dien.sinh_canh(dd, KHUNG, TIMING)["scenes"][0]
    assert s["svg"] == "laptop" and s["phu"] == ["cay"] and "bo_cuc" not in s and s["nhip"] == [None, "ba bốn", None]
    assert s["dan"] == {"the": "chao", "goc": "phai"}


def test_main_writes_canh_json_backup_and_hinh_thieu(tmp_path, svg_dir, monkeypatch):
    monkeypatch.setattr(dao_dien, "SVG_DIR", svg_dir)
    for name, data in (("dao-dien.json", _dd()), ("canh-khung.json", KHUNG), ("giong-timing.json", TIMING),
                       ("canh.json", {"scenes": [{"id": "cu"}]})):
        (tmp_path / name).write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    assert dao_dien.main(str(tmp_path)) == 0
    assert json.loads((tmp_path / "canh-truoc-dao-dien.json").read_text(encoding="utf-8")) == {"scenes": [{"id": "cu"}]}
    assert [s["id"] for s in json.loads((tmp_path / "canh.json").read_text(encoding="utf-8"))["scenes"]] == ["c1", "c2"]
    assert json.loads((tmp_path / "hinh-thieu.json").read_text(encoding="utf-8")) == []


def test_main_refuses_and_keeps_canh_json_when_errors(tmp_path, svg_dir, monkeypatch, capsys):
    monkeypatch.setattr(dao_dien, "SVG_DIR", svg_dir)
    bad = _dd(s1={"y": ""})
    for name, data in (("dao-dien.json", bad), ("canh-khung.json", KHUNG), ("giong-timing.json", TIMING),
                       ("canh.json", {"scenes": [{"id": "cu"}]})):
        (tmp_path / name).write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    assert dao_dien.main(str(tmp_path)) == 1 and "Lỗi" in capsys.readouterr().out
    assert json.loads((tmp_path / "canh.json").read_text(encoding="utf-8")) == {"scenes": [{"id": "cu"}]}
