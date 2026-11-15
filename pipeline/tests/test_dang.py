import csv
import json

import pytest

from tttc import dang, dung
from tttc import trang_thai as tt

GOI = {
    "phuong_an": [
        {"tieu_de": "Phương án một", "chu_thumb": ["A"], "file_thumb": "thumbnails/1.png"},
        {"tieu_de": "ChatGPT, Gemini, Claude: 0đ hay 522.500đ mỗi tháng?", "chu_thumb": ["B"],
         "file_thumb": "thumbnails/2.png"},
    ],
    "mo_ta": "Mô tả video.\n\n00:00 Mở đầu",
    "tags": ["chatgpt plus giá", "gói ai"],
    "shorts": [{"file": "shorts/1.mp4", "tieu_de": "Bản free đủ chưa? #shorts", "ngay": "14/11/2099",
                "gio": "12:00"}],
}


RETRIES_SEEN = []  # num_retries của mỗi lệnh execute, để kiểm tra có thử lại khi lỗi mạng


class FakeReq:
    def __init__(self, log, name, kw, result):
        self.log, self.name, self.kw, self.result = log, name, kw, result

    def execute(self, num_retries=0):
        RETRIES_SEEN.append(num_retries)
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

    def commentThreads(self):
        return self._res("commentThreads", {"id": "cmt123"})


@pytest.fixture
def video(tmp_path, monkeypatch):
    monkeypatch.setattr(dung, "check_av", lambda *_: [])
    monkeypatch.setattr(dang, "thoi_luong", lambda _p: 600.0)  # tệp giả "x": mặc định coi là video 10 phút
    d = tmp_path / "videos" / "2099-11-13-goi-ai"
    (d / "thumbnails").mkdir(parents=True)
    (d / "shorts").mkdir()
    for f in ["final.mp4", "shorts/1.mp4", "thumbnails/1.png", "thumbnails/2.png"]:
        (d / f).write_bytes(b"x")
    (d / "phu-de.srt").write_text("1\n00:00:00,000 --> 00:00:01,000\nA\n\n", encoding="utf-8")
    (d / "kich-ban.md").write_text("Kịch bản thử.", encoding="utf-8")
    (d / "nguon.json").write_text("[]", encoding="utf-8")
    (d / "nghe-thu.mp3").write_bytes(b"x")
    (d / "dong-goi.json").write_text(json.dumps(GOI, ensure_ascii=False), encoding="utf-8")
    tt.set_field(d, "chon", 2)
    return d


def _approve(d):
    tt.prepare_review(d, "duyet-1")
    tt.approve_review(d, "duyet-1")
    for step in ("giong", "render", "dong-goi"):
        tt.set_step(d, step, "xong")
    tt.prepare_review(d, "duyet-2")
    tt.approve_review(d, "duyet-2", 2)
    tt.approve_short(d, 0)


def test_publish_at_converts_vn_time():
    assert dang.publish_at("13/11/2026", "19:00") == "2026-11-13T12:00:00Z"
    assert dang.publish_at("01/01/2027", "05:30") == "2026-12-31T22:30:00Z"


def test_upload_refuses_without_both_approvals(video, tmp_path):
    yt = FakeYT()
    tt.set_step(video, "duyet-1", "da-duyet")
    with pytest.raises(PermissionError):
        dang.upload(video, "13/11/2099", "19:00", youtube=yt, tracker=tmp_path / "t.csv")
    with pytest.raises(PermissionError):
        dang.upload_short(video, 0, youtube=yt, tracker=tmp_path / "t.csv")
    assert yt.log == []


def test_build_body_uses_chosen_option(video):
    body = dang.build_body(video, "2099-11-13T12:00:00Z")
    assert body["snippet"]["title"] == GOI["phuong_an"][1]["tieu_de"]
    assert body["snippet"]["defaultLanguage"] == "vi" and body["snippet"]["categoryId"] == "28"
    st = body["status"]
    assert st["privacyStatus"] == "private" and st["publishAt"] == "2099-11-13T12:00:00Z"
    assert st["containsSyntheticMedia"] is True and st["selfDeclaredMadeForKids"] is False


def test_build_body_requires_choice(video):
    tt.set_field(video, "chon", None)
    with pytest.raises(ValueError):
        dang.build_body(video, "2099-11-13T12:00:00Z")


