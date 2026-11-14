import subprocess

from tttc import chuan_sfx


def test_gain_targets_peak_but_caps_loud_sustained_sounds():
    assert abs(chuan_sfx.do_loi(tb=-26.2, dinh=-3.2) - 0.2) < 1e-9
    assert abs(chuan_sfx.do_loi(tb=-34.7, dinh=-6.2) - 3.2) < 1e-9     # tiếng nhỏ: kéo đỉnh lên −3 dBFS
    assert abs(chuan_sfx.do_loi(tb=-5.0, dinh=-0.4) - -13.0) < 1e-9    # bass kéo dài: hạ theo trần trung bình


def test_normalizes_files_and_second_run_is_noop(tmp_path):
    for ten, amp in (("nho", 0.05), ("to", 0.9)):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "sine=f=800:d=0.5", "-af", f"volume={amp}",
                        str(tmp_path / f"{ten}.mp3")], check=True)
    assert {t for t, _ in chuan_sfx.chuan_hoa(tmp_path)} == {"nho.mp3", "to.mp3"}
    for ten in ("nho", "to"):
        tb, dinh = chuan_sfx.do_muc(tmp_path / f"{ten}.mp3")
        assert dinh <= -2.4 and tb <= -17.4
    assert chuan_sfx.chuan_hoa(tmp_path) == []
