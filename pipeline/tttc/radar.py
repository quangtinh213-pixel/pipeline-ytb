"""Radar chọn đề: chấm điểm đề tin, xếp hạng, ghi chu-de.md; đọc RSS công khai của kênh đối thủ.

Chỉ dùng tiêu đề, giờ đăng và số view của đối thủ làm tín hiệu; không lấy lời, kịch bản hay hình của họ.
Chạy: uv run python -m tttc.radar rss
"""
import json
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

PIPE = Path(__file__).resolve().parent.parent
CONFIG = PIPE / "config.json"
VN = timezone(timedelta(hours=7))
RSS = "https://www.youtube.com/feeds/videos.xml?channel_id={}"
SUGGEST_URL = "https://suggestqueries.google.com/complete/search"
NS = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015",
      "m": "http://search.yahoo.com/mrss/"}
THUC_THE_BAO_HOA = [
    "nvidia", "apple", "iphone", "microsoft", "openai",
    "google", "grab", "viettel", "chatgpt", "ai", "chip",
]


def doc_rss(channel_id: str, get=requests.get) -> list[dict]:
    """[{"id","tieu_de","dang_luc" (UTC+7),"view" (None nếu thiếu)}], bỏ qua mục hỏng."""
    try:
        r = get(RSS.format(channel_id), timeout=20)
        r.raise_for_status()
        root = ET.fromstring(r.text)
    except Exception as e:  # mạng, HTTP, XML hỏng: báo một loại lỗi, không làm sập vòng quét
        raise RuntimeError(f"RSS đối thủ không đọc được: {e}") from e
    out = []
    for e in root.findall("a:entry", NS):
        vid, title, pub = e.findtext("yt:videoId", namespaces=NS), e.findtext("a:title", namespaces=NS), e.findtext("a:published", namespaces=NS)
        if not (vid and title and pub):
            continue
        stat = e.find("m:group/m:community/m:statistics", NS)
        view = int(stat.get("views")) if stat is not None and (stat.get("views") or "").isdigit() else None
        out.append({"id": vid, "tieu_de": title, "dang_luc": datetime.fromisoformat(pub).astimezone(VN), "view": view})
    return out


def cham_diem(soc: int, so_lon: int, goc_vn: int) -> int:
    """soc + so_lon + 2 × goc_vn; mỗi thành phần 0–2 (góc Việt Nam nặng gấp đôi nhưng không loại cứng)."""
    for v in (soc, so_lon, goc_vn):
        if v not in (0, 1, 2):
            raise ValueError(f"điểm phải là 0, 1 hoặc 2, nhận {v}")
    return soc + so_lon + 2 * goc_vn


def xep_hang(de: list[dict], toi_thieu: int = 4) -> list[dict]:
    ok = [{**d, "diem": cham_diem(d["soc"], d["so_lon"], d["goc_vn"])} for d in de]
    ok = [d for d in ok if d["diem"] >= toi_thieu]
    return sorted(ok, key=lambda d: (-d["diem"], d["goc_vn"] == 0, -d["moi_luc"].timestamp()))


def _van_ban_chu_de(d: Path) -> str:
    """Trích tên thư mục và chủ đề thực sự (ưu tiên dong-goi.json / Đề 1; bỏ cảnh báo bão hòa và Đề 2–3)."""
    parts = [d.name.replace("_", " ")]
    goi_p = d / "dong-goi.json"
    if goi_p.exists():
        try:
            goi = json.loads(goi_p.read_text(encoding="utf-8", errors="ignore"))
            opts = goi.get("phuong_an") or []
            if opts:
                tt_p = d / "trang-thai.json"
                chon = None
                if tt_p.exists():
                    st = json.loads(tt_p.read_text(encoding="utf-8", errors="ignore"))
                    chon = st.get("pa_dang_dung") or st.get("chon")
                idx = chon - 1 if isinstance(chon, int) and 1 <= chon <= len(opts) else 0
                parts.append(opts[idx].get("tieu_de", ""))
                if goi.get("tags"):
                    parts.append(" ".join(str(t) for t in goi["tags"][:6]))
                return unicodedata.normalize("NFC", "\n".join(parts))
        except Exception:
            pass
    chu_de = d / "chu-de.md"
    if chu_de.exists():
        lines = [ln for ln in chu_de.read_text(encoding="utf-8", errors="ignore").splitlines() if not ln.lstrip().startswith(">")]
        raw = "\n".join(lines)
        if "## Đề 1" in raw and "## Đề 2" in raw:
            raw = raw.split("## Đề 2", 1)[0]
        parts.append(raw)
    return unicodedata.normalize("NFC", "\n".join(parts))