def test_build_body_title_max_100_chars(video):
    goi = dict(GOI, phuong_an=[{"tieu_de": "x" * 101, "chu_thumb": [], "file_thumb": "thumbnails/1.png"}])
    (video / "dong-goi.json").write_text(json.dumps(goi), encoding="utf-8")
    tt.set_field(video, "chon", 1)
    with pytest.raises(ValueError):
        dang.build_body(video, "2099-11-13T12:00:00Z")


def test_upload_calls_api_and_appends_tracker_row(video, tmp_path):
    _approve(video)
    yt, tracker = FakeYT(), tmp_path / "theo-doi.csv"
    vid = dang.upload(video, "13/11/2099", "19:00", youtube=yt, tracker=tracker, playlist_id="PL1")
    assert vid == "vid123"
    assert [n for n, _ in yt.log] == ["videos.insert", "thumbnails.set", "captions.insert",
                                      "playlistItems.insert"]
    assert yt.log[1][1]["videoId"] == "vid123"
    assert yt.log[2][1]["body"]["snippet"]["language"] == "vi"
    rows = list(csv.DictReader(tracker.open(encoding="utf-8")))
    assert rows[0]["tieu_de"] == GOI["phuong_an"][1]["tieu_de"]
    assert rows[0]["gio_dang"] == "13/11/2099 19:00" and rows[0]["link"].endswith("vid123")
    assert tt.load(video)["steps"]["dang"]["status"] == "xong"


def test_upload_short_uses_its_own_schedule(video, tmp_path):
    _approve(video)
    yt = FakeYT()
    dang.upload_short(video, 0, youtube=yt, tracker=tmp_path / "t.csv")
    body = yt.log[0][1]["body"]
    assert body["snippet"]["title"].endswith("#shorts")
    assert body["status"]["publishAt"] == "2099-11-14T05:00:00Z"


@pytest.mark.parametrize("change", ["file", "gio", "none"])
def test_upload_short_needs_its_own_approval(video, tmp_path, change):
    _approve(video)
    if change == "none":
        tt.set_field(video, "short_duyet", {})
    elif change == "file":
        (video / "shorts" / "1.mp4").write_bytes(b"dung lai")
    else:
        goi = json.loads((video / "dong-goi.json").read_text(encoding="utf-8"))
        goi["shorts"][0]["gio"] = "13:00"
        (video / "dong-goi.json").write_text(json.dumps(goi, ensure_ascii=False), encoding="utf-8")
    yt = FakeYT()
    with pytest.raises(PermissionError, match="Short"):
        dang.upload_short(video, 0, youtube=yt, tracker=tmp_path / "t.csv")
    assert yt.log == []


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
        dang.upload(video, "13/11/2099", "19:00", youtube=yt, tracker=tmp_path / "t.csv", playlist_id="")
    assert dang.upload(video, "13/11/2099", "19:00", youtube=yt, tracker=tmp_path / "t.csv", playlist_id="") == "vid123"
    assert [n for n, _ in yt.log].count("videos.insert") == 1
    assert dang.upload(video, "13/11/2099", "19:00", youtube=yt, tracker=tmp_path / "t.csv", playlist_id="") == "vid123"
    assert [n for n, _ in yt.log].count("videos.insert") == 1


def test_upload_short_twice_uploads_once(video, tmp_path):
    _approve(video)
    yt = FakeYT()
    dang.upload_short(video, 0, youtube=yt, tracker=tmp_path / "t.csv")
    dang.upload_short(video, 0, youtube=yt, tracker=tmp_path / "t.csv")
    assert [n for n, _ in yt.log].count("videos.insert") == 1
    assert len(list(csv.DictReader((tmp_path / "t.csv").open(encoding="utf-8")))) == 1


def test_short_retry_restores_tracker_after_write_failure(video, tmp_path, monkeypatch):
    _approve(video)
    yt, tracker = FakeYT(), tmp_path / "t.csv"
    with monkeypatch.context() as m:
        def fail(*args):
            raise OSError("tracker unavailable")

        m.setattr(dang, "_track", fail)
        with pytest.raises(OSError):
            dang.upload_short(video, 0, youtube=yt, tracker=tracker)
    assert dang.upload_short(video, 0, youtube=yt, tracker=tracker) == "vid123"
    assert [n for n, _ in yt.log].count("videos.insert") == 1
    assert "vid123" in tracker.read_text()


