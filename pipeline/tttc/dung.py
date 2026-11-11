"""Ghép canh.json + giọng thành dự án HyperFrames, bảng soi hình, kiểm hình–tiếng.

Trường canh.json theo mẫu (ngoài id, mau, start, end; mọi cảnh có thể ghi đè nen: toi|kem|vang):
- chuong:      so (vd "Phần 2"), chuong (tên chương)
- minh-hoa:    svg (tên trong pipeline/svg), phu? [tối đa 2 đạo cụ], nhan, nguon_id?, dong? bob|xoay|dap|chop (mặc định bob),
               san_khau? (phông: nen-dat mặc định, hoặc phần sau "san-khau-" của svg/san-khau-*.svg), bo_cuc? [1–4 {svg, x, y, to}] (thay phu;
               x,y 0–1 trên sàn, to 0,2–1,5), may_quay? dung|day-vao|keo-ra|lia|he-lo
- so-lon:      so (số hoặc chuỗi "5,3"), tu? (giá trị cũ: số đếm từ đó tới so, cũng phải khớp nguồn), truoc?, sau?, nhan, nguon_id, svg? (hình nền mờ), huong? len|xuong, dong? (như minh-hoa, mặc định không)
- bieu-do:     nhan (tiêu đề), bieu_do{kieu, nhan_x[], gia_tri[], don_vi, noi_bat?, chu_thich?, nguon_id (một id hoặc danh sách)}
- nhan-vat:    anh (tệp trong anh/), nhan (tên), vai
- trang-nguon: anh (tệp trong nguon/), khung "x,y,w,h" (% vùng trang), nguon_id
- trich-bao:   nguon_id, trich (nguyên văn một đoạn trong trich_dan, ≤ 25 từ), to_vang (cụm trong trich); trich nguồn tiếng Anh thì
               bắt buộc trich_vi (bản dịch của kênh, hiện lên màn hình kèm nhãn) và to_vang_vi (cụm trong trich_vi)
- quy-trinh:   tieu_de?, buoc [3–6 phần tử {nhan, svg?}], noi_bat? (chỉ số bước), nguon_id?, dong? (cho bước nổi bật, mặc định dap)
- xep-hang:    tieu_de?, moc? [2–10 nhãn năm: chạy theo năm, khi đó so của mỗi hàng là danh sách một giá trị cho mỗi mốc], hang [2–8 {nhan, so}] theo đúng thứ tự hiển thị (tác giả tự xếp), don_vi, nguon_id (bắt buộc: mọi số phải khớp nguồn),
               noi_bat? (chỉ số hàng), dong? (cho thanh nổi bật, mặc định dap); thanh ngang dài theo số, số đếm tăng ở đầu thanh
- ban-do:      tieu_de?, diem [2–6 {nhan, vi_do, kinh_do, noi_bat?}], noi? [{tu, den, nhan?}] (mũi tên cong nối hai điểm theo chỉ số),
               nguon_id?, dong? (vòng sáng ở điểm nổi bật, mặc định dap); bản đồ vị trí theo toạ độ (hình nước từ du-lieu/nuoc.json, Natural Earth); diem có thể ghi nuoc (mã ADM0_A3, vd VNM) để tô sáng nước đó
- so-sanh:     trai, phai {nhan, svg, so?, don_vi?, to? (0–1, cỡ hình tương đối)}, don_vi?, ti_le? ("gấp ~700 lần"),
               nguon_id (bắt buộc nếu có so), dong? (cho huy hiệu SO, mặc định dap)
- thoi-gian:   tieu_de?, truc {tu, den, don_vi}, hang [2–5 phần tử {nhan, tu, den, noi_bat?}], nguon_id (năm phải có trong nguồn)
- b-roll:      video (tệp trong broll/, tải bằng tttc.broll), nhan, so? ("01"), tu_khoa? (≤ 5 từ bật to giữa khung theo nhip[1]),
               chia? {so, truoc?, sau?, nhan} (video lùi sang trái, số hiện ở nửa phải theo nhip[2]); có số thì cần nguon_id
- chu-dong:    cau (câu chốt ≤ 16 từ, nên trùng lời đọc: từng chữ hiện đúng lúc giọng nói tới), nhan_tu? (cụm trong cau được tô
               màu nhấn và gạch dạ quang), nho? (dòng nhỏ phía trên, ≤ 5 từ)
- phan-tram:   so (0–100), sau? (mặc định "%"), tieu_de?, nhan (ý nghĩa con số), nguon_id (bắt buộc); vòng tròn chạy tới đúng tỉ lệ
- mo-dau:      cau? (câu hỏi của video) – logo kênh hiện ra với ba vòng "nhịp"; đặt ngay sau đoạn móc câu, không đặt ở giây 0
- ket-thuc:    cau? ("Xem tiếp nhé"), moi?, nut?, nut_xong?, khung? – cảnh cuối ≥ 5 s, chừa hai khung 16:9 bên phải cho phần tử
               màn hình kết thúc của YouTube (đặt video gợi ý đúng vào hai khung trong YouTube Studio)
Mọi mẫu: dan? {the, goc? phai|trai, huong? (hướng nhìn; mặc định nghiêng về giữa màn hình), tu?} – nhân vật dẫn chuyện; có
pipeline/nhan-vat/kit.json (bắt buộc khi có dan) cho PNG biểu cảm × hướng (tttc/nhan_vat.py).
Mọi mẫu: nhip? [cụm từ trong lời đọc của cảnh, theo thứ tự bước của mẫu – xem DEFAULT_STEPS]; null giữ mốc mặc định.
Nền tự gán theo vai trò: chương vàng, bằng chứng (trích báo, trang nguồn, nhân vật) kem, còn lại tối. Chuyển cảnh tự gán (transitions()).
Tự thêm: thanh tiến trình chương ở mép trên; Nhịp ló ra ở cảnh so-lon có trong_diem (dan_cua); dan.lau = số giây ló ra.
"""
import json
import re
import shutil
import sys
import subprocess
import tempfile
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import urlparse

from PIL import Image

