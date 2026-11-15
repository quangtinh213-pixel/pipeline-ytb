"""Kiểm canh.json theo timestamp giọng đọc và xuất phụ đề SRT."""
import json
import re
import sys
import unicodedata
from pathlib import Path

from tttc import ban_do as _ban_do, ngon_ngu, nhan_vat
from tttc.kiem import NUM, _scale, tokens, vi_value

MAU = {"minh-hoa", "bieu-do", "so-lon", "nhan-vat", "trang-nguon", "chuong", "trich-bao", "b-roll", "quy-trinh", "so-sanh", "thoi-gian", "ban-do", "xep-hang",
       "chu-dong", "phan-tram", "mo-dau", "ket-thuc"}
# Mẫu cảnh dọc 1080×1920 của Short viết riêng (templates/canh-doc); chỉ hợp lệ khi canh.json có "khuon": "doc"
MAU_DOC = {"moc", "bang-chung", "anh", "doi-chieu", "ket"}
MOC_MAX_TU, SO_MAX_KY_TU = 8, 12  # chữ hook và chuỗi số phải vừa bề rộng 1080 px (tom_tat: _check_boi đã giới hạn)
SVG_DIR = Path(__file__).resolve().parent.parent / "svg"
TOL = 0.5      # lệch cho phép giữa hình và tiếng (giây)
EPS = 0.01     # sai số làm tròn giữa hai cảnh liền nhau
CANH_MIN_LOI, CANH_MAX_LOI = 1.5, 10.0   # ngoài khoảng này là lỗi
DAN_GOC = {"phai", "trai"}  # góc màn hình của nhân vật dẫn chuyện (bộ nhân vật: pipeline/nhan-vat/kit.json)
MAY_QUAY = {"", "dung", "day-vao", "keo-ra", "lia", "he-lo", "punch-in", "lac"}  # camera áp lên "thế giới" của cảnh minh-hoa
DONG = {"", "bob", "xoay", "dap", "chop", "tilt", "tho"}  # chuyển động lặp trong cảnh (templates/canh/dong.js)
CANH_MIN_CB, CANH_MAX_CB = 2.5, 6.0      # ngoài khoảng này là cảnh báo (chuẩn kênh mẫu: 2,5–4 s/cảnh)
# user chốt 14/11/2026 (nghiên cứu đối thủ mục 6, P0): sau 60 s được giữ một sân khấu đồ họa tới 35 s
# (tttc.chat_luong đo độ dày bồi dần); b-roll giữ trần cũ vì clip kho ≤ 20 s và mỗi cảnh một clip
SAN_KHAU_TU, SAN_KHAU_MAX = 60.0, 35.0
MO_SOM = 45.0  # logo kênh / thẻ chương trước mốc này cắt ngang móc câu


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


DOC_KIT = object()  # mặc định: đọc nhan-vat/kit.json; truyền None để ép luật nhân vật SVG cũ