def test_unknown_insert_outcome_requires_studio_reconciliation(video, tmp_path, monkeypatch):
    _approve(video)
    yt = FakeYT()
    tracker = tmp_path / "t.csv"
    with monkeypatch.context() as m:
        def lose_response(*args, **kwargs):
            raise OSError("response lost")

        m.setattr(FakeReq, "execute", lose_response)
        with pytest.raises(OSError, match="response lost"):
            dang.upload_short(video, 0, youtube=yt, tracker=tracker)
    with pytest.raises(RuntimeError, match="Đối chiếu"):
        dang.upload_short(video, 0, youtube=yt, tracker=tracker)
    assert not yt.log


@pytest.mark.parametrize("file", ["final.mp4", "kich-ban.md", "nguon.json", "phu-de.srt", "thumbnails/2.png"])
def test_upload_rejects_changed_approved_asset(video, tmp_path, file):
    _approve(video)
    (video / file).write_bytes(b"changed")
    yt = FakeYT()
    with pytest.raises(PermissionError):
        dang.upload(video, "13/11/2099", "19:00", youtube=yt, tracker=tmp_path / "t.csv")
    assert yt.log == []


def test_approval_rejects_changed_pending_preview(video):
    tt.prepare_review(video, "duyet-1")
    (video / "nghe-thu.mp3").write_bytes(b"changed")
    with pytest.raises(ValueError, match="đã thay đổi"):
        tt.approve_review(video, "duyet-1")


def test_past_publish_time_refused(video):
    with pytest.raises(ValueError, match="đã qua"):
        dang.build_body(video, "2020-01-01T00:00:00Z")


class FlakyPlaylistYT(FakeYT):
    def __init__(self):
        super().__init__()
        self.fail = True

    def playlistItems(self):
        if self.fail:
            self.fail = False
            raise RuntimeError("quotaExceeded")
        return super().playlistItems()


def test_upload_retry_does_not_duplicate_caption(video, tmp_path):
    _approve(video)
    yt = FlakyPlaylistYT()
    with pytest.raises(RuntimeError):
        dang.upload(video, "13/11/2099", "19:00", youtube=yt, tracker=tmp_path / "t.csv", playlist_id="PL1")
    dang.upload(video, "13/11/2099", "19:00", youtube=yt, tracker=tmp_path / "t.csv", playlist_id="PL1")
    assert [n for n, _ in yt.log].count("captions.insert") == 1
    assert [n for n, _ in yt.log].count("playlistItems.insert") == 1


def test_upload_retries_transient_errors(video, tmp_path):
    _approve(video)
    RETRIES_SEEN.clear()
    dang.upload(video, "13/11/2099", "19:00", youtube=FakeYT(), tracker=tmp_path / "t.csv", playlist_id="PL1")
    assert RETRIES_SEEN and all(n == dang.RETRIES and n >= 1 for n in RETRIES_SEEN)


def test_track_migrates_old_csv_and_keeps_old_rows(tmp_path):
    import csv
    t = tmp_path / "theo-doi.csv"
    t.write_text("ngay,tieu_de,gio_dang,link,view_24h,view_7d,ctr,giu_chan_30s\n"
                 "09/11/2026,Cũ,09/11/2026 20:45,https://youtu.be/x,,,,\n", encoding="utf-8")
    dang._track(t, "Mới", "10/11/2026 15:30", "vid")
    rows = list(csv.DictReader(t.open(encoding="utf-8")))
    assert list(rows[0]) == dang.FIELDS and len(dang.FIELDS) == 14  # + o_lai_short, khuon_short (15/11)
    assert [r["tieu_de"] for r in rows] == ["Cũ", "Mới"] and rows[1]["chenh_gio"] == "" and rows[1]["link"].endswith("vid")


def test_rejected_insert_clears_pending_flag_so_retry_works(video, tmp_path, monkeypatch):
    from googleapiclient.errors import HttpError
    from httplib2 import Response

    _approve(video)
    yt, tracker = FakeYT(), tmp_path / "t.csv"
    with monkeypatch.context() as m:
        def quota(*args, **kwargs):
            raise HttpError(Response({"status": 403}), b'{"error": {"errors": [{"reason": "quotaExceeded"}]}}')

        m.setattr(FakeReq, "execute", quota)
        with pytest.raises(HttpError):
            dang.upload_short(video, 0, youtube=yt, tracker=tracker)
    assert tt.load(video).get("upload_dang_cho_id") is None
    assert dang.upload_short(video, 0, youtube=yt, tracker=tracker) == "vid123"


