"""Kiểm canh.json theo timestamp giọng đọc và xuất phụ đề SRT."""
import json
import re
import sys
import unicodedata
from pathlib import Path

from tttc.kiem import NUM, _scale, tokens, vi_value

MAU = {"minh-hoa", "bieu-do", "so-lon", "nhan-vat", "trang-nguon", "chuong", "trich-bao", "b-roll", "quy-trinh", "so-sanh", "thoi-gian"}
SVG_DIR = Path(__file__).resolve().parent.parent / "svg"
TOL = 0.5      # lệch cho phép giữa hình và tiếng (giây)
EPS = 0.01     # sai số làm tròn giữa hai cảnh liền nhau
CANH_MIN_LOI, CANH_MAX_LOI = 1.5, 10.0   # ngoài khoảng này là lỗi
DAN_THE, DAN_GOC = {"chao", "ngac-nhien", "nghi"}, {"phai", "trai"}  # nhân vật dẫn chuyện "Túi" (svg/tui-*.svg)
DONG = {"", "bob", "xoay", "dap", "chop", "tilt", "tho"}  # chuyển động lặp trong cảnh (templates/canh/dong.js)
CANH_MIN_CB, CANH_MAX_CB = 2.5, 6.0      # ngoài khoảng này là cảnh báo (chuẩn kênh mẫu: 2,5–4 s/cảnh)


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[.,!?:;\"'()…“”‘’]", "", unicodedata.normalize("NFC", s).lower())).strip()


def phrase_time(words: list[dict], phrase: str, start: float, end: float) -> float | None:
    """Thời điểm bắt đầu cụm từ đầu tiên khớp, trong cửa sổ [start, end) của cảnh."""
    toks = _norm(phrase).split()
    win = [w for w in words if start - 0.01 <= w["start"] < end]
    for i in range(len(win) - len(toks) + 1):
        if [_norm(w["w"]) for w in win[i:i + len(toks)]] == toks:
            return win[i]["start"]
    return None