def validate(scenes: dict, timing: dict, svg_dir: Path = SVG_DIR, nguon: list | tuple = (),
             video_dir: Path | None = None, kit=DOC_KIT, goc: Path | None = None) -> list[str]:
    """Trả danh sách 'Lỗi: ...' (phải sửa) và 'Cảnh báo: ...' (nên xem).
    goc: thư mục chứa anh/, broll/, nguon/ (thư mục video cha của một Short); không truyền thì dùng video_dir."""
    goc = Path(goc) if goc is not None else (Path(video_dir) if video_dir is not None else None)
    doc = scenes.get("khuon") == "doc"
    kit = nhan_vat.doc_kit() if kit is DOC_KIT else kit
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
        if not doc and c["mau"] in MAU_DOC:
            msgs.append(f"Lỗi: {cid} mẫu dọc {c['mau']} chỉ dùng cho Short (canh.json cần \"khuon\": \"doc\")")
        elif c["mau"] not in (MAU_DOC if doc else MAU):
            msgs.append(f"Lỗi: {cid} dùng mẫu không có: {c['mau']}"
                        + (f" (Short dọc gốc chỉ dùng {', '.join(sorted(MAU_DOC))})" if doc else ""))
        elif doc:
            msgs += _check_doc(c, goc)
        if c.get("dan") is not None:
            msgs += _check_dan(c, timing.get("words", []), kit)
        msgs += [f"Lỗi: {cid} {k} có vẻ là tiếng Anh: «{t}»; mọi chữ trên màn hình phải là tiếng Việt"
                 for k, t in ngon_ngu.man_hinh(c) if ngon_ngu.la_tieng_anh(t)]
        if c.get("dong", "") not in DONG:
            msgs.append(f"Lỗi: {cid} dong không hợp lệ: {c['dong']} (chọn {', '.join(sorted(DONG - {''}))})")
        san_khau = c["start"] >= SAN_KHAU_TU and c["mau"] != "b-roll"
        tran = SAN_KHAU_MAX if san_khau else CANH_MAX_LOI
        if dur < CANH_MIN_LOI or dur > tran:
            msgs.append(f"Lỗi: {cid} dài {dur:.1f} s (cho phép {CANH_MIN_LOI:g}–{tran:g} s)")
        elif dur < CANH_MIN_CB or (dur > CANH_MAX_CB and not san_khau):
            msgs.append(f"Cảnh báo: {cid} dài {dur:.1f} s (nên {CANH_MIN_CB:g}–{CANH_MAX_CB:g} s)")
        elif c["start"] < 30.0 and dur > 3.5:
            msgs.append(f"Cảnh báo: {cid} trong 30s đầu dài {dur:.1f} s (nên ≤ 3,5 s để giữ chân người xem)")
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
        if c["mau"] == "minh-hoa":
            msgs += _check_minh_hoa(c, svg_dir)
        if c["mau"] == "quy-trinh":
            msgs += _check_quy_trinh(c, svg_dir)
        if c["mau"] == "so-sanh":
            msgs += _check_so_sanh(c, svg_dir)
        if c["mau"] == "ban-do":
            msgs += _check_ban_do(c)
        if c["mau"] == "xep-hang":
            msgs += _check_xep_hang(c)
        if c["mau"] == "thoi-gian":
            msgs += _check_thoi_gian(c)
        if c["mau"] in ("mo-dau", "chuong") and 0 < c["start"] < MO_SOM:
            msgs.append(f"Cảnh báo: {cid} {c['mau']} ở giây {c['start']:.0f}: logo kênh và thẻ chương đặt từ giây "
                        f"{MO_SOM:g} trở đi, 30 s đầu chỉ dùng số lớn, ảnh bằng chứng, sa bàn và câu hỏi móc")
        if c["mau"] in ("chu-dong", "phan-tram", "mo-dau", "ket-thuc"):
            msgs += _check_mau_moi(c, dur, sc)
        msgs += _check_boi(c, timing.get("words", []), svg_dir, by_id)
        if c["mau"] == "trich-bao" and c.get("cac") is not None:
            msgs += _check_cac(c, by_id)
        elif c["mau"] == "trich-bao":
            msgs += _check_quote(c, by_id.get(c.get("nguon_id")))
        if c["mau"] == "b-roll" and video_dir is not None and not (Path(video_dir) / "broll" / c.get("video", "")).is_file():
            msgs.append(f"Lỗi: {cid} cần video broll/{c.get('video')} chưa tải")
    return msgs


def _trong_01(v, n: int) -> bool:
    return isinstance(v, (list, tuple)) and len(v) == n and all(isinstance(x, (int, float)) and 0 <= x <= 1 for x in v)


