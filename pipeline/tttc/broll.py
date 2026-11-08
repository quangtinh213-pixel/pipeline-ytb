"""B-roll miễn phí từ Pexels (giấy phép Pexels: dùng thương mại, không bắt buộc ghi công – kênh vẫn ghi)."""
import json
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