def validate(scenes: dict, timing: dict, svg_dir: Path = SVG_DIR, nguon: list | tuple = (),
             video_dir: Path | None = None) -> list[str]:
    """Trả danh sách 'Lỗi: ...' (phải sửa) và 'Cảnh báo: ...' (nên xem)."""
    by_id = {n["id"]: n for n in nguon}
    msgs, ids = [], set(by_id)
    sc = scenes["scenes"]
    if not sc:
        return ["Lỗi: canh.json không có cảnh nào"]
    if abs(sc[0]["start"]) > TOL:
        msgs.append(f"Lỗi: cảnh đầu bắt đầu ở {sc[0]['start']} s, phải là 0")
    if abs(sc[-1]["end"] - timing["duration"]) > TOL:
        msgs.append(f"Lỗi: cảnh cuối kết thúc ở {sc[-1]['end']} s, tiếng dài {timing['duration']:.2f} s")
    for prev, cur in zip(sc, sc[1:]):
        if cur["start"] > prev["end"] + EPS:
            msgs.append(f"Lỗi: hở {cur['start'] - prev['end']:.2f} s giữa {prev['id']} và {cur['id']}")
        elif cur["start"] < prev["end"] - EPS:
            msgs.append(f"Lỗi: {prev['id']} và {cur['id']} chồng nhau {prev['end'] - cur['start']:.2f} s")
    seen = set()
    for c in sc:
        cid, dur = c["id"], c["end"] - c["start"]
        if cid in seen:
            msgs.append(f"Lỗi: trùng id cảnh {cid}")
        seen.add(cid)
        if c["mau"] not in MAU:
            msgs.append(f"Lỗi: {cid} dùng mẫu không có: {c['mau']}")
        if c.get("dan") is not None:
            msgs += _check_dan(c, timing.get("words", []))
        if c.get("dong", "") not in DONG:
            msgs.append(f"Lỗi: {cid} dong không hợp lệ: {c['dong']} (chọn {', '.join(sorted(DONG - {''}))})")
        if dur < CANH_MIN_LOI or dur > CANH_MAX_LOI:
            msgs.append(f"Lỗi: {cid} dài {dur:.1f} s (cho phép {CANH_MIN_LOI:g}–{CANH_MAX_LOI:g} s)")
        elif dur < CANH_MIN_CB or dur > CANH_MAX_CB:
            msgs.append(f"Cảnh báo: {cid} dài {dur:.1f} s (nên {CANH_MIN_CB:g}–{CANH_MAX_CB:g} s)")
        if c.get("svg") and not (Path(svg_dir) / f"{c['svg']}.svg").exists():
            msgs.append(f"Lỗi: {cid} cần hình {c['svg']}.svg chưa có trong thư viện")
        nid = (c.get("bieu_do") or {}).get("nguon_id") or c.get("nguon_id")
        nids = nid if isinstance(nid, list) else [nid] if nid else []
        for n in nids:
            if n not in ids:
                msgs.append(f"Lỗi: {cid} trỏ tới nguồn [#{n}] không có trong nguon.json")
        msgs += _check_values(c, [by_id[n] for n in nids if n in by_id], bool(nids))
        for ph in c.get("nhip") or []:
            if ph and phrase_time(timing.get("words", []), ph, c["start"], c["end"]) is None:
                msgs.append(f"Lỗi: {cid} có nhịp '{ph}' nhưng giọng đọc không nói cụm này trong cảnh")
        for label in _nhan_pills(c):
            if len(label.split()) > NHAN_MAX_TU:
                msgs.append(f"Cảnh báo: {cid} nhãn dài {len(label.split())} từ (≤ {NHAN_MAX_TU}): {label[:30]}")
        if c["mau"] == "quy-trinh":
            msgs += _check_quy_trinh(c, svg_dir)
        if c["mau"] == "so-sanh":
            msgs += _check_so_sanh(c, svg_dir)
        if c["mau"] == "thoi-gian":
            msgs += _check_thoi_gian(c)
        if c["mau"] == "trich-bao":
            msgs += _check_quote(c, by_id.get(c.get("nguon_id")))
        if c["mau"] == "b-roll" and video_dir is not None and not (Path(video_dir) / "broll" / c.get("video", "")).is_file():
            msgs.append(f"Lỗi: {cid} cần video broll/{c.get('video')} chưa tải")
    return msgs


NHAN_MAX_TU = 5  # nhãn dạng viên (pill) ≤ 5 từ; dòng dưới của so-lon là câu ngắn nên không tính


def _nhan_pills(c: dict) -> list[str]:
    if c["mau"] == "minh-hoa":
        return [c["nhan"]] if c.get("nhan") else []
    if c["mau"] == "so-sanh":
        return [c[k]["nhan"] for k in ("trai", "phai") if isinstance(c.get(k), dict) and c[k].get("nhan")]
    if c["mau"] == "quy-trinh":
        return [b["nhan"] for b in c.get("buoc") or [] if b.get("nhan")]
    return []


def _check_quy_trinh(c: dict, svg_dir: Path) -> list[str]:
    buoc, out = c.get("buoc") or [], []
    if not 3 <= len(buoc) <= 6:
        out.append(f"Lỗi: {c['id']} quy-trinh cần 3–6 bước (đang {len(buoc)})")
    nb = c.get("noi_bat")
    if nb is not None and not (isinstance(nb, int) and 0 <= nb < len(buoc)):
        out.append(f"Lỗi: {c['id']} noi_bat={nb} nằm ngoài các bước")
    out += [f"Lỗi: {c['id']} bước '{b.get('nhan')}' cần hình {b['svg']}.svg chưa có trong thư viện"
            for b in buoc if b.get("svg") and not (Path(svg_dir) / f"{b['svg']}.svg").exists()]
    return out


def _check_dan(c: dict, words: list[dict]) -> list[str]:
    d = c["dan"]
    if not isinstance(d, dict) or d.get("the") not in DAN_THE or d.get("goc", "phai") not in DAN_GOC:
        return [f"Lỗi: {c['id']} dan phải là {{the: {'|'.join(sorted(DAN_THE))}, goc?: phai|trai, tu?: cụm}}"]
    if d.get("tu") and phrase_time(words, d["tu"], c["start"], c["end"]) is None:
        return [f"Lỗi: {c['id']} dan.tu '{d['tu']}' nhưng giọng đọc không nói cụm này trong cảnh"]
    return []