from tttc import ban_do, grain, nhan_vat, theme
from tttc.canh import _norm, cues, phrase_time
from tttc.kiem import vi_value
from tttc.tron_am import tron

PIPE = Path(__file__).resolve().parent.parent
TPL, SVG, CONFIG = PIPE / "templates" / "canh", PIPE / "svg", PIPE / "config.json"
SFX = PIPE / "am-thanh" / "sfx"
PREFIX = {"minh-hoa": "mh-", "bieu-do": "bd-", "so-lon": "sl-", "nhan-vat": "nv-", "trang-nguon": "tn-",
          "chuong": "ch-", "trich-bao": "tb-", "b-roll": "br-", "quy-trinh": "qt-", "so-sanh": "ss-", "thoi-gian": "tg-", "ban-do": "bn-", "xep-hang": "xh-",
          "chu-dong": "cd-", "phan-tram": "pt-", "mo-dau": "md-", "ket-thuc": "kt-"}
# Mốc mặc định (giây tính từ đầu cảnh) của các bước trong mỗi mẫu, theo thứ tự canh.json:nhip.
DEFAULT_STEPS = {
    "minh-hoa": [0.72, 0.5, 0.58],     # nhãn, đạo cụ 1, đạo cụ 2
    "so-lon": [0.05, 1.6],             # bắt đầu đếm, dòng dưới
    "trang-nguon": [0.8],              # zoom vào số
    "nhan-vat": [0.8],                 # thẻ vai trò
    "so-sanh": [0.5, 1.1, 1.8],        # bên trái, bên phải (+SO), nhãn tỉ lệ
    "chuong": [],
    "trich-bao": [0.9],                # tô vàng
    "b-roll": [0.5, 0.3, 0.6],         # nhãn, từ khoá bật lên, khung chia đôi
    "phan-tram": [0.35, 0.6],          # vòng bắt đầu chạy, dòng ý nghĩa
    "mo-dau": [],
    "ket-thuc": [],
}
GSAP = "https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"
# Màu phụ theo ý nghĩa (canh.json: sac): (nhấn, bóng, bóng tối, màu chữ trên nhấn). Mặc định không ghi sac = vàng thương hiệu.
# Màu phụ lấy từ brand/theme.json (xanh: tiết kiệm, miễn phí; do: giới hạn, rủi ro, thuế; lam: AI, dữ liệu; tim: gói cao cấp).
SAC, VANG = theme.SAC, theme.VANG
TILE_W, TILE_H, COLS = 384, 216, 10


def _render_cfg() -> dict:
    return _read_json(CONFIG, {}).get("render", {})


def render_args(cfg: dict | None = None) -> list[str]:
    """Tham số `hyperframes render` từ config.json:render (bitrate, max_bitrate, keyframe); khóa không đặt thì bỏ."""
    cfg = _render_cfg() if cfg is None else cfg
    out = []
    for key, flag in (("bitrate", "--video-bitrate"), ("max_bitrate", "--max-bitrate"), ("keyframe", "--keyframe-interval")):
        if cfg.get(key):
            out += [flag, str(cfg[key])]
    return out


def _read_json(p: Path, default):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default


def vi_number(x) -> str:
    """Số viết kiểu Việt, giữ đúng số chữ số thập phân: 5.3 → '5,3', 522500 → '522.500'."""
    if isinstance(x, str):
        return x.strip()
    whole, _, frac = repr(float(x)).partition(".") if not float(x).is_integer() else (str(int(x)), "", "")
    whole = f"{int(whole):,}".replace(",", ".")
    return f"{whole},{frac}" if frac else whole


def _num(x) -> float:
    return vi_value(x) if isinstance(x, str) else x


def _source_line(nguon: dict) -> str:
    if nguon.get("trang_thai") == "tu-tinh":
        return f"Tự tính: {nguon['cong_thuc']}"
    host = urlparse(nguon["url"]).netloc.removeprefix("www.")
    d = date.fromisoformat(nguon["ngay_truy_cap"])
    return f"Nguồn: {host}, {d:%d/%m/%Y}"


def _nuoc_json(diem: list[dict]) -> str:
    """Hình các nước quanh các điểm của cảnh bản đồ (khung rộng hơn vùng chứa điểm); chưa có dữ liệu thì rỗng, chỉ còn lưới."""
    data = ban_do.doc()
    if data is None:
        return "{}"
    los, las = [d["kinh_do"] for d in diem], [d["vi_do"] for d in diem]
    pl, pa = max(25, 0.5 * (max(los) - min(los))), max(25, 0.5 * (max(las) - min(las)))
    return json.dumps(ban_do.chon(data["nuoc"], min(los) - pl, max(los) + pl, min(las) - pa, max(las) + pa),
                      ensure_ascii=False, separators=(",", ":"))