def test_gan_hashtag_formats_long_short_and_avoids_duplicates(video, tmp_path):
    long_desc = dang.gan_hashtag("Mô tả video.", ["điện thoại cũ", "giá iphone", "apple"], is_short=False)
    tail_long = long_desc.splitlines()[-1].split()
    assert tail_long == ["#NhipCongNghe", "#DienThoaiCu", "#GiaIphone"]

    short_desc = dang.gan_hashtag("Mô tả short.", ["điện thoại cũ", "giá iphone", "apple"], is_short=True)
    tail_short = short_desc.splitlines()[-1].split()
    assert tail_short == ["#shorts", "#NhipCongNghe", "#DienThoaiCu", "#GiaIphone"]

    already = "Mô tả đã có #AI sẵn."
    assert dang.gan_hashtag(already, ["apple", "google"], is_short=False) == already
    already_short = "Mô tả #shorts sẵn."
    assert dang.gan_hashtag(already_short, ["apple"], is_short=True) == already_short

    body = dang.build_body(video, "2099-11-13T12:00:00Z")
    assert "#NhipCongNghe #ChatgptPlusGia #GoiAi" in body["snippet"]["description"]

    _approve(video)
    yt = FakeYT()
    dang.upload_short(video, 0, youtube=yt, tracker=tmp_path / "t.csv")
    assert "#shorts #NhipCongNghe #ChatgptPlusGia #GoiAi" in yt.log[0][1]["body"]["snippet"]["description"]


def test_binh_luan_ghim_calls_comment_threads_insert():
    yt = FakeYT()
    RETRIES_SEEN.clear()
    cid = dang.binh_luan_ghim(yt, "vid123", "Bạn đoán giá bao nhiêu?")
    assert cid == "cmt123"
    assert yt.log == [
        (
            "commentThreads.insert",
            {
                "part": "snippet",
                "body": {
                    "snippet": {
                        "videoId": "vid123",
                        "topLevelComment": {"snippet": {"textOriginal": "Bạn đoán giá bao nhiêu?"}},
                    }
                },
            },
        )
    ]
    assert RETRIES_SEEN == [dang.RETRIES]


def test_thumb_media_validates_size_and_mime(tmp_path):
    jpg = tmp_path / "thumb.jpg"
    jpg.write_bytes(b"jpgdata")
    assert dang._thumb_media(jpg).mimetype() == "image/jpeg"

    big = tmp_path / "big.png"
    big.write_bytes(b"x" * (dang.MAX_THUMB_BYTES + 1))
    with pytest.raises(ValueError, match="2MB"):
        dang._thumb_media(big)


def test_lock_does_not_spin_on_non_lock_oserror(tmp_path, monkeypatch):
    import errno
    import sys
    import types

    calls = []
    fake_msvcrt = types.SimpleNamespace(
        LK_LOCK=1,
        LK_UNLCK=0,
        locking=lambda fd, mode, size: calls.append(mode) or (_ for _ in ()).throw(OSError(errno.EBADF, "bad fd")),
    )
    monkeypatch.setattr(dang.os, "name", "nt")
    monkeypatch.setitem(sys.modules, "msvcrt", fake_msvcrt)
    with pytest.raises(OSError):
        with dang._lock(tmp_path / ".dang.lock"):
            pass
    assert len(calls) == 1


def test_doi_bao_bi_khong_lam_short_mat_duyet(video, tmp_path):
    from unittest.mock import MagicMock
    from tttc import giam_sat
    _approve(video)
    tracker = tmp_path / "t.csv"
    dang.upload(video, "13/11/2099", "15:30", youtube=FakeYT(), tracker=tracker)
    yt = MagicMock()
    yt.videos.return_value.list.return_value.execute.return_value = {"items": [{"snippet": {"title": "cũ"}}]}
    giam_sat.doi_bao_bi(video, 1, youtube=yt, tracker=tracker)  # CTR thấp: xoay sang phương án 1
    assert dang.upload_short(video, 0, youtube=FakeYT(), tracker=tracker) == "vid123"


def test_tieu_de_co_dau_nho_lon_bi_tu_choi():
    with pytest.raises(ValueError):
        dang._check_text("Giá <10 triệu", "", [])


