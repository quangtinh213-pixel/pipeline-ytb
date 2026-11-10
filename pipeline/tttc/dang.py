"""Đăng YouTube: riêng tư + hẹn giờ, chỉ khi đã qua cả 2 điểm duyệt."""
import csv
import fcntl
import json
import os
import sys
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from tttc import theo_doi
from tttc import trang_thai as tt

ROOT = Path(__file__).resolve().parents[2]
TRACKER = ROOT / "theo-doi.csv"
CONFIG = ROOT / "pipeline" / "config.json"
FIELDS = ["ngay", "tieu_de", "gio_dang", "link", "view_24h", "view_7d", "ctr", "giu_chan_30s"] + theo_doi.EXTRA
SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.force-ssl"]
KR = "tui-tien-cong-nghe"
RETRIES = 3  # tự thử lại khi lỗi mạng/5xx tạm thời, nhất là khi tải video lớn


def publish_at(date_vn: str, time_vn: str) -> str:
    local = datetime.strptime(f"{date_vn} {time_vn}", "%d/%m/%Y %H:%M").replace(tzinfo=ZoneInfo("Asia/Ho_Chi_Minh"))
    return local.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _goi(video_dir: Path) -> dict:
    return json.loads((video_dir / "dong-goi.json").read_text(encoding="utf-8"))


def _check_text(title: str, desc: str, tags: list[str]) -> None:
    if not title or len(title) > 100:
        raise ValueError(f"Tiêu đề phải 1–100 ký tự (đang {len(title)})")
    if len(desc.encode("utf-8")) > 5000 or "<" in desc or ">" in desc:
        raise ValueError("Mô tả quá 5000 byte hoặc có ký tự < > (YouTube từ chối)")
    if sum(len(t) + 2 for t in tags) > 500:
        raise ValueError("Tổng tags quá 500 ký tự")


def _body(title: str, desc: str, tags: list[str], when: str) -> dict:
    _check_text(title, desc, tags)
    if datetime.strptime(when, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc) <= datetime.now(timezone.utc) + timedelta(minutes=15):
        raise ValueError(f"Giờ đăng {when} (UTC) đã qua hoặc quá gần, YouTube không hẹn giờ được: chọn giờ khác")
    return {"snippet": {"title": title, "description": desc, "tags": tags, "categoryId": "28",
                        "defaultLanguage": "vi", "defaultAudioLanguage": "vi"},
            "status": {"privacyStatus": "private", "publishAt": when, "selfDeclaredMadeForKids": False,
                       "containsSyntheticMedia": True}}


def _chosen(video_dir: Path) -> dict:
    chon = tt.load(video_dir).get("chon")
    opts = _goi(video_dir)["phuong_an"]
    if not isinstance(chon, int) or not 1 <= chon <= len(opts):
        raise ValueError("Chưa chọn phương án tiêu đề/thumbnail ở điểm duyệt 2 (trường 'chon')")
    return opts[chon - 1]


def build_body(video_dir, when: str) -> dict:
    d = Path(video_dir)
    goi = _goi(d)
    return _body(_chosen(d)["tieu_de"], goi["mo_ta"], goi.get("tags", []), when)


def _guard(video_dir: Path) -> None:
    if not tt.review_current(video_dir, "duyet-2"):
        raise PermissionError("Thiếu biên nhận duyệt hoặc tệp đã thay đổi, cần duyệt lại trước khi upload")


def _media(path: Path, mime: str):
    from googleapiclient.http import MediaFileUpload
    return MediaFileUpload(str(path), mimetype=mime, resumable=mime.startswith("video"))


def _insert(d: Path, yt, body: dict, path: Path, key: str) -> str:
    if tt.load(d).get("upload_dang_cho_id"):
        raise RuntimeError("Lần tải trước chưa xác nhận được ID. Đối chiếu YouTube Studio trước khi thử lại.")
    request = yt.videos().insert(part="snippet,status", body=body, media_body=_media(path, "video/mp4"))
    tt.set_field(d, "upload_dang_cho_id", key)
    return request.execute(num_retries=RETRIES)["id"]


@contextmanager
def _lock(path: Path):
    with path.open("a") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        yield


def _track(tracker: Path, title: str, when_vn: str, vid: str) -> None:
    link = f"https://youtu.be/{vid}"
    with _lock(tracker.with_name(f".{tracker.name}.lock")):
        fields, rows = FIELDS, []
        if tracker.exists():
            with tracker.open(encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                fields = list(dict.fromkeys([*(reader.fieldnames or []), *FIELDS]))
                rows = list(reader)
        if any(r["link"] == link for r in rows):
            return
        rows.append({"ngay": when_vn.split()[0], "tieu_de": title, "gio_dang": when_vn, "link": link})
        tmp = tracker.with_name(f".{tracker.name}.tmp")
        with tmp.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)
        os.replace(tmp, tracker)


def upload(video_dir, date_vn: str, time_vn: str, youtube=None, tracker: Path = TRACKER,
           playlist_id: str | None = None) -> str:
    d = Path(video_dir)
    with _lock(d / ".dang.lock"):
        return _upload(d, date_vn, time_vn, youtube, Path(tracker), playlist_id)


