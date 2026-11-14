"""Đồng bộ lượt xem và tín hiệu đối thủ từ YouTube Data API + RSS về theo-doi.csv.
Chạy: uv run python scripts/dong-bo-view.py  – nên chạy mỗi ngày để không lỡ cửa sổ 24–48 giờ.
"""
import csv
import json
import re
import unicodedata
from datetime import datetime, timedelta
from pathlib import Path
from tttc import giam_sat, radar, reach, theo_doi
from tttc.dang import analytics_client, client, reporting_client, _lock
from tttc.theo_doi import VN, dien_view

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "pipeline" / "config.json"
TRACKER = ROOT / "theo-doi.csv"
LO = 50  # videos.list nhận tối đa 50 id mỗi lần
CHO_DU_LIEU = 9  # 7 ngày đo + khoảng 2 ngày Analytics trễ
_STOP_WORDS = {
    "của", "cho", "với", "những", "người", "dùng", "này", "khi", "sao", "làm",
    "việt", "nam", "video", "shorts", "cách", "trên", "dưới", "hơn", "nhất",
    "cũng", "nhưng", "chỉ", "mới", "từ", "đã", "đang", "sẽ", "gì", "nào",
}


def _vid(r: dict) -> str | None:
    m = re.search(r"youtu\.be/([A-Za-z0-9_-]+)", r.get("link", ""))
    return m.group(1) if m else None


def _tokens(text: str) -> set[str]:
    norm = unicodedata.normalize("NFC", text or "").lower()
    return {t for t in re.findall(r"[0-9a-zA-ZÀ-ỹ]{2,}", norm) if t not in _STOP_WORDS}


def cap_nhat_doi_thu(rows: list[dict], rss_items: list[dict], now: datetime) -> int:
    """Đối chiếu RSS của đối thủ để tự điền trung_de_ho, chenh_gio và view_ho_24h vào theo-doi.csv."""
    if not rss_items:
        return 0
    item_toks = [(it, _tokens(it.get("tieu_de", ""))) for it in rss_items]
    by_id = {it["id"]: it for it in rss_items if it.get("id")}
    changed = 0
    for r in rows:
        title = r.get("tieu_de", "")
        if "#shorts" in title.lower():
            continue
        try:
            gio_minh = datetime.strptime(r.get("gio_dang", ""), "%d/%m/%Y %H:%M").replace(tzinfo=VN)
        except ValueError:
            continue
        match_id = (r.get("trung_de_ho") or "").strip()
        matched = by_id.get(match_id) if match_id else None
        if matched is None:
            rtoks = _tokens(title)
            cands = []
            for it, toks in item_toks:
                delta_h = abs(theo_doi.chenh_gio(gio_minh, it["dang_luc"]))
                chung = len(rtoks & toks)
                if delta_h <= 24 and chung >= 2:
                    cands.append((chung, -delta_h, it))
            if cands:
                cands.sort(key=lambda x: (-x[0], -x[1]))
                matched = cands[0][2]
        if matched is None:
            continue
        row_changed = False
        if not match_id and matched.get("id"):
            r["trung_de_ho"] = matched["id"]
            row_changed = True
        if not (r.get("chenh_gio") or "").strip():
            r["chenh_gio"] = f"{theo_doi.chenh_gio(gio_minh, matched['dang_luc']):+.1f}"
            row_changed = True
        if not (r.get("view_ho_24h") or "").strip() and matched.get("view") is not None:
            if (now - matched["dang_luc"]) >= timedelta(hours=24):
                r["view_ho_24h"] = str(matched["view"])
                row_changed = True
        changed += int(row_changed)
    return changed