def _check_thoi_gian(c: dict) -> list[str]:
    hang, truc, out = c.get("hang") or [], c.get("truc") or {}, []
    if not 2 <= len(hang) <= 5:
        out.append(f"Lỗi: {c['id']} thoi-gian cần 2–5 hàng (đang {len(hang)})")
    lo, hi = truc.get("tu"), truc.get("den")
    if lo is None or hi is None or not lo < hi:
        return out + [f"Lỗi: {c['id']} thoi-gian cần truc có tu < den (trục {lo}–{hi})"]
    for h in hang:
        if not isinstance(h.get("tu"), (int, float)) or not isinstance(h.get("den"), (int, float)) or not h["tu"] < h["den"]:
            out.append(f"Lỗi: {c['id']} hàng '{h.get('nhan')}' cần tu < den ({h.get('tu')}–{h.get('den')})")
        elif h["tu"] < lo or h["den"] > hi:
            out.append(f"Lỗi: {c['id']} hàng '{h.get('nhan')}' {h['tu']}–{h['den']} nằm ngoài trục {lo}–{hi}")
    return out


def _check_so_sanh(c: dict, svg_dir: Path) -> list[str]:
    out = []
    for ben in ("trai", "phai"):
        s = c.get(ben)
        if not isinstance(s, dict) or not s.get("nhan"):
            out.append(f"Lỗi: {c['id']} so-sanh thiếu {ben} (cần nhan và svg)")
            continue
        to = s.get("to", 1.0)
        if not isinstance(to, (int, float)) or not 0 < to <= 1:
            out.append(f"Lỗi: {c['id']} {ben}.to={to} phải trong (0, 1]")
        if not s.get("svg") or not (Path(svg_dir) / f"{s['svg']}.svg").exists():
            out.append(f"Lỗi: {c['id']} {ben} cần hình {s.get('svg')}.svg chưa có trong thư viện")
    return out


def _check_quote(c: dict, src: dict | None) -> list[str]:
    """Trích báo phải là nguyên văn một đoạn trong trich_dan của nguồn; phần tô vàng nằm trong đoạn trích."""
    if not src:
        return [f"Lỗi: {c['id']} trích báo thiếu nguon_id hợp lệ"]
    out = []
    trich = c.get("trich", "")
    if not trich or _norm(trich) not in _norm(src.get("trich_dan", "")):
        out.append(f"Lỗi: {c['id']} trích không đúng nguyên văn nguồn [#{src['id']}]")
    if c.get("to_vang") and _norm(c["to_vang"]) not in _norm(trich):
        out.append(f"Lỗi: {c['id']} cụm tô vàng không nằm trong đoạn trích")
    if len(trich.split()) > 25:
        out.append(f"Lỗi: {c['id']} đoạn trích dài quá 25 từ")
    return out


def _unit_scale(text: str) -> str:
    m = NUM.search("1 " + (text or "").strip())
    return _scale(m.group(2)) if m else ""


def _check_values(c: dict, srcs: list[dict], has_ref: bool) -> list[str]:
    """Số hiện trên màn hình (so-lon, bieu-do, so-sanh, thoi-gian) phải có nguồn và khớp giá trị + quy mô trong nguồn."""
    if c["mau"] == "so-lon" and "so" in c:
        pairs = [(c["so"], _unit_scale(c.get("truoc", "") + " " + c.get("sau", "")))]
    elif c["mau"] == "bieu-do" and c.get("bieu_do"):
        scale = _unit_scale(c["bieu_do"].get("don_vi", ""))
        pairs = [(v, scale) for v in c["bieu_do"]["gia_tri"]]
    elif c["mau"] == "thoi-gian":  # năm trên các thanh là số hiện trên màn hình; vạch trục chỉ là thang đo
        pairs = [(h[k], "") for h in c.get("hang") or [] for k in ("tu", "den") if isinstance(h.get(k), (int, float))]
        if not pairs:
            return []
    elif c["mau"] == "so-sanh":  # mỗi bên có thể có đơn vị riêng ("tỷ transistor" so với "triệu transistor")
        pairs = [(s["so"], _unit_scale(s.get("don_vi", c.get("don_vi", ""))))
                 for s in (c.get("trai"), c.get("phai")) if isinstance(s, dict) and s.get("so") is not None]
        if not pairs:
            return []
    else:
        return []
    if not has_ref:
        return [f"Lỗi: {c['id']} hiện số nhưng thiếu nguon_id"]
    allowed = {(v, sc) for s in srcs for _, v, sc in tokens(s["gia_tri"])}
    out = []
    for v, scale in pairs:
        num = vi_value(v) if isinstance(v, str) else float(v)
        if (num, scale) not in allowed:
            out.append(f"Lỗi: {c['id']} hiện {v}{' ' + scale if scale else ''} không khớp nguồn "
                       f"{[s['id'] for s in srcs]}")
    return out