def _check_doc(c: dict, goc: Path | None) -> list[str]:
    """Trường bắt buộc và giới hạn chữ của một cảnh dùng mẫu dọc; tệp ảnh/video phải có trong thư mục cha (goc)."""
    cid, mau, out = c["id"], c["mau"], []
    chuoi = lambda v: isinstance(v, str) and bool(v.strip())
    thieu_tep = lambda rel: goc is not None and not (goc / rel).is_file()
    # compose chỉ chép anh/, nguon/, broll/ của thư mục video vào composition; ảnh ở chỗ khác render ra khung trống
    ngoai_kho = lambda rel: Path(rel).parts[:1] not in (("anh",), ("nguon",), ("broll",))
    if mau in ("moc", "ket"):
        if not chuoi(c.get("chu")):
            out.append(f"Lỗi: {cid} {mau} thiếu chu")
        elif mau == "moc" and len(c["chu"].split()) > MOC_MAX_TU:
            out.append(f"Cảnh báo: {cid} chu dài {len(c['chu'].split())} từ (≤ {MOC_MAX_TU} từ để đọc được trong một giây)")
        if chuoi(c.get("so")) and len(c["so"].strip()) > SO_MAX_KY_TU:
            out.append(f"Cảnh báo: {cid} so «{c['so']}» dài hơn {SO_MAX_KY_TU} ký tự, dễ tràn khung 1080 px")
    elif mau == "bang-chung":
        if not chuoi(c.get("anh")):
            out.append(f"Lỗi: {cid} bang-chung thiếu anh")
        elif ngoai_kho(c["anh"]):
            out.append(f"Lỗi: {cid} anh «{c['anh']}» phải nằm trong anh/, nguon/ hoặc broll/ của thư mục video")
        elif thieu_tep(c["anh"]):
            out.append(f"Lỗi: {cid} cần ảnh {c['anh']} chưa có trong {goc}")
        v = c.get("vung")
        if not _trong_01(v, 4) or v[2] <= 0 or v[3] <= 0 or v[0] + v[2] > 1 + EPS or v[1] + v[3] > 1 + EPS:
            out.append(f"Lỗi: {cid} vung phải là [x, y, w, h] trong 0–1 và nằm trọn trong ảnh, đang là {v}")
        if not chuoi(c.get("tom_tat")):
            out.append(f"Lỗi: {cid} bang-chung thiếu tom_tat (một dòng tiếng Việt dưới bằng chứng)")
        if not c.get("nguon_id"):
            out.append(f"Lỗi: {cid} bang-chung thiếu nguon_id")
    elif mau == "anh":
        if chuoi(c.get("anh")) == chuoi(c.get("video")):
            out.append(f"Lỗi: {cid} mẫu anh cần đúng một trong anh / video")
        elif chuoi(c.get("anh")) and ngoai_kho(c["anh"]):
            out.append(f"Lỗi: {cid} anh «{c['anh']}» phải nằm trong anh/, nguon/ hoặc broll/ của thư mục video")
        elif chuoi(c.get("anh")) and thieu_tep(c["anh"]):
            out.append(f"Lỗi: {cid} cần ảnh {c['anh']} chưa có trong {goc}")
        elif chuoi(c.get("video")) and thieu_tep(Path("broll") / c["video"]):
            out.append(f"Lỗi: {cid} cần video broll/{c['video']} chưa tải")
        if c.get("diem_giu") is not None and not _trong_01(c["diem_giu"], 2):
            out.append(f"Lỗi: {cid} diem_giu phải là [x, y] trong 0–1, đang là {c['diem_giu']}")
    elif mau == "doi-chieu":
        for ve in ("tren", "duoi"):
            x = c.get(ve)
            if not (isinstance(x, dict) and chuoi(x.get("nhan")) and chuoi(x.get("so"))):
                out.append(f"Lỗi: {cid} doi-chieu thiếu vế {ve} (cần nhan và so)")
        if c.get("noi_bat") not in (None, "", "tren", "duoi"):
            out.append(f"Lỗi: {cid} noi_bat phải là tren hoặc duoi, đang là {c['noi_bat']}")
    return out


NHAN_MAX_TU = 5  # nhãn dạng viên (pill) ≤ 5 từ; dòng dưới của so-lon là câu ngắn nên không tính


