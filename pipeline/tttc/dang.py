"""Đăng YouTube: riêng tư + hẹn giờ, chỉ khi đã qua cả 2 điểm duyệt."""
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from tttc import trang_thai as tt

ROOT = Path(__file__).resolve().parents[2]
TRACKER = ROOT / "theo-doi.csv"
CONFIG = ROOT / "pipeline" / "config.json"
FIELDS = ["ngay", "tieu_de", "gio_dang", "link", "view_24h", "view_7d", "ctr", "giu_chan_30s"]
SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.force-ssl"]
KR = "tui-tien-cong-nghe"


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
    if not tt.is_approved(video_dir):
        raise PermissionError("Video chưa qua đủ 2 điểm duyệt, không upload")


def _media(path: Path, mime: str):
    from googleapiclient.http import MediaFileUpload
    return MediaFileUpload(str(path), mimetype=mime, resumable=mime.startswith("video"))


def _track(tracker: Path, title: str, when_vn: str, vid: str) -> None:
    new = not tracker.exists()
    with tracker.open("a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        w.writerow({"ngay": when_vn.split()[0], "tieu_de": title, "gio_dang": when_vn,
                    "link": f"https://youtu.be/{vid}"})


def upload(video_dir, date_vn: str, time_vn: str, youtube=None, tracker: Path = TRACKER,
           playlist_id: str | None = None) -> str:
    d = Path(video_dir)
    _guard(d)
    body = build_body(d, publish_at(date_vn, time_vn))
    yt = youtube or client()
    if playlist_id is None:
        playlist_id = json.loads(CONFIG.read_text(encoding="utf-8")).get("playlist_id") or None
    vid = yt.videos().insert(part="snippet,status", body=body,
                             media_body=_media(d / "final.mp4", "video/mp4")).execute()["id"]
    yt.thumbnails().set(videoId=vid, media_body=_media(d / _chosen(d)["file_thumb"], "image/png")).execute()
    yt.captions().insert(part="snippet", body={"snippet": {"videoId": vid, "language": "vi", "name": "Tiếng Việt"}},
                         media_body=_media(d / "phu-de.srt", "application/octet-stream")).execute()
    if playlist_id:
        yt.playlistItems().insert(part="snippet", body={"snippet": {
            "playlistId": playlist_id, "resourceId": {"kind": "youtube#video", "videoId": vid}}}).execute()
    _track(Path(tracker), body["snippet"]["title"], f"{date_vn} {time_vn}", vid)
    tt.set_step(d, "dang", "xong", f"https://youtu.be/{vid}")
    return vid


def upload_short(video_dir, index: int, youtube=None, tracker: Path = TRACKER) -> str:
    d = Path(video_dir)
    _guard(d)
    goi = _goi(d)
    s = goi["shorts"][index]
    body = _body(s["tieu_de"], goi["mo_ta"], goi.get("tags", []), publish_at(s["ngay"], s["gio"]))
    yt = youtube or client()
    vid = yt.videos().insert(part="snippet,status", body=body,
                             media_body=_media(d / s["file"], "video/mp4")).execute()["id"]
    _track(Path(tracker), s["tieu_de"], f"{s['ngay']} {s['gio']}", vid)
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