def _vars(c: dict, by_id: dict, credits: dict, broll_credits: dict | None = None) -> dict:
    broll_credits = broll_credits or {}
    src = lambda nid: " · ".join(dict.fromkeys(_source_line(by_id[n]) for n in (nid if isinstance(nid, list) else [nid])
                                               if n in by_id))  # nhiều id cùng một trang chỉ ghi một lần
    m = c["mau"]
    if m == "chuong":
        return {"so": c.get("so", ""), "ten": c.get("chuong", "")}
    if m == "minh-hoa":
        phu = c.get("phu", [])
        sk = c.get("san_khau", "nen-dat")
        return {"svg": f"assets/svg/{c['svg']}.svg", "nhan": c.get("nhan", ""), "nguon": src(c.get("nguon_id")),
                "phu1": f"assets/svg/{phu[0]}.svg" if len(phu) > 0 else "",
                "phu2": f"assets/svg/{phu[1]}.svg" if len(phu) > 1 else "", "dong": c.get("dong", "bob"),
                "phong": f"assets/svg/{'nen-dat' if sk == 'nen-dat' else 'san-khau-' + sk}.svg",
                "bo_cuc": json.dumps([{**b, "svg": f"assets/svg/{b['svg']}.svg"} for b in c.get("bo_cuc", [])],
                                     ensure_ascii=False),
                "may_quay": c.get("may_quay") or "dung", "thoi_luong": round(c.get("end", 0) - c.get("start", 0), 3)}
    if m == "so-lon":
        return {"so": _num(c["so"]), "so_hien": vi_number(c["so"]), "tu": _num(c["tu"]) if c.get("tu") is not None else 0,
                "tu_hien": vi_number(c["tu"]) if c.get("tu") is not None else "", "truoc": c.get("truoc", ""),
                "sau": c.get("sau", ""), "nhan": c.get("nhan", ""), "nguon": src(c.get("nguon_id")),
                "svg": f"assets/svg/{c.get('svg', 'tien')}.svg", "huong": c.get("huong", ""), "dong": c.get("dong", "")}
    if m == "bieu-do":
        b = c["bieu_do"]
        return {"tieu_de": c.get("nhan", ""), "nhan_x": json.dumps(b["nhan_x"], ensure_ascii=False),
                "gia_tri": json.dumps([_num(v) for v in b["gia_tri"]]),
                "so_hien": json.dumps([vi_number(v) for v in b["gia_tri"]]), "don_vi": b.get("don_vi", ""),
                "noi_bat": b.get("noi_bat", -1), "chu_thich": b.get("chu_thich", ""), "nguon": src(b.get("nguon_id"))}
    if m == "nhan-vat":
        return {"anh": f"assets/anh/{c['anh']}", "ten": c.get("nhan", ""), "vai": c.get("vai", ""),
                "ghi_cong": "Ảnh: " + credits[c["anh"]] if c["anh"] in credits else ""}
    if m == "trang-nguon":
        n = by_id.get(c.get("nguon_id"))
        url = n["url"].split("://", 1)[-1].removeprefix("www.").rstrip("/") if n else ""
        return {"anh": f"assets/nguon/{c['anh']}", "khung": c.get("khung", "0,0,0,0"), "url": url,
                "nguon": src(c.get("nguon_id"))}
    if m == "trich-bao":
        n = by_id[c["nguon_id"]]
        return {"bao": n.get("ten") or urlparse(n["url"]).netloc.removeprefix("www."),
                "ngay": f"{date.fromisoformat(n['ngay_truy_cap']):%d/%m/%Y}",
                "tieu_de": c.get("trich_vi") or c["trich"], "to_vang": c.get("to_vang_vi" if c.get("trich_vi") else "to_vang", ""),
                "dich": "Bản dịch của kênh" if c.get("trich_vi") else ""}
    if m == "thoi-gian":
        return {"tieu_de": c.get("tieu_de", ""), "nguon": src(c.get("nguon_id")),
                "truc": json.dumps(c["truc"], ensure_ascii=False),
                "hang": json.dumps([dict(h, noi_bat=bool(h.get("noi_bat"))) for h in c["hang"]], ensure_ascii=False)}
    if m == "so-sanh":
        def side(s):
            co = s.get("so") is not None
            return json.dumps({"nhan": s["nhan"], "svg": f"assets/svg/{s['svg']}.svg", "so": _num(s["so"]) if co else None,
                               "so_hien": vi_number(s["so"]) if co else "", "don_vi": s.get("don_vi", c.get("don_vi", "")),
                               "to": s.get("to", 1.0)}, ensure_ascii=False)
        return {"trai": side(c["trai"]), "phai": side(c["phai"]), "ti_le": c.get("ti_le", ""),
                "nguon": src(c.get("nguon_id")), "dong": c.get("dong", "dap")}
    if m == "quy-trinh":
        return {"tieu_de": c.get("tieu_de", ""), "noi_bat": c.get("noi_bat", -1), "dong": c.get("dong", "dap"),
                "nguon": src(c.get("nguon_id")),
                "buoc": json.dumps([{"nhan": b["nhan"], "svg": f"assets/svg/{b['svg']}.svg" if b.get("svg") else ""}
                                    for b in c["buoc"]], ensure_ascii=False)}
    if m == "xep-hang":
        nb = c.get("noi_bat", -1)
        one = lambda f, x: [f(y) for y in x] if isinstance(x, list) else f(x)  # chuỗi giá trị theo mốc (chạy theo năm) hoặc một số
        return {"tieu_de": c.get("tieu_de", ""), "don_vi": c.get("don_vi", ""), "nguon": src(c.get("nguon_id")), "dong": c.get("dong", "dap"),
                "moc": json.dumps(c.get("moc") or [], ensure_ascii=False),
                "hang": json.dumps([{"nhan": h["nhan"], "so": one(_num, h["so"]), "so_hien": one(vi_number, h["so"]), "noi_bat": i == nb}
                                    for i, h in enumerate(c["hang"])], ensure_ascii=False)}
    if m == "ban-do":
        return {"tieu_de": c.get("tieu_de", ""), "nguon": src(c.get("nguon_id")), "dong": c.get("dong", "dap"),
                "nuoc": _nuoc_json(c["diem"]),
                "diem": json.dumps([dict(d, noi_bat=bool(d.get("noi_bat"))) for d in c["diem"]], ensure_ascii=False),
                "noi": json.dumps([{"tu": e["tu"], "den": e["den"], "nhan": e.get("nhan", "")} for e in c.get("noi") or []],
                                  ensure_ascii=False)}
    if m == "b-roll":
        ch = c.get("chia")
        return {"nhan": c.get("nhan", ""), "so": c.get("so", ""), "ghi_cong": broll_credits.get(c["video"], ""),
                "tu_khoa": c.get("tu_khoa", ""), "nguon": src(c.get("nguon_id")),
                "chia": json.dumps({"so_hien": vi_number(ch["so"]), "truoc": ch.get("truoc", ""), "sau": ch.get("sau", ""),
                                    "nhan": ch.get("nhan", "")}, ensure_ascii=False) if ch else ""}
    if m == "chu-dong":
        return {"cau": c["cau"], "nhan_tu": c.get("nhan_tu", ""), "nho": c.get("nho", "")}
    if m == "phan-tram":
        return {"so": _num(c["so"]), "so_hien": vi_number(c["so"]), "sau": c.get("sau", "%"), "tieu_de": c.get("tieu_de", ""),
                "nhan": c.get("nhan", ""), "nguon": src(c.get("nguon_id"))}
    if m == "mo-dau":
        return {"cau": c.get("cau", "")}
    if m == "ket-thuc":
        return {k: c[k] for k in ("cau", "nut", "nut_xong", "khung") if c.get(k)} | ({"moi": c["moi"]} if c.get("moi") else {})
    raise ValueError(f"mẫu không có: {m}")