def _nhan_pills(c: dict) -> list[str]:
    if c["mau"] == "minh-hoa":
        return [c["nhan"]] if c.get("nhan") else []
    if c["mau"] == "so-sanh":
        return [c[k]["nhan"] for k in ("trai", "phai") if isinstance(c.get(k), dict) and c[k].get("nhan")]
    if c["mau"] == "quy-trinh":
        return [b["nhan"] for b in c.get("buoc") or [] if b.get("nhan")]
    if c["mau"] == "xep-hang":
        return [h["nhan"] for h in c.get("hang") or [] if isinstance(h, dict) and h.get("nhan")]
    if c["mau"] == "ban-do":
        return [x["nhan"] for k in ("diem", "noi") for x in c.get(k) or [] if isinstance(x, dict) and x.get("nhan")]
    return []


def san_khau_hop_le(svg_dir: Path = SVG_DIR) -> set[str]:
    """Phông hợp lệ: nen-dat cùng phần sau `san-khau-` của mọi tệp san-khau-*.svg (thêm phông = thêm tệp SVG)."""
    return {"nen-dat"} | {f.stem.removeprefix("san-khau-") for f in Path(svg_dir).glob("san-khau-*.svg")}


def _check_minh_hoa(c: dict, svg_dir: Path) -> list[str]:
    cid, out = c["id"], []
    if c.get("san_khau", "nen-dat") not in san_khau_hop_le(svg_dir):
        out.append(f"Lỗi: {cid} san_khau '{c['san_khau']}' không có (chọn {', '.join(sorted(san_khau_hop_le(svg_dir)))})")
    if c.get("may_quay", "") not in MAY_QUAY:
        out.append(f"Lỗi: {cid} may_quay '{c['may_quay']}' không hợp lệ (chọn {', '.join(sorted(MAY_QUAY - {''}))})")
    bc = c.get("bo_cuc")
    if bc is not None:
        if c.get("phu"):
            out.append(f"Lỗi: {cid} không dùng cùng lúc phu và bo_cuc")
        if not isinstance(bc, list) or not 1 <= len(bc) <= 4:
            out.append(f"Lỗi: {cid} bo_cuc cần 1–4 đạo cụ")
        else:
            for b in bc:
                ok = (isinstance(b, dict) and 0 <= b.get("x", -1) <= 1 and 0 <= b.get("y", -1) <= 1
                      and 0.2 <= b.get("to", 1.0) <= 1.5 and (Path(svg_dir) / f"{b.get('svg')}.svg").exists())
                if not ok:
                    out.append(f"Lỗi: {cid} bo_cuc có đạo cụ sai: {b} (cần svg có trong thư viện, x và y trong 0–1, to trong 0,2–1,5)")
    return out


def _check_mau_moi(c: dict, dur: float, sc: list[dict]) -> list[str]:
    cid, m, out = c["id"], c["mau"], []
    if m == "chu-dong":
        cau = (c.get("cau") or "").split()
        if not cau:
            out.append(f"Lỗi: {cid} chu-dong cần cau")
        elif len(cau) > 16:
            out.append(f"Lỗi: {cid} cau dài {len(cau)} từ (≤ 16)")
        if c.get("nhan_tu") and _norm(c["nhan_tu"]) not in _norm(c.get("cau", "")):
            out.append(f"Lỗi: {cid} nhan_tu «{c['nhan_tu']}» không nằm trong cau")
    if m == "phan-tram":
        try:
            v = vi_value(c["so"]) if isinstance(c.get("so"), str) else float(c["so"])
        except (KeyError, TypeError, ValueError):
            v = None
        if v is None or not 0 <= v <= 100:
            out.append(f"Lỗi: {cid} phan-tram cần so trong 0–100 (đang {c.get('so')})")
    if m == "mo-dau" and c is sc[0]:
        out.append(f"Cảnh báo: {cid} mo-dau ở giây 0 làm mất móc câu; đặt sau đoạn mở đầu")
    if m == "ket-thuc":
        if c is not sc[-1]:
            out.append(f"Lỗi: {cid} ket-thuc phải là cảnh cuối")
        if dur < 5:
            out.append(f"Cảnh báo: {cid} ket-thuc dài {dur:.1f} s; màn hình kết thúc của YouTube cần ≥ 5 s")
    return out