def _giay(iso: str) -> float:
    """Thời lượng ISO 8601 của Data API (PT1H2M3S) ra giây."""
    m = re.fullmatch(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    if not m:
        return 0.0
    d, h, mi, s = (int(x or 0) for x in m.groups())
    return float(((d * 24 + h) * 60 + mi) * 60 + s)


def cap_nhat_giu_chan(rows: list[dict], thoi_luong: dict[str, float], analytics, now: datetime) -> int:
    """Điền giu_chan_30s còn trống bằng tỉ lệ người xem còn ở giây 30, tính trên 7 ngày đầu của video.
    Analytics trễ khoảng 2–3 ngày nên chỉ điền khi video đủ CHO_DU_LIEU ngày; số không đổi theo ngày chạy."""
    if analytics is None:
        return 0
    changed = 0
    for r in rows:
        v = _vid(r)
        if not v or (r.get("giu_chan_30s") or "").strip() or v not in thoi_luong:
            continue
        try:
            ngay = datetime.strptime(r.get("gio_dang", ""), "%d/%m/%Y %H:%M").date()
        except ValueError:
            continue
        # shortcut: ngày của Analytics theo giờ Thái Bình Dương, ở đây lấy ngày VN; lệch tối đa vài giờ đầu, đổi khi cần số chính xác tới giờ
        if (now.date() - ngay).days < CHO_DU_LIEU:
            continue
        w = giam_sat.giu_chan_tai(analytics, v, 30, thoi_luong[v], ngay.isoformat(), (ngay + timedelta(days=6)).isoformat())
        if w is not None:
            r["giu_chan_30s"] = f"{w * 100:.0f}%"
            changed += 1
    return changed


def cap_nhat_ctr(rows: list[dict], reporting, now: datetime, tai=reach.tai) -> int:
    """Điền ctr còn trống bằng CTR thumbnail gộp 7 ngày đầu (Reporting API). Chỉ điền khi đủ báo cáo cả 7 ngày.
    Dòng đã có CTR điền tay thì không ghi đè, chỉ in số tính được để đối chiếu đơn vị."""
    if reporting is None:
        return 0
    job = reach.job_id(reporting)
    ngay_url = reach.bao_cao_theo_ngay(reporting, job)
    if not ngay_url:
        print(f"CTR: job {job} chưa có báo cáo (báo cáo đầu tiên có sau khoảng 48 giờ kể từ lúc tạo job)")
        return 0
    cache: dict = {}
    changed = 0
    for r in rows:
        v = _vid(r)
        try:
            ngay = datetime.strptime(r.get("gio_dang", ""), "%d/%m/%Y %H:%M").replace(tzinfo=VN).astimezone(reach.PT).date()
        except ValueError:
            continue
        cac_ngay = [ngay + timedelta(days=k) for k in range(7)]
        if not v or not all(d in ngay_url for d in cac_ngay):
            continue
        for d in cac_ngay:
            if d not in cache:
                cache[d] = reach.doc_csv(tai(reporting, ngay_url[d]))
        c = reach.ctr([cache[d] for d in cac_ngay], v)
        if c is None:
            continue
        if (r.get("ctr") or "").strip():
            print(f"CTR đối chiếu {v}: sổ {r['ctr']} – báo cáo {c * 100:.1f}%")
            continue
        r["ctr"] = f"{c * 100:.1f}%"
        changed += 1
    return changed


def dong_bo():
    if not TRACKER.exists():
        print("Không tìm thấy theo-doi.csv")
        return

    with _lock(TRACKER.with_name(f".{TRACKER.name}.lock")):
        with TRACKER.open(encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []
            rows = list(reader)

        vids = [v for r in rows if (v := _vid(r))]
        if not vids:
            print("Không có video id trong theo-doi.csv")
            return

        yt = client()
        stats, thoi_luong = {}, {}
        for i in range(0, len(vids), LO):
            resp = yt.videos().list(part="statistics,contentDetails", id=",".join(vids[i:i + LO])).execute()
            stats |= {it["id"]: it["statistics"].get("viewCount", "0") for it in resp.get("items", [])}
            thoi_luong |= {it["id"]: _giay(it.get("contentDetails", {}).get("duration", "")) for it in resp.get("items", [])}

        now = datetime.now(VN)
        updated = sum(dien_view(r, stats[v], now) for r in rows if (v := _vid(r)) in stats)

        try:
            an = analytics_client()
        except Exception as e:  # token hết hạn/bị thu hồi: vẫn ghi phần view, chỉ bỏ phần giữ chân
            print(f"Cảnh báo Analytics: {e}")
            an = None
        if an is None:
            print("Bỏ qua giữ chân 30s: chưa có token Analytics (chạy `uv run python -m tttc.dang login-analytics`)")
        giu_chan_updated = cap_nhat_giu_chan(rows, thoi_luong, an, now)

        ctr_updated = 0
        try:
            ctr_updated = cap_nhat_ctr(rows, reporting_client(), now)
        except Exception as e:  # API chưa bật / mạng lỗi: vẫn ghi các cột khác
            print(f"Cảnh báo CTR (Reporting API): {str(e)[:300]}")

        opp_updated = 0
        if CONFIG.exists():
            kenh_ho = json.loads(CONFIG.read_text(encoding="utf-8")).get("doi_thu", {}).get("kenh_id")
            if kenh_ho:
                try:
                    opp_updated = cap_nhat_doi_thu(rows, radar.doc_rss(kenh_ho), now)
                except RuntimeError as e:
                    print(f"Cảnh báo đồng bộ đối thủ: {e}")

        tmp = TRACKER.with_name(f".{TRACKER.name}.tmp")
        with tmp.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)
        tmp.replace(TRACKER)
        print(f"Đã điền số view cho {updated}/{len(rows)} video, giữ chân 30s cho {giu_chan_updated} video, CTR cho {ctr_updated} video "
              f"và đối chiếu đối thủ cho {opp_updated} dòng vào theo-doi.csv")


if __name__ == "__main__":
    dong_bo()
