import base64
import json
import subprocess
import unicodedata

import pytest

from tttc import tts

CFG = {"voice_id": "v1", "model_id": "eleven_multilingual_v2", "speed": 1.0}

SCRIPT = """#### Beat 1: Mở đầu
* **[TRÊN MÀN HÌNH]:** Bảng giá *0 đ | 132.000 đ* [#p1]
* **Lời đọc:**
  Xin chào các bạn. [#p1]
  Hôm nay mình so **ba** gói.

#### Beat 2: Giá
* **[TRÊN MÀN HÌNH]:** Thẻ chữ
* **Lời đọc:** Gói Plus giá năm trăm nghìn. [#p2]
"""


@pytest.fixture(scope="module")
def silent_mp3(tmp_path_factory):
    p = tmp_path_factory.mktemp("a") / "s.mp3"
    subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
                    "-t", "1", "-c:a", "libmp3lame", "-b:a", "64k", str(p)], check=True)
    return base64.b64encode(p.read_bytes()).decode()


class Resp:
    def __init__(self, status, body=None):
        self.status_code, self._body = status, body or {}

    def json(self):
        return self._body

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


def _alignment(text):
    chars = list(text)
    return {"characters": chars,
            "character_start_times_seconds": [i * 0.05 for i in range(len(chars))],
            "character_end_times_seconds": [(i + 1) * 0.05 for i in range(len(chars))]}


def _video(tmp_path, script=SCRIPT):
    (tmp_path / "kich-ban.md").write_text(script, encoding="utf-8")
    return tmp_path


def test_spoken_paragraphs_strips_markers():
    assert tts.spoken_paragraphs(SCRIPT) == [
        "Xin chào các bạn.", "Hôm nay mình so ba gói.", "Gói Plus giá năm trăm nghìn."]


def test_spoken_paragraphs_nfc():
    paras = tts.spoken_paragraphs(unicodedata.normalize("NFD", SCRIPT))
    assert paras[0] == unicodedata.normalize("NFC", "Xin chào các bạn.")


def test_words_from_alignment_offsets():
    words = tts.words_from_alignment(_alignment("Xin chào"), offset=10.0)
    assert [w["w"] for w in words] == ["Xin", "chào"]
    assert words[0]["start"] == pytest.approx(10.0)
    assert words[1]["end"] == pytest.approx(10.4)


def test_words_from_alignment_nfd():
    words = tts.words_from_alignment(_alignment(unicodedata.normalize("NFD", "giá rẻ")), 0)
    assert [w["w"] for w in words] == ["giá", "rẻ"]


def test_tts_skips_done_paragraphs(tmp_path, silent_mp3, monkeypatch):
    d = _video(tmp_path)
    (d / "giong").mkdir()
    (d / "giong" / "doan-000.mp3").write_bytes(base64.b64decode(silent_mp3))
    (d / "giong" / "doan-000.json").write_text(json.dumps(_alignment("Xin chào các bạn.")))
    calls = []

    def post(url, **kw):
        calls.append(kw["json"]["text"])
        return Resp(200, {"audio_base64": silent_mp3, "alignment": _alignment(kw["json"]["text"])})

    tts.synthesize(d, post=post, key="k", cfg=CFG)
    assert "Xin chào các bạn." not in calls and len(calls) == 2


def test_tts_retries_only_failed_paragraph(tmp_path, silent_mp3, monkeypatch):
    monkeypatch.setattr(tts, "_sleep", lambda s: None)
    d = _video(tmp_path)
    calls, failed = [], set()

    def post(url, **kw):
        t = kw["json"]["text"]
        calls.append(t)
        if t.startswith("Hôm nay") and t not in failed:
            failed.add(t)
            return Resp(500)
        return Resp(200, {"audio_base64": silent_mp3, "alignment": _alignment(t)})

    tts.synthesize(d, post=post, key="k", cfg=CFG)
    assert calls.count("Xin chào các bạn.") == 1
    assert calls.count("Hôm nay mình so ba gói.") == 2


def test_tts_gives_up_after_3_attempts(tmp_path, monkeypatch):
    monkeypatch.setattr(tts, "_sleep", lambda s: None)
    with pytest.raises(RuntimeError):
        tts.synthesize(_video(tmp_path), post=lambda url, **kw: Resp(503), key="k", cfg=CFG)


def test_timing_duration_matches_audio(tmp_path, silent_mp3):
    d = _video(tmp_path, "* **Lời đọc:**\n  Một.\n  Hai.\n")

    def post(url, **kw):
        return Resp(200, {"audio_base64": silent_mp3, "alignment": _alignment(kw["json"]["text"])})

    tts.synthesize(d, post=post, key="k", cfg=CFG)
    timing = json.loads((d / "giong-timing.json").read_text())
    assert timing["duration"] == pytest.approx(2.0, abs=0.1)
    assert timing["paragraphs"][1]["start"] == pytest.approx(1.0, abs=0.06)
    assert timing["words"][1]["w"] == "Hai." and timing["words"][1]["start"] >= 1.0
    assert (d / "giong.mp3").exists()