def test_upload_tu_choi_video_dai_duoi_7_phut(video, tmp_path, monkeypatch):
    _approve(video)
    monkeypatch.setattr(dang, "thoi_luong", lambda _p: 135.0)
    yt = FakeYT()
    with pytest.raises(ValueError, match=r"2:15.*Shorts"):
        dang.upload(video, "13/11/2099", "19:00", youtube=yt, tracker=tmp_path / "t.csv")
    assert yt.log == [] and tt.load(video)["steps"]["dang"]["status"] != "xong"


def test_upload_tu_choi_khi_khong_do_duoc_thoi_luong(video, tmp_path, monkeypatch):
    _approve(video)
    monkeypatch.setattr(dang, "thoi_luong", lambda _p: None)
    with pytest.raises(ValueError, match="(?i)không đo được"):
        dang.upload(video, "13/11/2099", "19:00", youtube=FakeYT(), tracker=tmp_path / "t.csv")


def test_upload_ngan_duoc_qua_khi_co_ly_do_va_ghi_vao_trang_thai(video, tmp_path, monkeypatch):
    _approve(video)
    monkeypatch.setattr(dang, "thoi_luong", lambda _p: 347.0)
    with pytest.raises(ValueError, match="lý do"):
        dang.upload(video, "13/11/2099", "19:00", youtube=FakeYT(), tracker=tmp_path / "t.csv", cho_phep_ngan="  ")
    vid = dang.upload(video, "13/11/2099", "19:00", youtube=FakeYT(), tracker=tmp_path / "t.csv",
                      cho_phep_ngan="tin nóng cần ra trong ngày")
    assert vid == "vid123"
    ghi = tt.load(video)["cho_phep_ngan"]
    assert ghi["ly_do"] == "tin nóng cần ra trong ngày" and ghi["giay"] == 347.0


def test_thoi_luong_doc_bang_ffprobe(tmp_path):
    import subprocess
    mp4 = tmp_path / "v.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=blue:s=64x36:d=2",
                    "-pix_fmt", "yuv420p", str(mp4)], check=True)
    assert abs(dang.thoi_luong(mp4) - 2.0) < 0.1
    (tmp_path / "hong.mp4").write_bytes(b"x")
    assert dang.thoi_luong(tmp_path / "hong.mp4") is None and dang.thoi_luong(tmp_path / "khong-co.mp4") is None


def _short_moi(video, **them):
    goi = json.loads((video / "dong-goi.json").read_text(encoding="utf-8"))
    goi["shorts"][0].update(them)
    (video / "dong-goi.json").write_text(json.dumps(goi, ensure_ascii=False), encoding="utf-8")


def _dong_so(tracker):
    import csv
    return list(csv.DictReader(tracker.open(encoding="utf-8", newline="")))[-1]


def test_upload_short_dung_mo_ta_rieng(video, tmp_path):
    _short_moi(video, khuon="doc", mo_ta="Mô tả riêng của Short.")
    _approve(video)
    tt.set_field(video, "video_id", "dai999")
    yt = FakeYT()
    dang.upload_short(video, 0, youtube=yt, tracker=tmp_path / "t.csv")
    desc = yt.log[0][1]["body"]["snippet"]["description"]
    assert "Mô tả riêng của Short." in desc and "Mô tả video." not in desc and "youtu.be/dai999" in desc


def test_upload_short_cu_khong_co_khuon_ghi_cu(video, tmp_path):
    _approve(video)
    yt = FakeYT()
    dang.upload_short(video, 0, youtube=yt, tracker=tmp_path / "t.csv")
    assert "Mô tả video." in yt.log[0][1]["body"]["snippet"]["description"]
    assert _dong_so(tmp_path / "t.csv")["khuon_short"] == "cu"


def test_upload_short_doc_ghi_khuon_doc(video, tmp_path):
    _short_moi(video, khuon="doc")
    _approve(video)
    dang.upload_short(video, 0, youtube=FakeYT(), tracker=tmp_path / "t.csv")
    assert _dong_so(tmp_path / "t.csv")["khuon_short"] == "doc"


def test_doi_mo_ta_short_sau_khi_duyet_thi_phai_duyet_lai(video):
    _short_moi(video, mo_ta="Bản đã duyệt.")
    tt.approve_short(video, 0)
    assert tt.short_current(video, 0)
    _short_moi(video, mo_ta="Bản sửa sau khi duyệt.")
    assert not tt.short_current(video, 0)
