"""Đăng YouTube: riêng tư + hẹn giờ, chỉ khi đã qua cả 2 điểm duyệt."""
import csv
import errno
import json
import os
import re
import subprocess
import sys
import time
import unicodedata
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

from tttc import theo_doi
from tttc import trang_thai as tt

ROOT = Path(__file__).resolve().parents[2]
TRACKER = ROOT / "theo-doi.csv"
CONFIG = ROOT / "pipeline" / "config.json"
FIELDS = ["ngay", "tieu_de", "gio_dang", "link", "view_24h", "view_7d", "ctr", "giu_chan_30s"] + theo_doi.EXTRA
SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.force-ssl"]
ANALYTICS_SCOPES = ["https://www.googleapis.com/auth/yt-analytics.readonly", "https://www.googleapis.com/auth/youtube.readonly"]
KR = "tui-tien-cong-nghe"
RETRIES = 3  # tự thử lại khi lỗi mạng/5xx tạm thời, nhất là khi tải video lớn


def publish_at(date_vn: str, time_vn: str) -> str:
    local = datetime.strptime(f"{date_vn} {time_vn}", "%d/%m/%Y %H:%M").replace(tzinfo=tt.VN)  # VN không đổi giờ theo mùa; Windows không có sẵn dữ liệu múi giờ
    return local.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def kiem_tra_gio_vang(time_vn: str) -> list[str]:
    """Cảnh báo nếu giờ hẹn đăng video dài rơi vào vùng chết (17:00–21:00) làm mất ưu thế trước đối thủ."""
    try:
        gio = int(time_vn.split(":")[0])
        if 17 <= gio < 21:
            return [f"Cảnh báo vùng chết: Giờ đăng {time_vn} rơi vào khung 17:00–21:00 đã bị đối thủ phủ sóng. Khung chuẩn vàng là 15:00–16:00 (mặc định 15:30)."]
    except Exception:
        pass
    return []


def _goi(video_dir: Path) -> dict:
    return json.loads((video_dir / "dong-goi.json").read_text(encoding="utf-8"))


def _check_text(title: str, desc: str, tags: list[str]) -> None:
    if not title or len(title) > 100 or "<" in title or ">" in title:
        raise ValueError(f"Tiêu đề phải 1–100 ký tự, không có < > (đang {len(title)} ký tự)")
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


def _to_hashtag(tag: str) -> str:
    clean = unicodedata.normalize("NFKD", tag.replace("đ", "d").replace("Đ", "D"))
    ascii_str = "".join(ch for ch in clean if not unicodedata.combining(ch))
    words = re.findall(r"[A-Za-z0-9]+", ascii_str)
    return "#" + "".join(w[:1].upper() + w[1:] for w in words) if words else ""


def gan_hashtag(desc: str, tags: list[str], is_short: bool = False) -> str:
    """Nối 3 hashtag chuẩn (hoặc #shorts + 2–3 hashtag cho Shorts) vào cuối mô tả nếu chưa có."""
    if re.search(r"(?:^|\s)#[A-Za-zÀ-ỹ]\w*", desc):
        return desc
    hs: list[str] = ["#shorts"] if is_short else []
    hs.append("#NhipCongNghe")
    seen = {h.lower() for h in hs}
    gioi_han = 4 if is_short else 3
    for t in tags:
        h = _to_hashtag(t)
        if h and h.lower() not in seen:
            hs.append(h)
            seen.add(h.lower())
        if len(hs) >= gioi_han:
            break
    moi = f"{desc.rstrip()}\n\n{' '.join(hs)}"
    return moi if len(moi.encode("utf-8")) <= 5000 else desc


def build_body(video_dir, when: str) -> dict:
    d = Path(video_dir)
    goi = _goi(d)
    tags = goi.get("tags", [])
    mo_ta = goi["mo_ta"]
    tap_truoc = (goi.get("tap_truoc") or "").strip()
    if tap_truoc and f"youtu.be/{tap_truoc}" not in mo_ta:
        mo_ta = f"👉 Xem tập trước trong chuỗi: https://youtu.be/{tap_truoc}\n\n{mo_ta}"
    return _body(_chosen(d)["tieu_de"], gan_hashtag(mo_ta, tags, is_short=False), tags, when)


def _guard(video_dir: Path) -> None:
    if not tt.review_current(video_dir, "duyet-2"):
        raise PermissionError("Thiếu biên nhận duyệt hoặc tệp đã thay đổi, cần duyệt lại trước khi upload")


# Cổng định dạng (docs/nghien-cuu/de-xuat-phat-trien-2026-11-15.md mục 1.2): video dài 2:21 và 5:47 đăng như video dài
# thì trông như kênh tin tự động tóm tin và gần như không được thử; tin chỉ đủ vài phút thì làm Shorts.
DAI_TOI_THIEU = 420.0  # giây (7:00)


def thoi_luong(path: Path) -> float | None:
    """Thời lượng thật của tệp video (ffprobe); None nếu không có tệp hoặc không đọc được."""
    if not Path(path).is_file():
        return None
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip().splitlines()[0])
    except (IndexError, ValueError):
        return None