def _check_xep_hang(c: dict) -> list[str]:
    """Thanh xếp hạng: 2–8 hàng có nhãn và số (số được _check_values đối chiếu nguồn), noi_bat là chỉ số hàng."""
    hang, out = c.get("hang") or [], []
    if not 2 <= len(hang) <= 8:
        out.append(f"Lỗi: {c['id']} xep-hang cần 2–8 hàng (đang {len(hang)})")
    moc = c.get("moc") or []
    if moc and not (2 <= len(moc) <= 10 and all(isinstance(m, str) and m for m in moc)):
        out.append(f"Lỗi: {c['id']} moc cần 2–10 nhãn năm/mốc dạng chữ (đang {len(moc)})")
    for i, h in enumerate(hang):
        so = h.get("so") if isinstance(h, dict) else None
        ok_one = lambda x: isinstance(x, (int, float, str)) and not isinstance(x, bool)
        if not isinstance(h, dict) or not h.get("nhan") or not (ok_one(so) and not moc or isinstance(so, list) and moc and all(ok_one(x) for x in so)):
            out.append(f"Lỗi: {c['id']} hàng {i} cần nhan và so" + (" (một số cho mỗi mốc trong moc)" if moc else ""))
        elif moc and len(so) != len(moc):
            out.append(f"Lỗi: {c['id']} hàng {i} có {len(so)} giá trị nhưng moc có {len(moc)} mốc")
    nb = c.get("noi_bat")
    if nb is not None and not (isinstance(nb, int) and not isinstance(nb, bool) and 0 <= nb < len(hang)):
        out.append(f"Lỗi: {c['id']} noi_bat={nb} nằm ngoài các hàng")
    return out


def _check_ban_do(c: dict) -> list[str]:
    """Sơ đồ vị trí: 2–6 điểm có toạ độ hợp lệ, các mũi tên nối đúng chỉ số điểm."""
    diem, noi, out = c.get("diem") or [], c.get("noi") or [], []
    if not 2 <= len(diem) <= 6:
        out.append(f"Lỗi: {c['id']} ban-do cần 2–6 điểm (đang {len(diem)})")
    for i, d in enumerate(diem):
        if not isinstance(d, dict) or not d.get("nhan"):
            out.append(f"Lỗi: {c['id']} điểm {i} thiếu nhan")
            continue
        ma = d.get("nuoc")
        if ma and (data := _ban_do.doc()) is not None and ma not in data["nuoc"]:
            out.append(f"Lỗi: {c['id']} điểm '{d['nhan']}' nuoc '{ma}' không có trong dữ liệu bản đồ (mã ADM0_A3, ví dụ VNM, USA)")
        for k, lim in (("vi_do", 90), ("kinh_do", 180)):
            v = d.get(k)
            if not isinstance(v, (int, float)) or isinstance(v, bool) or not -lim <= v <= lim:
                out.append(f"Lỗi: {c['id']} điểm '{d['nhan']}' {k} phải là số trong khoảng ±{lim}")
    for j, e in enumerate(noi):
        ok = isinstance(e, dict) and all(isinstance(e.get(k), int) and 0 <= e[k] < len(diem) for k in ("tu", "den"))
        if not ok or e["tu"] == e["den"]:
            out.append(f"Lỗi: {c['id']} noi[{j}] phải nối hai điểm khác nhau theo chỉ số 0–{max(len(diem) - 1, 0)}")
    return out


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


