import json
from pathlib import Path
from tttc import kham


def test_tim_cu_roi_ignores_first_2pct_and_sorts_by_drop_size():
    pts = [(0.01, 1.00), (0.02, 0.90), (0.05, 0.82), (0.10, 0.70), (0.20, 0.68), (0.50, 0.40)]
    roi = kham.tim_cu_roi(pts, thoi_luong=500.0, nguong_diem=5.0)
    assert [r["roi_diem"] for r in roi] == [28.0, 12.0, 8.0]
    assert roi[1]["giay"] == 50.0 and roi[1]["mmss"] == "0:50"
    assert kham.tim_cu_roi([], 500.0) == [] and kham.tim_cu_roi([(0.1, 0.9)], 0.0) == []


def test_khop_boi_canh_and_tao_kham_nghiem(tmp_path):
    (tmp_path / "phu-de.srt").write_text(
        "1\n00:00:00,000 --> 00:00:20,000\nCâu mở đầu chuẩn.\n\n"
        "2\n00:00:20,000 --> 00:00:35,000\nTrong thông tư có một chi tiết lạ.\n",
        encoding="utf-8",
    )
    (tmp_path / "canh.json").write_text(json.dumps({
        "scenes": [
            {"id": "c001", "mau": "so-lon", "start": 0.0, "end": 20.0},
            {"id": "c002", "mau": "trang-nguon", "start": 20.0, "end": 35.0},
        ]
    }), encoding="utf-8")
    ctx = kham.khop_boi_canh(tmp_path, 25.0)
    assert "chi tiết lạ" in ctx["thoai"] and ctx["canh_id"] == "c002" and ctx["mau"] == "trang-nguon"

    pts = [(0.02, 0.95), (0.05, 0.80), (0.10, 0.72), (0.50, 0.42), (1.0, 0.25)]
    out = kham.tao_kham_nghiem(tmp_path, pts, thoi_luong=500.0, ctr="6.3%", hien_thi="7855")
    txt = out.read_text(encoding="utf-8")
    assert out == tmp_path / "kham-nghiem.md"
    assert "0:25" in txt and "chi tiết lạ" in txt and "trang-nguon" in txt


def test_khop_boi_canh_handles_missing_files_gracefully(tmp_path):
    ctx = kham.khop_boi_canh(tmp_path, 10.0)
    assert ctx == {"thoai": "—", "canh_id": "—", "mau": "—"}