def moc_tu(cau: str, words: list[dict], start: float, end: float) -> list[float]:
    """Giây (tính từ đầu cảnh) giọng đọc nói tới từng chữ của cau: khớp lần lượt, cho phép lời đọc chen 3 chữ;
    chữ không khớp hiện ngay sau chữ trước."""
    win = [w for w in words if start - 0.01 <= w["start"] < end]
    out, j, prev = [], 0, 0.2
    for tok in (_norm(t) for t in cau.split()):
        hit = next((k for k in range(j, min(j + 4, len(win))) if _norm(win[k]["w"]) == tok), None)
        if hit is not None:
            prev, j = round(max(0.0, win[hit]["start"] - start), 3), hit + 1
        else:
            prev = round(prev + 0.08, 3)
        out.append(prev)
    return out


def steps(c: dict, words: list[dict]) -> list[float]:
    """Mốc từng bước của cảnh: từ khoá trong nhip (khớp giọng đọc) hoặc mặc định của mẫu."""
    if c["mau"] == "bieu-do":
        n = len(c["bieu_do"]["gia_tri"])
        base = [0.4 + i * 0.18 for i in range(n)] + [0.4 + n * 0.18 + 0.5]
    elif c["mau"] == "quy-trinh":
        base = [round(0.5 + 0.55 * i, 3) for i in range(len(c["buoc"]))]
    elif c["mau"] == "thoi-gian":
        base = [round(0.5 + 0.6 * i, 3) for i in range(len(c["hang"]))]
    elif c["mau"] == "xep-hang":
        base = [round(0.4 + 1.3 * k, 3) for k in range(len(c["moc"]))] if c.get("moc") else [round(0.4 + 0.4 * i, 3) for i in range(len(c["hang"]))]
    elif c["mau"] == "ban-do":
        nd = len(c["diem"])
        base = [round(0.5 + 0.55 * i, 3) for i in range(nd)] + [round(0.5 + 0.55 * nd + 0.5 * j, 3) for j in range(len(c.get("noi") or []))]
    elif c["mau"] == "chu-dong":
        return moc_tu(c["cau"], words, c["start"], c["end"])
    else:
        base = list(DEFAULT_STEPS[c["mau"]])
    for k, ph in enumerate(c.get("nhip") or []):
        t = phrase_time(words, ph, c["start"], c["end"]) if ph else None
        if t is not None and k < len(base):
            base[k] = round(t - c["start"], 3)
    return base


def sfx_events(c: dict, st: list[float]) -> list[tuple[str, float, float]]:
    """(tệp, giây tính từ đầu cảnh, âm lượng) gắn theo đúng các mốc hình của cảnh."""
    m = c["mau"]
    if m == "chuong":
        return [("impact-bass-1", 0.1, 0.25)]
    if m == "minh-hoa":
        ev = [("pop", 0.55, 0.3)]
        n = len(c.get("bo_cuc") or c.get("phu", [])[:2])
        ev += [("pop", st[k + 1] if k + 1 < len(st) else st[-1] + 0.08 * (k + 2 - len(st)), 0.2) for k in range(n)]
        return ev
    if m == "so-lon":
        return [("ping", st[0] + 1.3, 0.3)]
    if m == "bieu-do":
        return [("pop", st[-1] + 0.1, 0.3)] if c["bieu_do"].get("chu_thich") else []
    if m == "quy-trinh":
        return [("pop", t, 0.2) for t in st[:6]]
    if m == "thoi-gian":
        return [("whoosh-short", t, 0.2) for t in st[:5]]
    if m == "xep-hang":
        return [("pop", t, 0.2) for t in st[:10]]
    if m == "ban-do":
        nd = len(c["diem"])
        return [("pop", t, 0.2) for t in st[:nd]] + [("whoosh-short", t, 0.2) for t in st[nd:]]
    if m == "so-sanh":
        return [("pop", st[0], 0.3), ("pop", st[1], 0.3)] + ([("chime", st[2] + 0.1, 0.3)] if c.get("ti_le") else [])
    if m == "trang-nguon":
        return [("whoosh-short", st[0], 0.3)]
    if m == "nhan-vat":
        return [("whoosh-short", 0.05, 0.25)]
    if m == "trich-bao":
        return [("click-soft", st[0], 0.35)]
    if m == "chu-dong":
        return [("whoosh-short", 0.0, 0.18)]
    if m == "phan-tram":
        return [("whoosh", st[0], 0.2), ("ping", st[0] + 1.4, 0.3)]
    if m == "mo-dau":
        return [("impact-bass-1", 0.05, 0.3), ("chime", 0.35, 0.22)]
    if m == "ket-thuc":
        return [("whoosh-short", 0.3, 0.25), ("click", 1.9, 0.45), ("chime", 2.2, 0.22)]
    if m == "b-roll":
        return ([("pop", st[1], 0.25)] if c.get("tu_khoa") else []) + ([("whoosh-short", st[2], 0.3)] if c.get("chia") else [])
    return []


BANG_CHUNG = {"trich-bao", "trang-nguon", "nhan-vat"}


def grounds(scenes: list[dict]) -> list[str]:
    """Nền theo vai trò (user duyệt 12/11/2026): chương vàng, bằng chứng kem, số liệu và minh họa tối; canh.json ghi đè được."""
    return [c.get("nen") or ("vang" if c["mau"] == "chuong" else "kem" if c["mau"] in BANG_CHUNG else "toi")
            for c in scenes]


PEEK_LAU = 1.8  # giây Nhịp ló ra ở cảnh số trọng điểm