def _check_dan(c: dict, words: list[dict], kit: dict | None = None) -> list[str]:
    d = c["dan"]
    if not kit:
        return [f"Lỗi: {c['id']} có dan nhưng chưa có bộ nhân vật (pipeline/nhan-vat/kit.json)"]
    the_ok = kit["the"]
    if not isinstance(d, dict) or d.get("the") not in the_ok or d.get("goc", "phai") not in DAN_GOC:
        return [f"Lỗi: {c['id']} dan phải là {{the: {'|'.join(sorted(the_ok))}, goc?: phai|trai, huong?, tu?: cụm}}"]
    huong = d.get("huong") or nhan_vat.huong_mac_dinh(d.get("goc", "phai"))
    if not nhan_vat.hop_le(d["the"], huong, kit):
        return [f"Lỗi: {c['id']} dan {d['the']} không có huong '{huong}' trong bộ nhân vật (kit.json:dang)"]
    if d.get("lau") is not None and not (isinstance(d["lau"], (int, float)) and 0.8 <= d["lau"] <= 6):
        return [f"Lỗi: {c['id']} dan.lau phải là số giây 0,8–6"]
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


BOI_MAX, TOM_TAT_MAX_TU, THE_MAX_TU = 6, 14, 6
KIEU_NHAN, MUI_TEN, TONG = {"nhan", "vang", "do", "trang"}, {"trai", "phai", "len", "xuong"}, {"hook", "khai-niem", "ky-thuat", "viet-nam"}


def _so_chu(cid: str, ten: str, text: str, srcs: list[dict]) -> list[str]:
    """Số trong chữ tự do hiện trên màn hình (nhãn bồi dần, tóm tắt) phải khớp giá trị trong nguồn của cảnh."""
    so = tokens(text, keep_small=False)
    if not so:
        return []
    if not srcs:
        return [f"Lỗi: {cid} {ten} hiện số nhưng cảnh thiếu nguon_id"]
    allowed = {(v, sc) for s in srcs for _, v, sc in tokens(s["gia_tri"])}
    return [f"Lỗi: {cid} {ten} hiện {raw}{' ' + sc if sc else ''} không khớp nguồn {[s['id'] for s in srcs]}"
            for raw, v, sc in so if (v, sc) not in allowed]


def _check_boi(c: dict, words: list[dict], svg_dir: Path, by_id: dict) -> list[str]:
    """Nhãn bồi dần (boi), thanh tóm tắt (tom_tat), tông chương (tong), viền/phóng trang nguồn."""
    cid, out = c["id"], []
    nid = c.get("nguon_id")
    srcs = [by_id[n] for n in (nid if isinstance(nid, list) else [nid] if nid else []) if n in by_id]
    boi = c.get("boi") or []
    if len(boi) > BOI_MAX:
        out.append(f"Lỗi: {cid} có {len(boi)} nhãn bồi dần (tối đa {BOI_MAX})")
    for k, b in enumerate(boi):
        ten = f"boi[{k}]"
        if not b.get("chu") and not b.get("svg"):
            out.append(f"Lỗi: {cid} {ten} cần chu hoặc svg")
        if b.get("chu") and len(b["chu"].split()) > NHAN_MAX_TU:
            out.append(f"Lỗi: {cid} {ten} dài {len(b['chu'].split())} từ (≤ {NHAN_MAX_TU})")
        if b.get("svg") and not (Path(svg_dir) / f"{b['svg']}.svg").exists():
            out.append(f"Lỗi: {cid} {ten} cần hình {b['svg']}.svg chưa có trong thư viện")
        if b.get("kieu", "nhan") not in KIEU_NHAN:
            out.append(f"Lỗi: {cid} {ten} kieu {b['kieu']} (chọn {', '.join(sorted(KIEU_NHAN))})")
        if b.get("mui_ten") and b["mui_ten"] not in MUI_TEN:
            out.append(f"Lỗi: {cid} {ten} mui_ten {b['mui_ten']} (chọn {', '.join(sorted(MUI_TEN))})")
        if not all(isinstance(b.get(a), (int, float)) and 0 <= b[a] <= 1 for a in ("x", "y")):
            out.append(f"Lỗi: {cid} {ten} cần x, y trong 0–1")
        if b.get("tu") and phrase_time(words, b["tu"], c["start"], c["end"]) is None:
            out.append(f"Lỗi: {cid} {ten} bật theo '{b['tu']}' nhưng giọng đọc không nói cụm này trong cảnh")
        out += _so_chu(cid, ten, b.get("chu") or "", srcs)
    if c.get("tom_tat"):
        if len(c["tom_tat"].split()) > TOM_TAT_MAX_TU:
            out.append(f"Lỗi: {cid} tom_tat dài {len(c['tom_tat'].split())} từ (≤ {TOM_TAT_MAX_TU}, một dòng)")
        out += _so_chu(cid, "tom_tat", c["tom_tat"], srcs)
    if c.get("tong") and c["tong"] not in TONG:
        out.append(f"Lỗi: {cid} tong {c['tong']} (chọn {', '.join(sorted(TONG))})")
    if c.get("vien") and c["vien"] not in KIEU_NHAN - {"trang"}:
        out.append(f"Lỗi: {cid} vien {c['vien']} (chọn nhan, vang, do)")
    if c.get("zoom") is not None and not (isinstance(c["zoom"], (int, float)) and 1.5 <= c["zoom"] <= 4):
        out.append(f"Lỗi: {cid} zoom {c['zoom']} (1,5–4)")
    return out