def _upload(d: Path, date_vn: str, time_vn: str, youtube, tracker: Path, playlist_id: str | None) -> str:
    state = tt.load(d)
    if state["steps"]["dang"]["status"] == "xong":
        return state["video_id"]
    _guard(d)
    vid = state.get("video_id")
    when = f"{date_vn} {time_vn}"
    if vid and state.get("lich_dang") != when:
        raise ValueError("Video đã có ID với lịch khác hoặc thiếu lịch đã ghi, đối chiếu YouTube Studio trước")
    title = _chosen(d)["tieu_de"]
    body = build_body(d, publish_at(date_vn, time_vn)) if not vid else None
    yt = youtube or client()
    if playlist_id is None:
        playlist_id = json.loads(CONFIG.read_text(encoding="utf-8")).get("playlist_id") or None
    if not vid:  # lưu id ngay sau khi tạo: bước sau hỏng thì chạy lại không tạo video thứ hai
        vid = _insert(d, yt, body, d / "final.mp4", "video")
        tt.set_fields(d, video_id=vid, lich_dang=when, upload_dang_cho_id=None)
    yt.thumbnails().set(videoId=vid, media_body=_media(d / _chosen(d)["file_thumb"], "image/png")).execute(num_retries=RETRIES)
    if not state.get("phu_de_ok"):  # chạy lại sau lỗi bước playlist không thêm bản phụ đề thứ hai
        yt.captions().insert(part="snippet", body={"snippet": {"videoId": vid, "language": "vi", "name": "Tiếng Việt"}},
                             media_body=_media(d / "phu-de.srt", "application/octet-stream")).execute(num_retries=RETRIES)
        tt.set_field(d, "phu_de_ok", True)
    if playlist_id and state.get("playlist_ok") != playlist_id:
        yt.playlistItems().insert(part="snippet", body={"snippet": {
            "playlistId": playlist_id, "resourceId": {"kind": "youtube#video", "videoId": vid}}}).execute(num_retries=RETRIES)
        tt.set_field(d, "playlist_ok", playlist_id)
    _track(tracker, title, when, vid)
    tt.set_step(d, "dang", "xong", f"https://youtu.be/{vid}")
    return vid


def upload_short(video_dir, index: int, youtube=None, tracker: Path = TRACKER) -> str:
    d = Path(video_dir)
    with _lock(d / ".dang.lock"):
        return _upload_short(d, index, youtube, Path(tracker))


def _upload_short(d: Path, index: int, youtube, tracker: Path) -> str:
    state = tt.load(d)
    done, schedules = state.get("short_ids") or {}, state.get("short_lich") or {}
    key = str(index)
    goi = _goi(d)
    if not 0 <= index < len(goi.get("shorts", [])):
        raise ValueError("Chỉ số Short không tồn tại")
    s = goi["shorts"][index]
    when = f"{s['ngay']} {s['gio']}"
    if key in done:
        saved = schedules.get(key, {"tieu_de": s["tieu_de"], "gio": when})
        _track(tracker, saved["tieu_de"], saved["gio"], done[key])
        return done[key]
    _guard(d)
    body = _body(s["tieu_de"], goi["mo_ta"], goi.get("tags", []), publish_at(s["ngay"], s["gio"]))
    yt = youtube or client()
    vid = _insert(d, yt, body, d / s["file"], f"short:{key}")
    done[key] = vid
    schedules[key] = {"tieu_de": s["tieu_de"], "gio": when}
    tt.set_fields(d, short_ids=done, short_lich=schedules, upload_dang_cho_id=None)
    _track(tracker, s["tieu_de"], when, vid)
    return vid


def login(client_secret_json: str) -> None:
    """Một lần: mở trình duyệt đăng nhập tài khoản kênh, lưu token vào Keychain."""
    import keyring
    from google_auth_oauthlib.flow import InstalledAppFlow
    secret = Path(client_secret_json).read_text(encoding="utf-8")
    flow = InstalledAppFlow.from_client_config(json.loads(secret), SCOPES)
    creds = flow.run_local_server(port=0)
    keyring.set_password(KR, "youtube-client", secret)
    keyring.set_password(KR, "youtube-token", creds.to_json())


def client():
    import keyring
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    tok = keyring.get_password(KR, "youtube-token")
    if not tok:
        raise RuntimeError("Chưa đăng nhập YouTube: chạy `uv run python -m tttc.dang login <client_secret.json>`")
    creds = Credentials.from_authorized_user_info(json.loads(tok), SCOPES)
    if not creds.valid:
        creds.refresh(Request())
        keyring.set_password(KR, "youtube-token", creds.to_json())
    return build("youtube", "v3", credentials=creds)


if __name__ == "__main__":
    if sys.argv[1] == "login":
        login(sys.argv[2])
    elif sys.argv[1] == "short":
        print(upload_short(sys.argv[2], int(sys.argv[3])))
    else:
        print(upload(sys.argv[1], sys.argv[2], sys.argv[3]))
