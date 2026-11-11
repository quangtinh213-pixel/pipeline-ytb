"""B-roll: kho clip tải thủ công (pipeline/broll-kho/) là đường chính; Pexels API là đường phụ khi có khoá.

Giấy phép Pexels/Pixabay: dùng thương mại, không bắt buộc ghi công – kênh vẫn ghi.
"""
import io
import json
import re
import subprocess
import tempfile
import unicodedata
from pathlib import Path
from urllib.parse import urlparse

import requests

API = "https://api.pexels.com/videos/search"
KR = "tui-tien-cong-nghe"


def _key() -> str:
    import keyring
    k = keyring.get_password(KR, "pexels")
    if not k:
        raise RuntimeError("Chưa có khoá Pexels trong Keychain (service tui-tien-cong-nghe, tên pexels)")
    return k


def search(query: str, key: str | None = None, per_page: int = 15, get=requests.get) -> list[dict]:
    r = get(API, params={"query": query, "orientation": "landscape", "size": "medium", "per_page": per_page},
            headers={"Authorization": key or _key()}, timeout=30)
    r.raise_for_status()
    return r.json().get("videos", [])


def pick(videos: list[dict], min_seconds: float) -> dict | None:
    """Clip đủ dài cho cảnh, khổ ngang, chọn tệp mp4 gần 1920 px nhất (không lấy 4K cho nhẹ render)."""
    for v in videos:
        if v.get("duration", 0) < min_seconds:
            continue
        files = [f for f in v.get("video_files", []) if f.get("file_type") == "video/mp4"
                 and f.get("width", 0) > f.get("height", 0) and 1280 <= f.get("width", 0) <= 2560]
        if files:
            best = min(files, key=lambda f: abs(f["width"] - 1920))
            return {"id": v["id"], "link": best["link"], "duration": v["duration"],
                    "tac_gia": v.get("user", {}).get("name", "Pexels"), "trang": v.get("url", "")}
    return None


def download(item: dict, video_dir, get=requests.get) -> Path:
    d = Path(video_dir) / "broll"
    d.mkdir(parents=True, exist_ok=True)
    path = d / f"pexels-{item['id']}.mp4"
    if not path.exists():
        r = get(item["link"], timeout=120)
        r.raise_for_status()
        tmp = path.with_suffix(".tmp")
        tmp.write_bytes(r.content)
        tmp.replace(path)  # ghi nguyên tử: tải dở không để lại tệp cắt cụt bị coi là đã có
    log = d / "ghi-cong.json"
    credits = json.loads(log.read_text(encoding="utf-8")) if log.exists() else []
    if not any(c["tep"] == path.name for c in credits):
        credits.append({"tep": path.name, "tac_gia": item["tac_gia"], "link": item["trang"],
                        "ghi_cong": f"Video: {item['tac_gia']} trên Pexels"})
        log.write_text(json.dumps(credits, ensure_ascii=False, indent=1), encoding="utf-8")
    return path


KHO = Path(__file__).resolve().parent.parent / "broll-kho"
VIDEO_EXT = {".mp4", ".mov", ".webm", ".m4v", ".mkv"}
ANH_EXT = {".jpg", ".jpeg", ".png", ".webp"}


def _ascii(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.replace("đ", "d").replace("Đ", "D"))
    return s.encode("ascii", "ignore").decode().lower()