def mmss(giay: float) -> str:
    return f"{int(giay) // 60}:{int(giay) % 60:02d}"


def kiem_thoi_luong(d: Path, cho_phep_ngan: str | None = None) -> None:
    """Từ chối đăng dạng video dài khi final.mp4 < 7:00, trừ khi có lý do (ghi vào trang-thai.json:cho_phep_ngan)."""
    giay = thoi_luong(d / "final.mp4")
    if giay is None:
        raise ValueError("Không đo được thời lượng final.mp4 (ffprobe), kiểm tệp trước khi đăng")
    if giay >= DAI_TOI_THIEU:
        return
    if cho_phep_ngan is None:
        raise ValueError(f"Video dài {mmss(giay)} < {mmss(DAI_TOI_THIEU)}: không đăng dạng video dài, cắt thành Shorts. "
                         "Muốn đăng vẫn đăng thì chạy lại với --cho-phep-ngan \"<lý do>\"")
    if len(cho_phep_ngan.strip()) < 5:
        raise ValueError("--cho-phep-ngan cần lý do cụ thể (ít nhất 5 ký tự)")
    tt.set_field(d, "cho_phep_ngan", {"ly_do": cho_phep_ngan.strip(), "giay": giay})


MAX_THUMB_BYTES = 2 * 1024 * 1024
THUMB_MIMES = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}


def _media(path: Path, mime: str):
    from googleapiclient.http import MediaFileUpload
    return MediaFileUpload(str(path), mimetype=mime, resumable=mime.startswith("video"))


def _thumb_media(path: Path):
    size = path.stat().st_size
    if size > MAX_THUMB_BYTES:
        raise ValueError(f"Thumbnail vượt quá 2MB ({size} bytes): {path}")
    return _media(path, THUMB_MIMES.get(path.suffix.lower(), "image/png"))


def _insert(d: Path, yt, body: dict, path: Path, key: str) -> str:
    if tt.load(d).get("upload_dang_cho_id"):
        raise RuntimeError("Lần tải trước chưa xác nhận được ID. Đối chiếu YouTube Studio trước khi thử lại.")
    request = yt.videos().insert(part="snippet,status", body=body, media_body=_media(path, "video/mp4"))
    tt.set_field(d, "upload_dang_cho_id", key)
    from googleapiclient.errors import HttpError
    try:
        return request.execute(num_retries=RETRIES)["id"]
    except HttpError as e:
        if e.resp.status in (400, 401, 403):  # YouTube từ chối từ đầu (vd quotaExceeded): chắc chắn chưa tạo video, gỡ cờ
            tt.set_field(d, "upload_dang_cho_id", None)
        raise


@contextmanager
def _lock(path: Path):
    with path.open("a") as f:
        if os.name != "nt":
            import fcntl
            fcntl.flock(f, fcntl.LOCK_EX)
            yield
            return
        import msvcrt  # Windows không có fcntl
        f.seek(0)
        while True:
            try:
                msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)  # tự chờ ~10 s rồi báo lỗi, nên lặp để chờ như flock
                break
            except OSError as e:
                if e.errno not in (errno.EACCES, errno.EDEADLK) and getattr(e, "winerror", None) not in (33, 36):
                    raise
                time.sleep(0.05)
        try:
            yield
        finally:
            f.seek(0)
            msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)


def _track(tracker: Path, title: str, when_vn: str, vid: str, them: dict | None = None) -> None:
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
        rows.append({"ngay": when_vn.split()[0], "tieu_de": title, "gio_dang": when_vn, "link": link, **(them or {})})
        tmp = tracker.with_name(f".{tracker.name}.tmp")
        with tmp.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)
        os.replace(tmp, tracker)


def upload(video_dir, date_vn: str, time_vn: str, youtube=None, tracker: Path = TRACKER,
           playlist_id: str | None = None, cho_phep_ngan: str | None = None) -> str:
    d = Path(video_dir)
    with _lock(d / ".dang.lock"):
        return _upload(d, date_vn, time_vn, youtube, Path(tracker), playlist_id, cho_phep_ngan)


