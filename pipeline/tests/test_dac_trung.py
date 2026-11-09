"""Test đặc trưng: khóa hành vi hiện tại của thư viện SVG và đầu ra compose trước khi chuyển màu sang theme.
Khi cố ý đổi palette thì sinh lại golden-compose.sha256 và ghi lý do trong commit."""
import hashlib
import importlib.util
import json
from pathlib import Path

from tttc import dung

FIX = Path(__file__).resolve().parent / "fixtures"
GOLDEN = FIX / "golden-compose.sha256"
SVG_DIR = Path(__file__).resolve().parents[1] / "svg"

NGUON = [{"id": "p1", "gia_tri": "522.500 đ", "trich_dan": "", "url": "https://chatgpt.com/vi-VN/pricing",
          "ngay_truy_cap": "2026-11-07", "anh_chup": "nguon/p1.png", "trang_thai": "xac-minh"}]
SCENES = {"scenes": [
    {"id": "c1", "mau": "chuong", "start": 0, "end": 4, "so": "Phần 1", "chuong": "Mở đầu"},
    {"id": "c2", "mau": "minh-hoa", "start": 4, "end": 9, "svg": "chip", "nhan": "Chip", "sac": "xanh"},
    {"id": "c3", "mau": "so-lon", "start": 9, "end": 14, "so": 522500, "sau": " đ", "nhan": "Plus", "nguon_id": "p1"},
    {"id": "c4", "mau": "bieu-do", "start": 14, "end": 20, "nhan": "Giá",
     "bieu_do": {"kieu": "cot", "nhan_x": ["Go", "Plus"], "gia_tri": [132000, 522500], "don_vi": "đ",
                 "noi_bat": 1, "nguon_id": "p1"}},
]}
TIMING = {"duration": 20.0, "words": [{"w": "Xin", "start": 0.1, "end": 0.4}, {"w": "chào.", "start": 0.5, "end": 0.9}],
          "paragraphs": []}


def make_video(tmp_path):
    d = tmp_path / "v"
    d.mkdir()
    (d / "canh.json").write_text(json.dumps(SCENES, ensure_ascii=False), encoding="utf-8")
    (d / "giong-timing.json").write_text(json.dumps(TIMING), encoding="utf-8")
    (d / "nguon.json").write_text(json.dumps(NGUON, ensure_ascii=False), encoding="utf-8")
    (d / "giong.mp3").write_bytes(b"mp3")
    return d


def golden_compose_hash(composition_dir) -> str:
    root, h = Path(composition_dir), hashlib.sha256()
    for p in sorted(x for x in root.rglob("*") if x.is_file()):
        h.update(p.relative_to(root).as_posix().encode())
        h.update(p.read_bytes())
    return h.hexdigest()


def test_regenerated_svgs_are_byte_identical_to_committed(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location("ve", SVG_DIR / "ve.py")
    ve = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ve)
    monkeypatch.setattr(ve, "OUT", tmp_path)
    for name, fn in ve.ITEMS.items():
        ve.save(name, fn())
    for f in sorted(SVG_DIR.glob("*.svg")):
        assert (tmp_path / f.name).read_bytes() == f.read_bytes(), f.name


def test_compose_output_is_unchanged(tmp_path):
    out = dung.compose(make_video(tmp_path))
    assert golden_compose_hash(out) == GOLDEN.read_text(encoding="utf-8").strip()
