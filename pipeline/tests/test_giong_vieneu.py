import json
import subprocess
from pathlib import Path

import pytest

from tttc import giong_vieneu

SCRIPT = ("#### Beat 1\n**Lời đọc:**\nXin chào các bạn. Hôm nay mình so ba gói.\nGiá chưa gồm thuế.\n")
CFG = {"python": "py", "voice": "Hải Đăng", "pause_cau": 0.2, "pause_doan": 0.5, "phat_am": {}}


def _ff(args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)


def _dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True, check=True)
    return float(r.stdout)


def _fake_worker(seconds, lead=0.0, calls=None):
    """Thay cho tiến trình VieNeu: đọc jobs.json rồi tạo một tệp wav (tiếng sin, có thể kèm lặng đầu/cuối) cho mỗi job."""
    def run(cmd, **kw):
        jobs = json.loads(Path(cmd[cmd.index("--jobs") + 1]).read_text(encoding="utf-8"))
        if calls is not None:
            calls.append(jobs)
        for k, j in enumerate(jobs):
            s = seconds[k % len(seconds)]
            tone = f"sine=f=300:d={s}:r=48000"
            if lead:
                _ff(["-f", "lavfi", "-i", tone, "-af", f"adelay={int(lead * 1000)}:all=1,apad=pad_dur={lead}", j["out"]])
            else:
                _ff(["-f", "lavfi", "-i", tone, j["out"]])
        return subprocess.CompletedProcess(cmd, 0)
    return run


def _video(tmp_path, script=SCRIPT):
    (tmp_path / "kich-ban.md").write_text(script, encoding="utf-8")
    return tmp_path


def test_split_sentences_keeps_punctuation():
    assert giong_vieneu.cau("Xin chào. Hôm nay? Mình nói... xong!  ") == ["Xin chào.", "Hôm nay?", "Mình nói...", "xong!"]


def test_unit_name_changes_with_text_and_voice():
    a = giong_vieneu._ten("Xin chào.", "Hải Đăng")
    assert a == giong_vieneu._ten("Xin chào.", "Hải Đăng")
    assert a != giong_vieneu._ten("Xin chào!", "Hải Đăng") and a != giong_vieneu._ten("Xin chào.", "Thiện Minh")


def test_synthesize_builds_exact_paragraph_timing(tmp_path):
    d = _video(tmp_path)
    giong_vieneu.synthesize(d, cfg=CFG, run=_fake_worker([2.0, 3.0, 1.0]))
    t = json.loads((d / "giong-timing.json").read_text(encoding="utf-8"))
    # 3 câu: 2,0 + 0,2 | 3,0 + 0,5 | 1,0 + 0,5 (câu cuối của đoạn thì nghỉ pause_doan)
    assert t["duration"] == pytest.approx(7.2, abs=0.1) and abs(_dur(d / "giong.mp3") - 7.2) < 0.1
    w = t["words"]
    assert [x["w"] for x in w] == "Xin chào các bạn. Hôm nay mình so ba gói. Giá chưa gồm thuế.".split()
    assert w[0]["start"] == 0.0 and w[3]["end"] <= 2.0 + 1e-6          # câu 1 nằm trong [0, 2,0]
    assert w[4]["start"] == pytest.approx(2.2, abs=0.05)               # câu 2 bắt đầu sau nghỉ 0,2
    assert w[10]["start"] == pytest.approx(5.7, abs=0.05)              # câu 3 mở đoạn 2, sau câu 2 + nghỉ 0,5
    assert all(a["start"] <= b["start"] for a, b in zip(w, w[1:]))
    assert t["paragraphs"][0]["start"] == 0 and t["paragraphs"][-1]["end"] == pytest.approx(t["duration"], abs=0.01)


def test_synthesize_skips_units_already_made(tmp_path):
    d, calls = _video(tmp_path), []
    run = _fake_worker([1.0], calls=calls)
    giong_vieneu.synthesize(d, cfg=CFG, run=run)
    giong_vieneu.synthesize(d, cfg=CFG, run=run)
    assert len(calls) == 1 and len(calls[0]) == 3  # lần hai không gọi VieNeu nữa


def test_trims_silence_at_both_ends(tmp_path):
    d = _video(tmp_path, "#### B\n**Lời đọc:**\nXin chào.\n")
    giong_vieneu.synthesize(d, cfg=CFG, run=_fake_worker([1.0], lead=0.5))
    t = json.loads((d / "giong-timing.json").read_text(encoding="utf-8"))
    assert t["duration"] == pytest.approx(1.0 + 0.5, abs=0.1)  # 1 s tiếng thật + nghỉ 0,5; lặng đầu/cuối 0,5 s bị cắt


def test_pronunciation_map_applies_to_tts_text_only(tmp_path):
    d, calls = _video(tmp_path, "#### B\n**Lời đọc:**\nChatGPT giá rẻ.\n"), []
    cfg = dict(CFG, phat_am={"ChatGPT": "chát gi pi ti"})
    giong_vieneu.synthesize(d, cfg=cfg, run=_fake_worker([1.0], calls=calls))
    assert calls[0][0]["text"] == "chát gi pi ti giá rẻ." and calls[0][0]["voice"] == "Hải Đăng"
    t = json.loads((d / "giong-timing.json").read_text(encoding="utf-8"))
    assert t["words"][0]["w"] == "ChatGPT"


def test_audition_makes_one_mp3_per_voice(tmp_path):
    files = giong_vieneu.audition(tmp_path / "thu", ["Hải Đăng", "Thiện Minh"], "Xin chào các bạn.", cfg=CFG,
                                  run=_fake_worker([1.0]))
    assert [f.name for f in files] == ["Hải Đăng.mp3", "Thiện Minh.mp3"] and all(_dur(f) > 0.5 for f in files)


def test_empty_audio_for_a_sentence_is_a_clear_error_and_retried_next_time(tmp_path):
    d = _video(tmp_path, "#### B\n**Lời đọc:**\nXin chào.\n")

    def empty(cmd, **kw):
        for j in json.loads(Path(cmd[cmd.index("--jobs") + 1]).read_text(encoding="utf-8")):
            import wave
            with wave.open(j["out"], "wb") as w:
                w.setnchannels(1), w.setsampwidth(2), w.setframerate(48000)
        return subprocess.CompletedProcess(cmd, 0)
    with pytest.raises(RuntimeError, match="Xin chào"):
        giong_vieneu.synthesize(d, cfg=CFG, run=empty)
    assert not list((d / "giong-vieneu").glob("*.wav"))  # tệp rỗng bị xoá để lần sau làm lại


def test_digits_in_spoken_sentence_are_warned(tmp_path, capsys):
    d = _video(tmp_path, "#### B\n**Lời đọc:**\nGiữa 0 đồng và hơn một trăm nghìn.\n")
    giong_vieneu.synthesize(d, cfg=CFG, run=_fake_worker([1.0]))
    assert "chữ số" in capsys.readouterr().out


def test_tempo_slows_speech_down(tmp_path):
    d = _video(tmp_path, "#### B\n**Lời đọc:**\nXin chào.\n")
    giong_vieneu.synthesize(d, cfg=dict(CFG, toc_do=0.5), run=_fake_worker([1.0]))
    t = json.loads((d / "giong-timing.json").read_text(encoding="utf-8"))
    assert t["duration"] == pytest.approx(2.0 + 0.5, abs=0.15)  # 1 s tiếng chậm 0,5× → 2 s, cộng nghỉ 0,5 s