def kiem_bao_hoa(videos_dir: Path, thuc_the: list[str] | None = None, so_ngay: int = 4) -> dict[str, int]:
    """Đếm số video gần đây (tối đa so_ngay * 2 thư mục mới nhất) có nhắc mỗi thực thể; trả về mục >= 2."""
    root = Path(videos_dir)
    if not root.exists() or so_ngay <= 0:
        return {}
    entities = THUC_THE_BAO_HOA if thuc_the is None else thuc_the
    if not entities:
        return {}
    dirs = sorted(
        (p for p in root.iterdir() if p.is_dir() and not p.name.startswith(".")),
        key=lambda p: p.name,
        reverse=True,
    )[: so_ngay * 2]
    patterns = []
    for e in entities:
        if not e.strip():
            continue
        norm = unicodedata.normalize("NFC", e)
        # Tránh đếm nhầm đại từ tiếng Việt "ai" trong lời dẫn; chỉ bắt "AI" viết hoa hoặc slug thư mục "-ai-"
        if norm.lower() == "ai":
            pat = re.compile(r"(?<!\w)AI(?!\w)|(?:^|[-_ ])ai(?:$|[-_ ])")
            patterns.append((e, pat, False))
        else:
            patterns.append((e, re.compile(rf"(?<!\w){re.escape(norm.lower())}(?!\w)"), True))
    counts: dict[str, int] = {}
    for d in dirs:
        raw_text = _van_ban_chu_de(d)
        low_text = raw_text.lower()
        for e, pat, use_lower in patterns:
            if pat.search(low_text if use_lower else raw_text):
                counts[e] = counts.get(e, 0) + 1
    return {e: c for e, c in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])) if c >= 2}


def goi_y_tu_khoa(tu_khoa: str, get=requests.get) -> list[str]:
    """Lấy tối đa 5 gợi ý tìm kiếm YouTube từ Google Suggest; trả về [] nếu lỗi mạng hoặc dữ liệu hỏng."""
    q = (tu_khoa or "").strip()
    if not q:
        return []
    try:
        r = get(
            SUGGEST_URL,
            params={"client": "firefox", "ds": "yt", "hl": "vi", "q": q},
            timeout=5,
        )
        r.raise_for_status()
        data = r.json() if hasattr(r, "json") else json.loads(r.text)
        if not isinstance(data, list) or len(data) < 2 or not isinstance(data[1], list):
            return []
        return [str(x) for x in data[1][:5] if x is not None and str(x).strip()]
    except Exception:
        return []


def ghi_chu_de(
    video_dir,
    top: list[dict],
    ho_da_dang: dict[str, bool] | None = None,
    goi_y: dict[str, list[str]] | None = None,
    bao_hoa: dict[str, int] | None = None,
) -> Path:
    ho_da_dang = ho_da_dang or {}
    goi_y = goi_y or {}
    khối = []
    for n, d in enumerate(top[:3], 1):
        ho = {True: "có", False: "không"}.get(ho_da_dang.get(d["tieu_de"]), "chưa rõ")
        muc = (f"## Đề {n}: {d['tieu_de']}\n- Điểm: {d['diem']} (sốc {d['soc']}, số lớn {d['so_lon']}, "
               f"góc Việt Nam {d['goc_vn']}×2)\n- Tin gốc: {d['link']}\n- Họ đã đăng cùng sự kiện: {ho}\n")
        if kws := goi_y.get(d["tieu_de"]):
            muc += f"- Từ khóa tìm kiếm gợi ý: {', '.join(kws)}\n"
        khối.append(muc)
    if bao_hoa:
        chi_tiet = ", ".join(f"{k} ({v} video)" for k, v in bao_hoa.items())
        khối.insert(0, f"> ⚠️ Cảnh báo bão hòa chủ đề gần đây: {chi_tiet}\n")
    p = Path(video_dir) / "chu-de.md"
    p.write_text("\n".join(khối), encoding="utf-8", newline="\n")
    return p


def main(argv: list[str], get=requests.get) -> int:
    if argv[:1] != ["rss"]:
        print("dùng: python -m tttc.radar rss")
        return 2
    kenh = json.loads(CONFIG.read_text(encoding="utf-8"))["doi_thu"]["kenh_id"]
    try:
        for i in doc_rss(kenh, get=get):
            print(f"{i['dang_luc']:%d/%m %H:%M} · {i['view'] if i['view'] is not None else '?'} view · {i['tieu_de']}")
    except RuntimeError as e:
        print(e)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
