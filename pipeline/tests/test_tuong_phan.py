import shutil

from PIL import Image, ImageDraw

from tttc import tuong_phan

VUNG = (210, 960, 1710, 1044)


def _png(tmp_path, name, bg, fg):
    im = Image.new("RGB", (1920, 1080), bg)
    ImageDraw.Draw(im).rectangle([300, 980, 1600, 1030], fill=fg)  # "chữ" giả: một khối màu fg trên nền bg
    p = tmp_path / name
    im.save(p)
    return p


def test_ti_le_high_for_white_on_black_and_low_for_flat_grey(tmp_path):
    assert tuong_phan.ti_le(_png(tmp_path, "a.png", (0, 0, 0), (255, 255, 255)), VUNG) > 7
    assert tuong_phan.ti_le(_png(tmp_path, "b.png", (200, 200, 200), (210, 210, 210)), VUNG) < 1.2


def test_kiem_phu_de_reports_only_unreadable_scene(tmp_path):
    good = _png(tmp_path, "good.png", (17, 17, 17), (255, 255, 255))
    bad = _png(tmp_path, "bad.png", (200, 200, 200), (210, 210, 210))
    canh = {"scenes": [{"id": "c1", "start": 0.0, "end": 4.0}, {"id": "c2", "start": 4.0, "end": 8.0}]}

    def run(cmd, **kw):  # ffmpeg giả: -ss <giây> ... <tệp ra>
        t = float(cmd[cmd.index("-ss") + 1])
        shutil.copy(good if t < 4 else bad, cmd[-1])

    out = tuong_phan.kiem_phu_de(tmp_path / "final.mp4", canh, run=run)
    assert len(out) == 1 and "c2" in out[0] and out[0].startswith("Cảnh báo") and "khó đọc" in out[0]


def test_main_prints_warnings_and_exits_zero(tmp_path, capsys, monkeypatch):
    import json
    (tmp_path / "canh.json").write_text(json.dumps({"scenes": [{"id": "c1", "start": 0.0, "end": 4.0}]}), encoding="utf-8")
    (tmp_path / "final.mp4").write_bytes(b"x")
    bad = _png(tmp_path, "bad.png", (200, 200, 200), (210, 210, 210))
    monkeypatch.setattr(tuong_phan.subprocess, "run", lambda cmd, **kw: shutil.copy(bad, cmd[-1]))
    assert tuong_phan.main(str(tmp_path)) == 0
    assert "c1" in capsys.readouterr().out


def test_kiem_phu_de_skips_frames_without_caption(tmp_path):
    flat = _png(tmp_path, "flat.png", (17, 17, 17), (17, 17, 17))  # không có chữ trong dải phụ đề (đang lặng)
    canh = {"scenes": [{"id": "c1", "start": 0.0, "end": 4.0}]}
    assert tuong_phan.kiem_phu_de(tmp_path / "f.mp4", canh, run=lambda cmd, **kw: shutil.copy(flat, cmd[-1])) == []