def _ts(t: float) -> str:
    ms = round(t * 1000)
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def cues(timing: dict, max_chars: int = 42) -> list[tuple[float, float, str]]:
    """Gom từ thành dòng phụ đề ≤ max_chars (trừ một từ dài hơn nó), ngắt theo nghĩa: bắt buộc sau .!?, ưu tiên sau , ; :
    khi dòng đã ≥ 60% max_chars, và khi buộc ngắt vì vượt max_chars thì lùi về dấu , ; : gần nhất nếu vế đầu ≥ 40% max_chars; không để một từ
    đứng riêng một dòng giữa câu."""
    text = lambda ws: " ".join(x["w"] for x in ws)
    ket_cau = lambda w: w["w"][-1:] in ".!?"
    groups, cur = [], []
    for w in timing["words"]:
        if cur and len(text(cur + [w])) > max_chars:
            k = max((i for i in range(1, len(cur)) if cur[i - 1]["w"][-1:] in ",;:" and len(text(cur[:i])) >= 0.4 * max_chars),
                    default=0)  # chỉ lùi về dấu phẩy khi vế đầu đủ dài, tránh dòng vài từ chớp lên rồi mất
            groups.append(cur[:k] if k else cur)
            cur = cur[k:] if k else []
        cur.append(w)
        if ket_cau(w) or (w["w"][-1:] in ",;:" and len(text(cur)) >= 0.6 * max_chars):
            groups.append(cur)
            cur = []
    if cur:
        groups.append(cur)
    i = 1
    while i < len(groups):  # nhóm một từ khi câu chưa kết: mượn từ cuối của nhóm trước, hoặc gộp vào nhóm trước
        g, prev = groups[i], groups[i - 1]
        if len(g) == 1 and not ket_cau(prev[-1]):
            if len(prev) >= 3 and len(text([prev[-1], *g])) <= max_chars:
                groups[i], groups[i - 1] = [prev[-1], *g], prev[:-1]
            elif len(text(prev + g)) <= max_chars:
                groups[i - 1:i + 1] = [prev + g]
                continue
        i += 1
    return [(g[0]["start"], g[-1]["end"], text(g)) for g in groups]


def to_srt(timing: dict, max_chars: int = 42) -> str:
    return "".join(f"{i}\n{_ts(a)} --> {_ts(b)}\n{t}\n\n" for i, (a, b, t) in enumerate(cues(timing, max_chars), 1))


def main(video_dir: str) -> int:
    d = Path(video_dir)
    timing = json.loads((d / "giong-timing.json").read_text(encoding="utf-8"))
    nguon = json.loads((d / "nguon.json").read_text(encoding="utf-8")) if (d / "nguon.json").exists() else []
    msgs = validate(json.loads((d / "canh.json").read_text(encoding="utf-8")), timing, SVG_DIR, nguon)
    for m in msgs:
        print("-", m)
    (d / "phu-de.srt").write_text(to_srt(timing), encoding="utf-8")
    errs = [m for m in msgs if m.startswith("Lỗi")]
    print(f"{len(errs)} lỗi, {len(msgs) - len(errs)} cảnh báo; đã ghi phu-de.srt")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