def _check_cac(c: dict, by_id: dict) -> list[str]:
    """Trích báo nhiều nguồn: 2–3 thẻ, mỗi thẻ một nguồn có thật và tóm tắt ngắn; số trong tóm tắt khớp nguồn của thẻ."""
    cid, cac, out = c["id"], c["cac"], []
    if not isinstance(cac, list) or not 2 <= len(cac) <= 3:
        return [f"Lỗi: {cid} cac cần 2–3 thẻ nguồn"]
    for k, x in enumerate(cac):
        src = by_id.get(x.get("nguon_id"))
        if not src:
            out.append(f"Lỗi: {cid} cac[{k}] thiếu nguon_id hợp lệ")
        tt = x.get("tom_tat") or ""
        if not tt or len(tt.split()) > THE_MAX_TU:
            out.append(f"Lỗi: {cid} cac[{k}].tom_tat cần 1–{THE_MAX_TU} từ")
        out += _so_chu(cid, f"cac[{k}].tom_tat", tt, [src] if src else [])
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
    tv = c.get("trich_vi", "")
    if not tv and ngon_ngu.la_tieng_anh(trich, toi_thieu=2):  # câu trích là cả câu, không phải nhãn tên riêng
        out.append(f"Lỗi: {c['id']} trích bằng tiếng Anh: thêm trich_vi (bản dịch tiếng Việt của kênh) và to_vang_vi để hiện lên màn hình")
    if tv and c.get("to_vang_vi") and _norm(c["to_vang_vi"]) not in _norm(tv):
        out.append(f"Lỗi: {c['id']} to_vang_vi không nằm trong trich_vi")
    return out


def _unit_scale(text: str) -> str:
    m = NUM.search("1 " + (text or "").strip())
    return _scale(m.group(2)) if m else ""