def _upload(d: Path, date_vn: str, time_vn: str, youtube, tracker: Path, playlist_id: str | None,
            cho_phep_ngan: str | None = None) -> str:
    state = tt.load(d)
    if state["steps"]["dang"]["status"] == "xong":
        return state["video_id"]
    _guard(d)
    if not state.get("video_id"):  # video đã tạo trên YouTube (chạy lại sau lỗi) thì không chặn nữa
        kiem_thoi_luong(d, cho_phep_ngan)
    for w in kiem_tra_gio_vang(time_vn):
        print(f"⚠️  {w}")
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
    yt.thumbnails().set(videoId=vid, media_body=_thumb_media(d / _chosen(d)["file_thumb"])).execute(num_retries=RETRIES)
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
    them = {"khuon_short": s.get("khuon", "cu")}  # Short cũ không ghi khuon: dựng kiểu thu nhỏ sân khấu ngang
    if key in done:
        saved = schedules.get(key, {"tieu_de": s["tieu_de"], "gio": when})
        _track(tracker, saved["tieu_de"], saved["gio"], done[key], them)
        return done[key]
    _guard(d)
    if not tt.short_current(d, index):
        raise PermissionError("Short chưa duyệt hoặc tệp/tiêu đề/giờ đã đổi sau khi duyệt: chạy lại "
                              f"`python -m tttc.trang_thai duyet-short {d} {index}` sau khi người dùng xem lại")
    desc = s.get("mo_ta") or goi["mo_ta"]  # Short viết riêng có mô tả riêng; không có thì dùng mô tả video dài
    long_vid = state.get("video_id")
    if long_vid:
        desc = f"👉 Xem video phân tích chi tiết đầy đủ tại: https://youtu.be/{long_vid}\n\n" + desc
    tags = goi.get("tags", [])
    desc = gan_hashtag(desc, tags, is_short=True)
    body = _body(s["tieu_de"], desc, tags, publish_at(s["ngay"], s["gio"]))
    yt = youtube or client()
    vid = _insert(d, yt, body, d / s["file"], f"short:{key}")
    done[key] = vid
    schedules[key] = {"tieu_de": s["tieu_de"], "gio": when}
    tt.set_fields(d, short_ids=done, short_lich=schedules, upload_dang_cho_id=None)
    _track(tracker, s["tieu_de"], when, vid, them)
    return vid


def binh_luan_ghim(youtube, video_id: str, text: str) -> str:
    """Đăng bình luận mở đầu (để ghim trên YouTube Studio) điều hướng người xem."""
    res = youtube.commentThreads().insert(
        part="snippet",
        body={"snippet": {"videoId": video_id, "topLevelComment": {"snippet": {"textOriginal": text}}}},
    ).execute(num_retries=RETRIES)
    return res["id"]


def login(client_secret_json: str | None = None, ten: str = "youtube-token", scopes: list[str] = SCOPES) -> None:
    """Một lần: mở trình duyệt đăng nhập tài khoản kênh, lưu token vào Keychain.
    Không đưa client_secret.json thì dùng bản đã lưu trong Keychain từ lần đăng nhập trước."""
    import keyring
    from google_auth_oauthlib.flow import InstalledAppFlow
    secret = Path(client_secret_json).read_text(encoding="utf-8") if client_secret_json else keyring.get_password(KR, "youtube-client")
    if not secret:
        raise RuntimeError("Chưa có client_secret: chạy `uv run python -m tttc.dang login <client_secret.json>`")
    flow = InstalledAppFlow.from_client_config(json.loads(secret), scopes)
    creds = flow.run_local_server(port=0)
    keyring.set_password(KR, "youtube-client", secret)
    keyring.set_password(KR, ten, creds.to_json())


def _creds(ten: str):
    """Đọc token `ten` từ Keychain với đúng các quyền đã cấp lúc đăng nhập (không xin thêm quyền khi làm mới); None nếu chưa có."""
    import keyring
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    tok = keyring.get_password(KR, ten)
    if not tok:
        return None
    creds = Credentials.from_authorized_user_info(json.loads(tok))
    if not creds.valid:
        creds.refresh(Request())
        keyring.set_password(KR, ten, creds.to_json())
    return creds


def client():
    from googleapiclient.discovery import build
    creds = _creds("youtube-token")
    if creds is None:
        raise RuntimeError("Chưa đăng nhập YouTube: chạy `uv run python -m tttc.dang login <client_secret.json>`")
    return build("youtube", "v3", credentials=creds)


def analytics_client():
    """Client YouTube Analytics (token riêng `analytics-token`, chỉ đọc); None nếu chưa đăng nhập `login-analytics`."""
    from googleapiclient.discovery import build
    creds = _creds("analytics-token")
    return None if creds is None else build("youtubeAnalytics", "v2", credentials=creds)


def reporting_client():
    """Client YouTube Reporting (CTR thumbnail, `tttc.reach`), cùng token `analytics-token`; None nếu chưa đăng nhập."""
    from googleapiclient.discovery import build
    creds = _creds("analytics-token")
    return None if creds is None else build("youtubereporting", "v1", credentials=creds)


if __name__ == "__main__":
    if sys.argv[1] == "login":
        login(sys.argv[2] if len(sys.argv) > 2 else None)
    elif sys.argv[1] == "login-analytics":
        login(None, "analytics-token", ANALYTICS_SCOPES)
    elif sys.argv[1] == "short":
        print(upload_short(sys.argv[2], int(sys.argv[3])))
    elif sys.argv[1] == "comment":
        print(binh_luan_ghim(client(), sys.argv[2], sys.argv[3]))
    else:  # python -m tttc.dang <thư mục> <dd/mm/yyyy> <HH:MM> [--cho-phep-ngan "<lý do>"]
        a = sys.argv[1:]
        ngan = a[a.index("--cho-phep-ngan") + 1] if "--cho-phep-ngan" in a and a.index("--cho-phep-ngan") + 1 < len(a) else None
        print(upload(a[0], a[1], a[2], cho_phep_ngan=ngan))