def dan_cua(c: dict) -> dict | None:
    """Nhân vật của cảnh: dan ghi tay, hoặc Nhịp ngạc nhiên ló ra ở cảnh so-lon trọng điểm (cảnh khác dễ che số)."""
    if c.get("dan"):
        return c["dan"]
    if c["mau"] == "so-lon" and c.get("trong_diem") and c["end"] - c["start"] >= 2.5:
        return {"the": "ngac-nhien", "goc": "phai", "lau": PEEK_LAU}
    return None


def chuong_doan(scenes: list[dict], t0: float, total: float) -> list[tuple[float, float, str]]:
    """(bắt đầu, kết thúc, tên) mỗi chương tính từ t0; phần trước chương đầu là "Mở đầu"."""
    moc = [(c["start"] - t0, c.get("chuong", "")) for c in scenes if c["mau"] == "chuong"]
    if not moc or moc[0][0] > 0.01:
        moc.insert(0, (0.0, "Mở đầu"))
    return [(a, (moc[k + 1][0] if k + 1 < len(moc) else total), ten) for k, (a, ten) in enumerate(moc)]


IRIS = {"so-lon", "phan-tram", "mo-dau", "ket-thuc"}  # cảnh mở bằng mống mắt: khép vào tâm, cắt, mở ra


def transitions(scenes: list[dict]) -> list[tuple[int, str]]:
    """(chỉ số cảnh sau đường nối, kiểu): vào chương ba lớp màu nhấn quét qua, rời chương ba lớp tối quét qua, vào cảnh
    con số lớn (so-lon, phan-tram) và logo thì mống mắt khép–mở, cứ 3 đường nối còn lại có 1 lần chớp tối."""
    out = []
    for k in range(1, len(scenes)):
        a, b = scenes[k - 1]["mau"], scenes[k]["mau"]
        kind = ("vang" if b == "chuong" else "muc" if a == "chuong" else "iris" if b in IRIS
                else "dip" if k % 3 == 0 else "")
        if kind:
            out.append((k, kind))
    return out


def _scene_file(mau: str, sid: str, video: str = "") -> str:
    s = theme.cssify((TPL / f"{mau}.html").read_text(encoding="utf-8")).replace("__VIDEO__", f"assets/broll/{video}")
    s = s.replace("/*__DONG__*/", (TPL / "dong.js").read_text(encoding="utf-8"))
    s = s.replace(f'data-composition-id="{mau}"', f'data-composition-id="{sid}"')
    s = s.replace(f'__timelines["{mau}"]', f'__timelines["{sid}"]')
    return re.sub(rf"(?<![\w-]){PREFIX[mau]}", f"{sid}-{PREFIX[mau]}", s)  # id/class riêng cho mỗi lần gắn


