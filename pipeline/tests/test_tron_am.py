import re
import subprocess

from tttc import tron_am


def _run(args):
    return subprocess.run(args, capture_output=True, text=True, check=True)


def _tone(path, freq, seconds, amp=1.0, gap=None):
    vol = f"volume='if(between(t,{gap[0]},{gap[1]}),0,{amp})':eval=frame" if gap else f"volume={amp}"
    _run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"sine=f={freq}:d={seconds}:r=44100",
          "-af", vol, "-c:a", "libmp3lame", "-b:a", "128k", str(path)])
    return path


def _dur(p):
    return float(_run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)]).stdout)


def _level(p, f, t0, t1):
    """Mức trung bình (dB) của dải quanh tần số f trong [t0, t1]."""
    r = subprocess.run(["ffmpeg", "-v", "info", "-ss", str(t0), "-t", str(t1 - t0), "-i", str(p),
                        "-af", f"bandpass=f={f}:width_type=h:w=60,volumedetect", "-f", "null", "-"],
                       capture_output=True, text=True)
    return float(re.search(r"mean_volume: (-?[\d.]+) dB", r.stderr).group(1))


def test_tron_keeps_voice_duration(tmp_path):
    voice, music = _tone(tmp_path / "v.mp3", 1000, 6, 0.1), _tone(tmp_path / "m.mp3", 440, 6, 0.5)
    out = tron_am.tron(voice, music, tmp_path / "o.mp3", vao=0.2, ra=0.2)
    assert out == tmp_path / "o.mp3" and abs(_dur(out) - _dur(voice)) <= 0.06


def test_tron_ducks_music_under_voice(tmp_path):
    voice = _tone(tmp_path / "v.mp3", 1000, 8, 0.1, gap=(3, 5))  # có tiếng 0–3 s và 5–8 s, lặng 3–5 s
    music = _tone(tmp_path / "m.mp3", 440, 8, 0.5)
    out = tron_am.tron(voice, music, tmp_path / "o.mp3", vao=0.2, ra=0.2)
    noi, lang = _level(out, 440, 1.0, 2.5), _level(out, 440, 4.0, 4.8)
    assert lang - noi >= 6  # nhạc to hơn ≥ 6 dB trong chỗ lặng so với lúc có giọng


def test_tron_trims_long_music_and_loops_short(tmp_path):
    voice = _tone(tmp_path / "v.mp3", 1000, 6, 0.1)
    for secs in (30, 2):
        out = tron_am.tron(voice, _tone(tmp_path / f"m{secs}.mp3", 440, secs, 0.5), tmp_path / f"o{secs}.mp3",
                           vao=0.2, ra=0.2)
        assert abs(_dur(out) - 6) <= 0.06, secs
    assert _level(tmp_path / "o2.mp3", 440, 4.5, 5.5) > -60  # nhạc ngắn được lặp, cuối bài vẫn còn nhạc