def _check_values(c: dict, srcs: list[dict], has_ref: bool) -> list[str]:
    """Số hiện trên màn hình (so-lon, bieu-do, so-sanh, thoi-gian) phải có nguồn và khớp giá trị + quy mô trong nguồn."""
    if c["mau"] == "so-lon" and "so" in c:
        sc = _unit_scale(c.get("truoc", "") + " " + c.get("sau", ""))
        pairs = [(c["so"], sc)] + ([(c["tu"], sc)] if c.get("tu") is not None else [])  # tu = giá trị cũ để đếm từ đó lên
    elif c["mau"] == "bieu-do" and c.get("bieu_do"):
        scale = _unit_scale(c["bieu_do"].get("don_vi", ""))
        pairs = [(v, scale) for v in c["bieu_do"]["gia_tri"]]
    elif c["mau"] == "thoi-gian":  # năm trên các thanh là số hiện trên màn hình; vạch trục chỉ là thang đo
        pairs = [(h[k], "") for h in c.get("hang") or [] for k in ("tu", "den") if isinstance(h.get(k), (int, float))]
        if not pairs:
            return []
    elif c["mau"] == "phan-tram" and "so" in c:
        pairs = [(c["so"], _unit_scale(c.get("sau", "%")))]
    elif c["mau"] == "xep-hang":
        sc = _unit_scale(c.get("don_vi", ""))
        pairs = [(x, sc) for h in c.get("hang") or [] if isinstance(h, dict) and h.get("so") is not None
                 for x in (h["so"] if isinstance(h["so"], list) else [h["so"]])]
        if not pairs:
            return []
    elif c["mau"] == "so-sanh":  # mỗi bên có thể có đơn vị riêng ("tỷ transistor" so với "triệu transistor")
        pairs = [(s["so"], _unit_scale(s.get("don_vi", c.get("don_vi", ""))))
                 for s in (c.get("trai"), c.get("phai")) if isinstance(s, dict) and s.get("so") is not None]
        if not pairs:
            return []
    elif c["mau"] == "b-roll":  # số trong từ khoá bật lên hoặc nửa phải của khung chia đôi
        ch = c.get("chia") if isinstance(c.get("chia"), dict) else {}
        pairs = [(raw, sc) for raw, _, sc in tokens(c.get("tu_khoa") or "")]
        if ch.get("so") is not None:
            pairs.append((ch["so"], _unit_scale(ch.get("truoc", "") + " " + ch.get("sau", ""))))
        if not pairs:
            return []
    elif c["mau"] in MAU_DOC:  # mẫu dọc ghi số dạng chuỗi hiển thị ("15,89 triệu"): tách số và quy mô như lời đọc
        chuoi = [c.get("so")] if c["mau"] in ("moc", "ket") else             [(c.get(ve) or {}).get("so") for ve in ("tren", "duoi") if isinstance(c.get(ve), dict)] if c["mau"] == "doi-chieu" else []
        pairs = [(raw, sc) for t in chuoi if isinstance(t, str) for raw, _, sc in tokens(t)]
        if not pairs:
            return []
    else:
        return []
    if not has_ref:
        return [f"Lỗi: {c['id']} hiện số nhưng thiếu nguon_id"]
    allowed = {(v, sc) for s in srcs for _, v, sc in tokens(s["gia_tri"])}
    out = []
    for v, scale in pairs:
        try:
            num = vi_value(v) if isinstance(v, str) else float(v)
        except ValueError:
            out.append(f"Lỗi: {c['id']} hiện «{v}» không phải số; ngày tháng và chữ dùng mẫu minh-hoa hay chuong")
            continue
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
    text = lambda ws: " ".join(x["w"] for x in ws)
    return [(g[0]["start"], g[-1]["end"], text(g)) for g in nhom_tu(timing, max_chars)]


def nhom_tu(timing: dict, max_chars: int = 42) -> list[list[dict]]:
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
    return groups


def to_srt(timing: dict, max_chars: int = 42) -> str:
    return "".join(f"{i}\n{_ts(a)} --> {_ts(b)}\n{t}\n\n" for i, (a, b, t) in enumerate(cues(timing, max_chars), 1))


def main(video_dir: str) -> int:
    d = Path(video_dir)
    timing = json.loads((d / "giong-timing.json").read_text(encoding="utf-8"))
    nguon = json.loads((d / "nguon.json").read_text(encoding="utf-8")) if (d / "nguon.json").exists() else []
    msgs = validate(json.loads((d / "canh.json").read_text(encoding="utf-8")), timing, SVG_DIR, nguon)
    for m in msgs:
        print("-", m)
    (d / "phu-de.srt").write_text(to_srt(timing), encoding="utf-8", newline="\n")
    errs = [m for m in msgs if m.startswith("Lỗi")]
    print(f"{len(errs)} lỗi, {len(msgs) - len(errs)} cảnh báo; đã ghi phu-de.srt")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
