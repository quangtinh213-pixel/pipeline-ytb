import csv
import json

import pytest

from tttc import dang
from tttc import trang_thai as tt

GOI = {
    "phuong_an": [
        {"tieu_de": "Phương án một", "chu_thumb": ["A"], "file_thumb": "thumbnails/1.png"},
        {"tieu_de": "ChatGPT, Gemini, Claude: 0đ hay 522.500đ mỗi tháng?", "chu_thumb": ["B"],
         "file_thumb": "thumbnails/2.png"},
    ],
    "mo_ta": "Mô tả video.\n\n00:00 Mở đầu",
    "tags": ["chatgpt plus giá", "gói ai"],
    "shorts": [{"file": "shorts/1.mp4", "tieu_de": "Bản free đủ chưa? #shorts", "ngay": "14/11/2026",
                "gio": "12:00"}],
}


class FakeReq:
    def __init__(self, log, name, kw, result):
        self.log, self.name, self.kw, self.result = log, name, kw, result

    def execute(self):
        self.log.append((self.name, self.kw))
        return self.result


class FakeYT:
    def __init__(self):
        self.log = []

    def _res(self, name, result):
        log = self.log

        class R:
            def insert(self, **kw):
                return FakeReq(log, name + ".insert", kw, result)

            def set(self, **kw):
                return FakeReq(log, name + ".set", kw, result)
        return R()

    def videos(self):
        return self._res("videos", {"id": "vid123"})

    def thumbnails(self):
        return self._res("thumbnails", {})

    def captions(self):
        return self._res("captions", {})

    def playlistItems(self):
        return self._res("playlistItems", {})


@pytest.fixture
def video(tmp_path):
    d = tmp_path / "videos" / "2026-11-13-goi-ai"
    (d / "thumbnails").mkdir(parents=True)
    (d / "shorts").mkdir()
    for f in ["final.mp4", "shorts/1.mp4", "thumbnails/1.png", "thumbnails/2.png"]:
        (d / f).write_bytes(b"x")
    (d / "phu-de.srt").write_text("1\n00:00:00,000 --> 00:00:01,000\nA\n\n", encoding="utf-8")
    (d / "dong-goi.json").write_text(json.dumps(GOI, ensure_ascii=False), encoding="utf-8")
    tt.set_field(d, "chon", 2)
    return d


def _approve(d):
    tt.set_step(d, "duyet-1", "da-duyet")
    tt.set_step(d, "duyet-2", "da-duyet")


def test_publish_at_converts_vn_time():
    assert dang.publish_at("13/11/2026", "19:00") == "2026-11-13T12:00:00Z"
    assert dang.publish_at("01/01/2027", "05:30") == "2026-12-31T22:30:00Z"


def test_upload_refuses_without_both_approvals(video, tmp_path):
    yt = FakeYT()
    tt.set_step(video, "duyet-1", "da-duyet")
    with pytest.raises(PermissionError):
        dang.upload(video, "13/11/2026", "19:00", youtube=yt, tracker=tmp_path / "t.csv")
    with pytest.raises(PermissionError):
        dang.upload_short(video, 0, youtube=yt, tracker=tmp_path / "t.csv")
    assert yt.log == []


def test_build_body_uses_chosen_option(video):
    body = dang.build_body(video, "2026-11-13T12:00:00Z")
    assert body["snippet"]["title"] == GOI["phuong_an"][1]["tieu_de"]
    assert body["snippet"]["defaultLanguage"] == "vi" and body["snippet"]["categoryId"] == "28"
    st = body["status"]
    assert st["privacyStatus"] == "private" and st["publishAt"] == "2026-11-13T12:00:00Z"
    assert st["containsSyntheticMedia"] is True and st["selfDeclaredMadeForKids"] is False


def test_build_body_requires_choice(video):
    tt.set_field(video, "chon", None)
    with pytest.raises(ValueError):
        dang.build_body(video, "2026-11-13T12:00:00Z")


def test_build_body_title_max_100_chars(video):
    goi = dict(GOI, phuong_an=[{"tieu_de": "x" * 101, "chu_thumb": [], "file_thumb": "thumbnails/1.png"}])
    (video / "dong-goi.json").write_text(json.dumps(goi), encoding="utf-8")
    tt.set_field(video, "chon", 1)
    with pytest.raises(ValueError):
        dang.build_body(video, "2026-11-13T12:00:00Z")


def test_upload_calls_api_and_appends_tracker_row(video, tmp_path):
    _approve(video)
    yt, tracker = FakeYT(), tmp_path / "theo-doi.csv"
    vid = dang.upload(video, "13/11/2026", "19:00", youtube=yt, tracker=tracker, playlist_id="PL1")
    assert vid == "vid123"
    assert [n for n, _ in yt.log] == ["videos.insert", "thumbnails.set", "captions.insert",
                                      "playlistItems.insert"]
    assert yt.log[1][1]["videoId"] == "vid123"
    assert yt.log[2][1]["body"]["snippet"]["language"] == "vi"
    rows = list(csv.DictReader(tracker.open(encoding="utf-8")))
    assert rows[0]["tieu_de"] == GOI["phuong_an"][1]["tieu_de"]
    assert rows[0]["gio_dang"] == "13/11/2026 19:00" and rows[0]["link"].endswith("vid123")
    assert tt.load(video)["steps"]["dang"]["status"] == "xong"


def test_upload_short_uses_its_own_schedule(video, tmp_path):
    _approve(video)
    yt = FakeYT()
    dang.upload_short(video, 0, youtube=yt, tracker=tmp_path / "t.csv")
    body = yt.log[0][1]["body"]
    assert body["snippet"]["title"].endswith("#shorts")
    assert body["status"]["publishAt"] == "2026-11-14T05:00:00Z"


class FlakyThumbYT(FakeYT):
    def __init__(self):
        super().__init__()
        self.fail = True

    def thumbnails(self):
        if self.fail:
            self.fail = False
            raise RuntimeError("403 thumbnails")
        return super().thumbnails()


def test_upload_retry_does_not_duplicate_video(video, tmp_path):
    _approve(video)
    yt = FlakyThumbYT()
    with pytest.raises(RuntimeError):
        dang.upload(video, "13/11/2026", "19:00", youtube=yt, tracker=tmp_path / "t.csv", playlist_id="")
    assert dang.upload(video, "13/11/2026", "19:00", youtube=yt, tracker=tmp_path / "t.csv", playlist_id="") == "vid123"
    assert [n for n, _ in yt.log].count("videos.insert") == 1
    assert dang.upload(video, "13/11/2026", "19:00", youtube=yt, tracker=tmp_path / "t.csv", playlist_id="") == "vid123"
    assert [n for n, _ in yt.log].count("videos.insert") == 1


def test_upload_short_twice_uploads_once(video, tmp_path):
    _approve(video)
    yt = FakeYT()
    dang.upload_short(video, 0, youtube=yt, tracker=tmp_path / "t.csv")
    dang.upload_short(video, 0, youtube=yt, tracker=tmp_path / "t.csv")
    assert [n for n, _ in yt.log].count("videos.insert") == 1
