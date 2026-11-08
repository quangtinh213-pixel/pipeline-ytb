"""Ảnh nhân vật từ Wikimedia Commons, chỉ giấy phép tự do, có ghi công."""
import json
import re
import unicodedata
from html import unescape
from pathlib import Path

import requests

API = "https://commons.wikimedia.org/w/api.php"
UA = {"User-Agent": "TuiTienCongNghe-pipeline/0.1"}
FREE = re.compile(r"^(public domain|pd\b.*|cc0.*|cc by(-sa)? \d(\.\d)?.*)$", re.I)
PD = re.compile(r"^(public domain|pd\b.*|cc0.*)$", re.I)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", "", html or ""))).strip()


def search(query: str, limit: int = 10, get=requests.get) -> list[dict]:
    params = {"action": "query", "format": "json", "generator": "search", "gsrsearch": query,
              "gsrnamespace": 6, "gsrlimit": limit, "prop": "imageinfo", "iiprop": "url|extmetadata",
              "iiurlwidth": 1600, "iiextmetadatafilter": "LicenseShortName|Artist|License|UsageTerms"}
    r = get(API, params=params, headers=UA, timeout=30)
    r.raise_for_status()
    pages = sorted((r.json().get("query") or {}).get("pages", {}).values(), key=lambda p: p.get("index", 0))
    out = []
    for p in pages:
        ii = (p.get("imageinfo") or [{}])[0]
        meta = ii.get("extmetadata", {})
        out.append({"file": p["title"], "url": ii.get("thumburl") or ii.get("url", ""),
                    "giay_phep": _text(meta.get("LicenseShortName", {}).get("value", "")),
                    "tac_gia": _text(meta.get("Artist", {}).get("value", "")),
                    "link": ii.get("descriptionurl", "")})
    return out


def pick(results: list[dict]) -> dict | None:
    for r in results:
        lic = r["giay_phep"].strip()
        if not FREE.match(lic) or not r["url"]:
            continue
        if not r["tac_gia"]:
            if not PD.match(lic):
                continue  # CC bắt buộc ghi tác giả
            r = dict(r, tac_gia="Không rõ tác giả")
        return r
    return None


def _safe_name(file: str) -> str:
    name = unicodedata.normalize("NFKD", file.removeprefix("File:"))
    name = re.sub(r"[^\w.\-]+", "-", name.encode("ascii", "ignore").decode()).strip("-").lower()
    return name or "anh"


def download(item: dict, video_dir, get=requests.get) -> Path:
    d = Path(video_dir) / "anh"
    d.mkdir(parents=True, exist_ok=True)
    r = get(item["url"], headers=UA, timeout=60)
    r.raise_for_status()
    path = d / _safe_name(item["file"])
    path.write_bytes(r.content)
    log = d / "ghi-cong.json"
    credits = json.loads(log.read_text(encoding="utf-8")) if log.exists() else []
    credits.append({"tep": path.name, "file": item["file"], "tac_gia": item["tac_gia"],
                    "giay_phep": item["giay_phep"], "link": item["link"],
                    "ghi_cong": f"{item['tac_gia']}, Wikimedia Commons, {item['giay_phep']}"})
    log.write_text(json.dumps(credits, ensure_ascii=False, indent=1), encoding="utf-8")
    return path
