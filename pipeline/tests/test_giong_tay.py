import json
import subprocess

import pytest

from tttc import giong_tay


def _w(text, start, end):
    return {"text": text, "start": start, "end": end}


def test_can_chinh_exact_match_ignores_case_and_punctuation():
    asr = [_w("xin", 0.0, 0.3), _w("Chào", 0.4, 0.7), _w("các", 0.8, 1.0), _w("bạn", 1.1, 1.5)]
    words, khop = giong_tay.can_chinh(["Xin", "chào,", "các", "bạn."], asr, 2.0)
    assert [(w["w"], w["start"], w["end"]) for w in words] == [("Xin", 0.0, 0.3), ("chào,", 0.4, 0.7),
                                                                ("các", 0.8, 1.0), ("bạn.", 1.1, 1.5)]
    assert khop == 1.0


def test_can_chinh_number_block_takes_asr_span():
    asr = [_w("giá", 0.0, 0.3), _w("500.000", 0.4, 1.6), _w("đồng", 1.7, 2.0)]
    words, khop = giong_tay.can_chinh("giá năm trăm nghìn đồng".split(), asr, 2.2)
    assert words[0]["start"] == 0.0 and words[4]["end"] == 2.0
    mid = words[1:4]  # "năm trăm nghìn" nằm gọn trong khoảng của "500.000", đúng thứ tự
    assert all(0.4 <= w["start"] and w["end"] <= 1.6 for w in mid)
    assert mid[0]["start"] < mid[1]["start"] < mid[2]["start"]
    assert khop == pytest.approx(2 / 5)  # chỉ "giá" và "đồng" khớp thẳng


def test_can_chinh_missing_words_are_interpolated_between_neighbours():
    asr = [_w("xin", 0.0, 0.3), _w("bạn", 1.0, 1.4)]
    words, khop = giong_tay.can_chinh(["xin", "chào", "các", "bạn"], asr, 1.5)
    assert 0.3 <= words[1]["start"] < words[2]["start"] <= words[3]["start"] == 1.0
    assert khop == 0.5


def test_can_chinh_times_are_monotonic_and_inside_duration():
    asr = [_w("a", 0.0, 0.5), _w("c", 3.0, 3.5)]
    words, _ = giong_tay.can_chinh(["a", "b", "b2", "c", "d", "e"], asr, 4.0)
    starts = [w["start"] for w in words]
    assert starts == sorted(starts) and all(w["start"] <= w["end"] <= 4.0 for w in words)


SCRIPT = "#### Beat 1: Mở đầu\n**Lời đọc:**\nXin chào các bạn. [#p1]\nHôm nay mình so ba gói.\n"


def test_build_timing_paragraph_ranges_are_contiguous():
    asr = [_w(t, i * 0.5, i * 0.5 + 0.4) for i, t in enumerate("xin chào các bạn hôm nay mình so ba gói".split())]
    timing, khop = giong_tay.build_timing(SCRIPT, asr, 5.5)
    assert timing["duration"] == 5.5 and len(timing["words"]) == 10 and khop == 1.0
    r = timing["paragraphs"]
    assert [p["i"] for p in r] == [0, 1] and r[0]["start"] == 0 and r[0]["end"] == r[1]["start"] == 2.0 and r[1]["end"] == 5.5


def test_tu_srt_interpolates_words_inside_cue():
    srt = "1\n00:00:00,000 --> 00:00:02,000\nXin chào các bạn\n\n2\n00:00:03,000 --> 00:00:04,000\nHôm nay\n"
    w = giong_tay.tu_srt(srt)
    assert [x["text"] for x in w] == ["Xin", "chào", "các", "bạn", "Hôm", "nay"]
    assert w[0]["start"] == 0.0 and w[3]["end"] <= 2.0 and w[4]["start"] == 3.0 and w[5]["end"] <= 4.0
    assert all(a["start"] < b["start"] for a, b in zip(w, w[1:]))


def _tone(path, seconds):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"sine=f=300:d={seconds}",
                    "-c:a", "libmp3lame", str(path)], check=True)
    return path


def _dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                                capture_output=True, text=True, check=True).stdout)


def _video(tmp_path):
    (tmp_path / "kich-ban.md").write_text(SCRIPT, encoding="utf-8")
    return tmp_path


def test_main_with_srt_writes_voice_and_timing(tmp_path):
    d = _video(tmp_path)
    srt = d / "g.srt"
    srt.write_text("1\n00:00:00,000 --> 00:00:02,000\nXin chào các bạn\n\n2\n00:00:02,000 --> 00:00:05,000\nHôm nay mình so ba gói\n",
                   encoding="utf-8")
    assert giong_tay.main(str(d), [str(_tone(d / "goc.mp3", 5))], srt=str(srt)) == 0
    t = json.loads((d / "giong-timing.json").read_text(encoding="utf-8"))
    assert abs(_dur(d / "giong.mp3") - 5) < 0.1 and len(t["words"]) == 10 and t["paragraphs"][1]["end"] == pytest.approx(t["duration"])


def test_main_concatenates_several_files_in_order(tmp_path):
    d = _video(tmp_path)
    a, b = _tone(d / "a.mp3", 2), _tone(d / "b.mp3", 3)
    fake = lambda audio: [_w(t, i * 0.5, i * 0.5 + 0.4) for i, t in enumerate("xin chào các bạn hôm nay mình so ba gói".split())]
    assert giong_tay.main(str(d), [str(a), str(b)], phien_am=fake) == 0
    assert abs(_dur(d / "giong.mp3") - 5) < 0.15


def test_main_rejects_audio_that_does_not_match_script(tmp_path):
    d = _video(tmp_path)
    fake = lambda audio: [_w(t, i * 0.5, i * 0.5 + 0.4) for i, t in enumerate("hoàn toàn khác nội dung kịch bản".split())]
    assert giong_tay.main(str(d), [str(_tone(d / "a.mp3", 5))], phien_am=fake) == 1
    assert not (d / "giong-timing.json").exists()


def test_phien_am_reads_transcript_json_written_by_the_cli(tmp_path):
    def fake_run(cmd, **kw):
        out = __import__("pathlib").Path(cmd[cmd.index("--dir") + 1]) / "sub"
        out.mkdir()
        (out / "transcript.json").write_text(json.dumps([{"id": "w0", "text": "xin", "start": 0.0, "end": 0.3}]), encoding="utf-8")
        return subprocess.CompletedProcess(cmd, 0)
    assert giong_tay._phien_am(tmp_path / "a.mp3", run=fake_run) == [{"text": "xin", "start": 0.0, "end": 0.3}]
