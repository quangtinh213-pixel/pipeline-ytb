"""Radar chọn đề: chấm điểm đề tin, xếp hạng, ghi chu-de.md; đọc RSS công khai của kênh đối thủ.

Chỉ dùng tiêu đề, giờ đăng và số view của đối thủ làm tín hiệu; không lấy lời, kịch bản hay hình của họ.
Chạy: uv run python -m tttc.radar rss
"""
import json
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

PIPE = Path(__file__).resolve().parent.parent
CONFIG = PIPE / "config.json"
VN = timezone(timedelta(hours=7))
RSS = "https://www.youtube.com/feeds/videos.xml?channel_id={}"
NS = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015",
      "m": "http://search.yahoo.com/mrss/"}


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


def ghi_chu_de(video_dir, top: list[dict], ho_da_dang: dict[str, bool] | None = None) -> Path:
    ho_da_dang = ho_da_dang or {}
    khối = []
    for n, d in enumerate(top[:3], 1):
        ho = {True: "có", False: "không"}.get(ho_da_dang.get(d["tieu_de"]), "chưa rõ")
        khối.append(f"## Đề {n}: {d['tieu_de']}\n- Điểm: {d['diem']} (sốc {d['soc']}, số lớn {d['so_lon']}, "
                    f"góc Việt Nam {d['goc_vn']}×2)\n- Tin gốc: {d['link']}\n- Họ đã đăng cùng sự kiện: {ho}\n")
    p = Path(video_dir) / "chu-de.md"
    p.write_text("\n".join(khối), encoding="utf-8")
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