def _slug(stem: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", _ascii(stem)).strip("-") or "clip"


def _duration(p: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True, check=True)
    return round(float(r.stdout.strip()), 2)


def quet_kho(kho: Path = KHO) -> list[dict]:
    """Thêm clip mới trong kho vào kho.json (giữ nguyên mục đã có); trả về các mục mới để Claude điền mo_ta/ghi_cong."""
    kho = Path(kho)
    path = kho / "kho.json"
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    co = {e["tep"] for e in data}
    moi = []
    for f in sorted(kho.iterdir()):
        if f.suffix.lower() in VIDEO_EXT and f.name not in co:
            moi.append({"tep": f.name, "do_dai": _duration(f), "mo_ta": "", "ghi_cong": "",
                        "tu_khoa": [t for t in re.split(r"[^a-z0-9]+", _ascii(f.stem)) if t]})
    if moi:
        path.write_text(json.dumps(data + moi, ensure_ascii=False, indent=1), encoding="utf-8")
    return moi


def _chuan_hoa(src: Path, out: Path, bat_dau: float = 0.0, do_dai: float | None = None, crf: int = 20) -> None:
    """1920×1080 phủ kín (cắt mép), 30 fps, H.264, bỏ tiếng."""
    cut = (["-ss", str(bat_dau)] if bat_dau else []) + (["-t", str(do_dai)] if do_dai else [])
    zoom = ""
    if Path(src).suffix.lower() in ANH_EXT:  # ảnh tĩnh: lặp thành clip, phóng chậm tới 108% cho đỡ đứng hình
        if not do_dai:
            raise ValueError("Ảnh tĩnh phải có do_dai")
        cut = ["-loop", "1", "-framerate", "30", "-t", str(do_dai)]
        # phóng to 4× trước: zoompan cắt theo điểm ảnh nguyên của ảnh vào, ảnh nhỏ thì khung nhảy từng bước (giật)
        zoom = ",scale=7680:4320:flags=lanczos,zoompan=z='min(1+0.0004*on,1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps=30"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *cut, "-i", str(src), "-an",
                    "-vf", "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080" + zoom,
                    "-r", "30", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", str(crf), str(out)], check=True)


TIN_CAY = {"videos.pexels.com", "cdn.pixabay.com", "upload.wikimedia.org"}


def tai_ve(url: str, ten: str, kho, ghi_cong: str, nguon: str, mo_ta: str, tu_khoa: list[str],
           get=requests.get) -> Path:
    """Tải một clip (chỉ từ máy chủ tin cậy) vào kho: chuẩn hoá ≤ 20 s, thêm mục kho.json. Đã có thì bỏ qua."""
    if urlparse(url).hostname not in TIN_CAY:
        raise ValueError(f"Không tải từ máy chủ ngoài danh sách tin cậy: {urlparse(url).hostname}")
    if not ghi_cong.strip():
        raise ValueError("Clip phải có ghi công")
    kho = Path(kho)
    path = kho / "kho.json"
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    out = kho / f"{_slug(ten)}.mp4"
    if out.exists() and any(e["tep"] == out.name for e in data):
        return out
    with tempfile.TemporaryDirectory() as tmp:
        raw = Path(tmp) / "tai.mp4"
        r = get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=180)
        r.raise_for_status()
        raw.write_bytes(r.content)
        probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                "stream=codec_type", "-of", "csv=p=0", str(raw)], capture_output=True, text=True)
        if "video" not in probe.stdout:
            raise RuntimeError(f"Tệp tải về không phải video: {url}")
        _chuan_hoa(raw, out, do_dai=20, crf=22)
    data.append({"tep": out.name, "do_dai": _duration(out), "mo_ta": mo_ta, "ghi_cong": ghi_cong.strip(),
                 "tu_khoa": tu_khoa, "nguon": nguon})
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


def soi(clip: Path, out_png, w: int = 320, h: int = 180) -> Path:
    """3 khung (10%, 50%, 90%) cạnh nhau để duyệt mặt người, logo, chữ trước khi dùng clip."""
    from PIL import Image
    dur = _duration(Path(clip))
    strip = Image.new("RGB", (3 * w, h))
    for k, f in enumerate((0.1, 0.5, 0.9)):
        png = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{dur * f:.2f}", "-i", str(clip), "-frames:v", "1",
                              "-vf", f"scale={w}:{h}", "-f", "image2pipe", "-vcodec", "png", "-"],
                             capture_output=True, check=True).stdout
        strip.paste(Image.open(io.BytesIO(png)), (k * w, 0))
    out = Path(out_png)
    out.parent.mkdir(parents=True, exist_ok=True)
    strip.save(out)
    return out


def nhap(src: Path, video_dir, ghi_cong: str, bat_dau: float = 0.0, do_dai: float | None = None, hau_to: str = "") -> Path:
    """Cắt clip từ kho vào V/broll/: 1920×1080 phủ kín (cắt mép), 30 fps, H.264, bỏ tiếng; ghi công một lần."""
    if not ghi_cong.strip():
        raise ValueError("B-roll phải có ghi công (vd 'Video: Tên tác giả trên Pexels')")
    src = Path(src)
    d = Path(video_dir) / "broll"
    d.mkdir(parents=True, exist_ok=True)
    out = d / f"{_slug(src.stem)}{hau_to}.mp4"  # hau_to: lấy nhiều đoạn khác nhau từ cùng một clip
    _chuan_hoa(src, out, bat_dau, do_dai)
    log = d / "ghi-cong.json"
    credits = json.loads(log.read_text(encoding="utf-8")) if log.exists() else []
    if not any(c["tep"] == out.name for c in credits):
        credits.append({"tep": out.name, "ghi_cong": ghi_cong.strip(), "nguon_tep": src.name})
        log.write_text(json.dumps(credits, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


if __name__ == "__main__":
    for e in quet_kho():
        print("mới:", e["tep"], e["do_dai"], "s")
