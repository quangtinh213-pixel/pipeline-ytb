"""B-roll: kho clip tải thủ công (pipeline/broll-kho/) là đường chính; Pexels API là đường phụ khi có khoá.

Giấy phép Pexels/Pixabay: dùng thương mại, không bắt buộc ghi công – kênh vẫn ghi.
"""
import json
import re
import subprocess
import unicodedata
from pathlib import Path

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
        path.write_bytes(r.content)
    log = d / "ghi-cong.json"
    credits = json.loads(log.read_text(encoding="utf-8")) if log.exists() else []
    if not any(c["tep"] == path.name for c in credits):
        credits.append({"tep": path.name, "tac_gia": item["tac_gia"], "link": item["trang"],
                        "ghi_cong": f"Video: {item['tac_gia']} trên Pexels"})
        log.write_text(json.dumps(credits, ensure_ascii=False, indent=1), encoding="utf-8")
    return path


KHO = Path(__file__).resolve().parent.parent / "broll-kho"
VIDEO_EXT = {".mp4", ".mov", ".webm", ".m4v", ".mkv"}


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


def nhap(src: Path, video_dir, ghi_cong: str, bat_dau: float = 0.0, do_dai: float | None = None) -> Path:
    """Cắt clip từ kho vào V/broll/: 1920×1080 phủ kín (cắt mép), 30 fps, H.264, bỏ tiếng; ghi công một lần."""
    if not ghi_cong.strip():
        raise ValueError("B-roll phải có ghi công (vd 'Video: Tên tác giả trên Pexels')")
    src = Path(src)
    d = Path(video_dir) / "broll"
    d.mkdir(parents=True, exist_ok=True)
    # shortcut: tên ra theo tên clip gốc, một clip chỉ dùng một đoạn mỗi video; cần nhiều đoạn thì thêm hậu tố
    out = d / f"{_slug(src.stem)}.mp4"
    cut = (["-ss", str(bat_dau)] if bat_dau else []) + (["-t", str(do_dai)] if do_dai else [])
    subprocess.run(["ffmpeg", "-v", "error", "-y", *cut, "-i", str(src), "-an",
                    "-vf", "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080",
                    "-r", "30", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", str(out)], check=True)
    log = d / "ghi-cong.json"
    credits = json.loads(log.read_text(encoding="utf-8")) if log.exists() else []
    if not any(c["tep"] == out.name for c in credits):
        credits.append({"tep": out.name, "ghi_cong": ghi_cong.strip(), "nguon_tep": src.name})
        log.write_text(json.dumps(credits, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


if __name__ == "__main__":
    for e in quet_kho():
        print("mới:", e["tep"], e["do_dai"], "s")