def compose(video_dir, w: int = 1920, h: int = 1080, scene_range: tuple[int, int] | None = None,
            out: str = "composition") -> Path:
    d = Path(video_dir)
    scenes = _read_json(d / "canh.json", {"scenes": []})["scenes"]
    timing = _read_json(d / "giong-timing.json", {"duration": 0, "words": []})
    by_id = {n["id"]: n for n in _read_json(d / "nguon.json", [])}
    credits = {c["tep"]: c["ghi_cong"] for c in _read_json(d / "anh" / "ghi-cong.json", [])}
    broll_credits = {c["tep"]: c["ghi_cong"] for c in _read_json(d / "broll" / "ghi-cong.json", [])}
    i, j = scene_range or (0, len(scenes))
    nens = grounds(scenes)[i:j]
    scenes = scenes[i:j]
    t0 = scenes[0]["start"]
    total = round(scenes[-1]["end"] - t0, 3) if scene_range else timing["duration"]

    o = d / out
    if o.exists():
        shutil.rmtree(o)
    (o / "compositions").mkdir(parents=True)
    shutil.copytree(SVG, o / "assets" / "svg", ignore=shutil.ignore_patterns("*.py", "*.md", "*.png"))  # cả thư viện: mẫu dùng ảnh mặc định
    for k in {c["sac"] for c in scenes if c.get("sac")}:  # bản đổi màu nhấn vàng → màu phụ, không vẽ lại thư viện
        for f in list((o / "assets" / "svg").glob("*.svg")):
            if f.stem == "nen-dat" or f.stem.startswith("tui-") or "@" in f.stem:
                continue
            t = f.read_text(encoding="utf-8")
            for old, new in zip(VANG, SAC[k][:3]):
                t = re.sub(old, new, t, flags=re.I)
            (f.with_name(f"{f.stem}@{k}.svg")).write_text(t, encoding="utf-8")
    for sub in ("anh", "nguon", "broll"):
        if (d / sub).exists():
            shutil.copytree(d / sub, o / "assets" / sub)
    kit = nhan_vat.doc_kit()  # có bộ nhân vật PNG thì dùng, không thì nhân vật SVG cũ
    if kit:
        (o / "assets" / "nv").mkdir()
        can = set()  # chỉ chép ảnh mà các cảnh trong khoảng dựng thật sự dùng (kit đầy đủ nặng hàng MB)
        for c in scenes:
            dn = dan_cua(c)  # không dùng tên d: đó là thư mục video
            if dn:
                hg = dn.get("huong") or nhan_vat.huong_mac_dinh(dn.get("goc", "phai"))
                can.add(nhan_vat.tep(dn["the"], hg))
                if [dn["the"], hg] in kit["nham"]:
                    can.add(nhan_vat.tep(dn["the"], hg, True))
        for n in can:
            if (nhan_vat.KIT.parent / n).exists():
                shutil.copy(nhan_vat.KIT.parent / n, o / "assets" / "nv" / n)
    nhac = _read_json(CONFIG, {}).get("nhac_nen")
    if nhac and not (PIPE / nhac).is_file():
        raise FileNotFoundError(f"Không thấy nhạc nền {nhac} (config.json:nhac_nen)")
    if nhac:  # nhạc trộn sẵn vào một bản giọng: tự hạ khi có tiếng (tron_am), Shorts cắt cùng một tệp
        tron(d / "giong.mp3", PIPE / nhac, o / "assets" / "giong.mp3")
    else:
        shutil.copy(d / "giong.mp3", o / "assets" / "giong.mp3")
    shutil.copytree(SFX, o / "assets" / "sfx")
    if any(c["mau"] in ("mo-dau", "ket-thuc") for c in scenes):  # logo kênh cho cảnh mở đầu / kết thúc
        (o / "assets" / "brand").mkdir()
        shutil.copy(theme.THEME.parent / "logo-nhip-cong-nghe.png", o / "assets" / "brand" / "logo.png")
    do_grain = float(_render_cfg().get("grain") or 0)
    if do_grain > 0:  # hạt nhiễu mịn chống banding: PNG xám phủ overlay với độ mờ thấp
        grain.tao_grain(o / "assets" / "grain.png")

    hosts = []
    sfx = []
    for idx, (c, nen) in enumerate(zip(scenes, nens)):
        sid = c["id"]
        page = _scene_file(c["mau"], sid, c.get("video", ""))
        if h > w:  # Shorts: nhãn ghi công/nguồn nằm trên clip sáng, thêm nền tối để đủ tương phản (kiểm của hyperframes)
            page = page.replace("</style>", "#root [id$=\"-br-ghi-cong\"], #root [id$=\"-nguon\"] { background: rgba(0,0,0,0.6) !important; "
                                "color: #fff !important; padding: 6px 16px; border-radius: 10px; }</style>", 1)
        (o / "compositions" / f"{sid}.html").write_text(page, encoding="utf-8")
        st = steps(c, timing.get("words", []))
        sfx += [(f, c["start"] - t0 + t, v) for f, t, v in sfx_events(c, st)]
        extra = {"vao": str(c.get("vao", idx % 4))} if c["mau"] == "minh-hoa" else {}  # kiểu vào cảnh xoay vòng
        vals = json.dumps(dict(_vars(c, by_id, credits, broll_credits), nen=nen, nhip=json.dumps(st), **extra),
                          ensure_ascii=False)
        sac = c.get("sac")
        style = ""
        if sac in SAC:
            vals = re.sub(r"assets/svg/(?!nen-dat|tui-)([\w-]+)\.svg", rf"assets/svg/\1@{sac}.svg", vals)
            style = f' style="--accent:{SAC[sac][0]};--accent-ink:{SAC[sac][3]};--tint:16%"'
        vals = vals.replace("'", "&#39;")
        hosts.append(f'<div id="{sid}" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html"\n'
                     f'           data-start="{round(c["start"] - t0, 3)}" data-duration="{round(c["end"] - c["start"], 3)}"'
                     f' data-track-index="1" data-track-kind="graphics" data-width="1920" data-height="1080"{style}\n'
                     f"           data-variable-values='{vals}'></div>")

    trs, tr_js = [], []
    for k, kind in transitions(scenes):
        seam = round(scenes[k]["start"] - t0, 3)
        a = round(max(0.0, seam - 0.3), 3)
        if kind != "dip":
            sfx.append(("whoosh-short", seam - 0.3, 0.35))
        if kind == "dip":  # tối nhanh 3 khung trước cú cắt rồi sáng lại
            trs.append(f'<div id="tr-{k}" class="clip tr" data-start="{a}" data-duration="0.6" data-track-index="4">'
                       f'<div id="tr-{k}-p" class="tr-p tr-dip"></div></div>')
            tr_js.append(f'tl.fromTo("#tr-{k}-p", {{ opacity: 0 }}, {{ opacity: 0.6, duration: 0.1 }}, {seam - 0.1:.3f}); '
                         f'tl.to("#tr-{k}-p", {{ opacity: 0, duration: 0.15 }}, {seam:.3f});')
        elif kind == "iris":  # màn tối khép thành vòng tròn vào tâm (che cú cắt) rồi mở ra, viền màu nhấn chạy theo mép
            trs.append(f'<div id="tr-{k}" class="clip tr" data-start="{a}" data-duration="0.85" data-track-index="4">'
                       f'<div id="tr-{k}-p" class="tr-p tr-iris"></div><div id="tr-{k}-v" class="tr-vien"></div></div>')
            tr_js.append(f'tl.fromTo("#tr-{k}-p", {{ "--r": "1150px" }}, {{ "--r": "0px", duration: 0.3, ease: "power3.in" }}, {a:.3f}); '
                         f'tl.to("#tr-{k}-p", {{ "--r": "1150px", duration: 0.5, ease: "expo.out" }}, {seam:.3f}); '
                         f'tl.fromTo("#tr-{k}-v", {{ scale: 1 }}, {{ scale: 0, duration: 0.3, ease: "power3.in" }}, {a:.3f}); '
                         f'tl.to("#tr-{k}-v", {{ scale: 1, duration: 0.5, ease: "expo.out" }}, {seam:.3f});')
        else:  # ba lớp màu quét qua lệch nhau, lớp cuối cùng màu với nền cảnh đến: che cú cắt mà có chiều sâu
            trs.append(f'<div id="tr-{k}" class="clip tr" data-start="{round(a - 0.08, 3)}" data-duration="0.76" data-track-index="4">'
                       + "".join(f'<div id="tr-{k}-p{j}" class="tr-p tr-{kind}-{j}"></div>' for j in range(3)) + '</div>')
            tr_js.append(f'tl.fromTo(["#tr-{k}-p0", "#tr-{k}-p1", "#tr-{k}-p2"], {{ xPercent: -101 }}, '
                         f'{{ xPercent: 0, duration: 0.3, ease: "power3.in", stagger: 0.04 }}, {a - 0.08:.3f}); '
                         f'tl.to(["#tr-{k}-p0", "#tr-{k}-p1", "#tr-{k}-p2"], {{ xPercent: 101, duration: 0.32, ease: "power3.out", '
                         f'stagger: {{ each: 0.04, from: "end" }} }}, {seam:.3f});')

    caps = [f'<div id="cap-{k}" class="clip cap" data-start="{round(a - t0, 3)}" data-duration="{round(b - a, 3)}">'
            f"<span>{escape(t)}</span></div>"
            for k, (a, b, t) in enumerate(cues(timing)) if a >= t0 - 0.01 and b <= t0 + total + 0.01]

    dan_tags, dan_js = [], []
    if h <= w:  # shortcut: Shorts (khung dọc) chưa có nhân vật; thêm khi có nhu cầu
        for k, c in enumerate(scenes):
            d = dan_cua(c)
            if not d:
                continue
            a, dur = round(c["start"] - t0, 3), round(c["end"] - c["start"], 3)
            ra = phrase_time(timing.get("words", []), d["tu"], c["start"], c["end"]) if d.get("tu") else None
            vao = round(a + (ra - c["start"] if ra is not None else 0.3 if not d.get("lau") else 1.0), 3)
            if d.get("lau"):  # chỉ ló ra một lúc rồi lui xuống, không đứng suốt cảnh
                dur = round(min(dur, vao - a + d["lau"]), 3)
            the, goc = d["the"], d.get("goc", "phai")
            if not kit:
                raise ValueError(f"cảnh {c['id']} có dan nhưng chưa có bộ nhân vật (pipeline/nhan-vat/kit.json)")
            huong = d.get("huong") or nhan_vat.huong_mac_dinh(goc)
            co_nham = [the, huong] in kit["nham"]
            mo, nham = f"assets/nv/{nhan_vat.tep(the, huong)}", f"assets/nv/{nhan_vat.tep(the, huong, True)}"
            dan_tags.append(
                f'<div id="dan-{k}" class="clip dan dan-{goc}" data-start="{a}" data-duration="{dur}" '
                f'data-track-index="3"><img src="{mo}" alt="">'
                + (f'<img id="dan-{k}-nham" src="{nham}" alt="" style="opacity:0">' if co_nham else "") + '</div>')
            dan_js.append(f'tl.fromTo("#dan-{k}", {{ scale: 0, y: 40, transformOrigin: "50% 100%" }}, '
                          f'{{ scale: 1, y: 0, duration: 0.45, ease: "back.out(2)" }}, {vao});')
            if d.get("lau"):
                dan_js.append(f'tl.to("#dan-{k}", {{ scale: 0, y: 40, duration: 0.3, ease: "back.in(2)" }}, {a + dur - 0.3:.3f});')
            dan_js.append(f'tl.to("#dan-{k}", {{ y: -10, duration: 1.2, ease: "sine.inOut", yoyo: true, '
                          f'repeat: {max(0, int((a + dur - vao - 0.5) / 1.2) - 1)} }}, {vao + 0.5:.3f});')  # hữu hạn, đủ phủ hết cảnh
            t = vao + 1.8
            while co_nham and t < a + dur - 0.3:  # chớp mắt: ảnh nhắm mắt phủ lên ảnh mở mắt (cùng hình dáng) trong 0,14 s
                dan_js.append(f'tl.set("#dan-{k}-nham", {{ opacity: 1 }}, {t:.3f}); '
                              f'tl.set("#dan-{k}-nham", {{ opacity: 0 }}, {t + 0.14:.3f});')
                t += 2.8
    tien_do, tien_do_js = "", []
    if h <= w:  # shortcut: Shorts (khung dọc) chưa có thanh chương; thêm khi có nhu cầu
        doan = chuong_doan(scenes, t0, total)
        tien_do = ('<div id="tien-do" class="clip" data-start="0" data-duration="' + str(total) + '" data-track-index="6">'
                   + "".join(f'<div class="td-doan" style="left:{a / total * 100:.3f}%;width:{(b - a) / total * 100:.3f}%">'
                             f'<div id="td-{k}" class="td-day"></div></div>' for k, (a, b, _) in enumerate(doan))
                   + "".join(f'<div id="td-ten-{k}" class="td-ten" style="opacity:0">{escape(ten)}</div>'
                             for k, (_, _, ten) in enumerate(doan)) + "</div>")
        for k, (a, b, _) in enumerate(doan):
            tien_do_js.append(f'tl.fromTo("#td-{k}", {{ scaleX: 0 }}, {{ scaleX: 1, duration: {b - a:.3f}, ease: "none" }}, {a:.3f}); '
                              f'tl.set("#td-ten-{k}", {{ opacity: 1 }}, {a:.3f}); tl.set("#td-ten-{k}", {{ opacity: 0 }}, {b:.3f});')
    sfx_tags = [f'<audio id="sfx-{k}" src="assets/sfx/{f}.mp3" data-start="{round(t, 3)}" data-volume="{v}"></audio>'
                for k, (f, t, v) in enumerate(sorted(sfx, key=lambda e: e[1])) if 0 <= t < total - 0.1]

    audio = [f'<audio id="giong" src="assets/giong.mp3" data-start="0" data-media-start="{t0}" '
             f'data-duration="{total}" data-volume="1"></audio>']

    vertical = h > w
    # Shorts: sân khấu ngang thu nhỏ 0,5625 đặt giữa khung dọc, phụ đề to bên dưới.
    stage_open = ('<div id="san-khau" style="position:absolute;left:0;top:560px;width:1920px;height:1080px;'
                  'transform:scale(0.5625);transform-origin:0 0">') if vertical else ""
    stage_close = "</div>" if vertical else ""
    cap_css = ("bottom: 420px; font-size: 64px; max-width: 980px;" if vertical
               else "bottom: 36px; font-size: 44px; max-width: 1500px;")
    base = theme.cssify((TPL / "base.css").read_text(encoding="utf-8")).replace("1920px", f"{w}px").replace("1080px", f"{h}px")
    nhan0, nen, muc = theme.TH["nhan"][0], theme.TH["nen"], theme.TH["muc"]
    nhan1, nhan2, thanh = theme.TH["nhan"][1], theme.TH["nhan"][2], theme.TH["thanh"]
    vien_toi = float(_render_cfg().get("vien_toi", 0.28))  # viền tối điện ảnh quanh khung; 0 = tắt
    grain_css = (f"\n      #root::after {{ content: ''; position: absolute; inset: 0; background: url(assets/grain.png); "
                 f"opacity: {do_grain}; mix-blend-mode: overlay; pointer-events: none; z-index: 9; }}"
                 if do_grain > 0 else "")
    nen_rgb = ",".join(str(int(nen[i:i + 2], 16)) for i in (1, 3, 5))
    html = f"""<!doctype html>
<html lang="vi">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={w}, height={h}" />
    <script src="{GSAP}"></script>
    <style>
{base}
      #phu-de {{ position: absolute; inset: 0; pointer-events: none; z-index: 10; }}
      .cap {{ position: absolute; left: 0; right: 0; margin: 0 auto; text-align: center; {cap_css} }}
      .dan {{ position: absolute; bottom: 200px; width: 280px; height: 280px; z-index: 6; pointer-events: none; }}
      .dan img {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: contain; }}
      .dan-phai {{ right: 70px; }} .dan-trai {{ left: 70px; }}
      #tien-do {{ position: absolute; left: 0; right: 0; top: 0; height: 60px; z-index: 7; pointer-events: none; }}
      .td-doan {{ position: absolute; top: 0; height: 7px; background: rgba(255,255,255,0.22); border-right: 4px solid {nen}; }}
      .td-day {{ position: absolute; inset: 0; background: {nhan0}; transform-origin: left center; }}
      .td-ten {{ position: absolute; right: 40px; top: 18px; color: #fff; font: 700 26px/1 var(--font-display);
                background: rgba({nen_rgb},0.7); padding: 6px 14px; border-radius: 8px; }}
      .tr {{ position: absolute; inset: 0; z-index: 8; overflow: hidden; pointer-events: none; }}
      .tr-p {{ position: absolute; inset: 0; }}
      .tr-vang-0 {{ background: {nhan2}; }} .tr-vang-1 {{ background: {nhan1}; }} .tr-vang-2 {{ background: {nhan0}; }}
      .tr-muc-0 {{ background: {nhan0}; }} .tr-muc-1 {{ background: {thanh}; }} .tr-muc-2 {{ background: {nen}; }}
      .tr-dip {{ background: #000; opacity: 0; }}
      .tr-iris {{ --r: 1150px; background: {nen};
                 -webkit-mask: radial-gradient(circle at 50% 50%, transparent var(--r), #000 calc(var(--r) + 1px));
                 mask: radial-gradient(circle at 50% 50%, transparent var(--r), #000 calc(var(--r) + 1px)); }}
      .tr-vien {{ position: absolute; left: 50%; top: 50%; width: 2300px; height: 2300px; margin: -1150px 0 0 -1150px;
                 border-radius: 50%; box-shadow: 0 0 0 6px {nhan0}, 0 0 40px 6px {nhan0}; }}
      #vien-toi {{ position: absolute; inset: 0; z-index: 7; pointer-events: none;
                  background: radial-gradient(ellipse 80% 75% at 50% 48%, transparent 58%, rgba(0,0,0,{vien_toi}) 100%); }}
      .cap span {{ display: inline; background: rgba({nen_rgb},0.82); color: {muc}; padding: 6px 16px;
                  border-radius: 10px; font-weight: 700; line-height: 1.5; box-decoration-break: clone;
                  -webkit-box-decoration-break: clone; }}{grain_css}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="{w}" data-height="{h}">
      {stage_open}
      {chr(10).join(hosts)}
      {stage_close}
      {chr(10).join(trs)}
      {'<div id="vien-toi"></div>' if vien_toi > 0 else ""}
      {chr(10).join(dan_tags)}
      {tien_do}
      <div id="phu-de" class="clip" data-start="0" data-duration="{total}" data-track-index="5" data-track-kind="captions">
        {chr(10).join(caps)}
      </div>
      {chr(10).join(audio)}
      {chr(10).join(sfx_tags)}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      {chr(10).join(tr_js)}
      {chr(10).join(dan_js)}
      {chr(10).join(tien_do_js)}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
    (o / "index.html").write_text(html, encoding="utf-8")
    return o


def _probe(path: Path, stream: str | None = None) -> float | None:
    sel = ["-select_streams", stream, "-show_entries", "stream=duration"] if stream else ["-show_entries", "format=duration"]
    r = subprocess.run(["ffprobe", "-v", "error", *sel, "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True, check=True)
    value = r.stdout.strip().splitlines()
    return float(value[0]) if value and value[0] != "N/A" else None


def check_av(video_mp4, audio, tol: float = 0.5) -> list[str]:
    try:
        v = _probe(Path(video_mp4), "v:0")
        a = _probe(Path(video_mp4), "a:0")
        voice = _probe(Path(audio))
    except (subprocess.CalledProcessError, ValueError) as e:
        return [f"Không đọc được thời lượng hình–tiếng: {e}"]
    if v is None or a is None or voice is None:
        return ["Thiếu luồng hình/tiếng trong MP4 hoặc thiếu thời lượng giọng gốc"]
    return [f"Hình {v:.2f} s lệch {label} {t:.2f} s quá {tol} s"
            for label, t in (("tiếng trong MP4", a), ("giọng gốc", voice)) if abs(v - t) > tol]


def contact_sheet(video_mp4, scenes: dict, out_png) -> Path:
    sc = scenes["scenes"]
    cols, rows = min(len(sc), COLS), -(-len(sc) // COLS)
    sheet = Image.new("RGB", (cols * TILE_W, rows * TILE_H), (17, 17, 17))
    with tempfile.TemporaryDirectory() as tmp:
        for k, c in enumerate(sc):
            f = Path(tmp) / f"{k}.png"
            mid = (c["start"] + c["end"]) / 2
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{mid:.3f}", "-i", str(video_mp4), "-frames:v", "1",
                            "-vf", f"scale={TILE_W}:{TILE_H}", str(f)], check=True)
            sheet.paste(Image.open(f), ((k % COLS) * TILE_W, (k // COLS) * TILE_H))
    out = Path(out_png)
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    return out


if __name__ == "__main__" and sys.argv[1:] == ["render-args"]:
    print(" ".join(render_args()))
