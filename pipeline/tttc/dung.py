"""Ghép canh.json + giọng thành dự án HyperFrames, bảng soi hình, kiểm hình–tiếng.

Trường canh.json theo mẫu (ngoài id, mau, start, end; mọi cảnh có thể ghi đè nen: toi|kem|vang):
- chuong:      so (vd "Phần 2"), chuong (tên chương)
- minh-hoa:    svg (tên trong pipeline/svg), phu? [tối đa 2 đạo cụ], nhan, nguon_id?, dong? bob|xoay|dap|chop (mặc định bob),
               san_khau? (phông: nen-dat mặc định, hoặc phần sau "phong-" của svg/phong-*.svg), bo_cuc? [1–4 {svg, x, y, to}] (thay phu;
               x,y 0–1 trên sàn, to 0,2–1,5), may_quay? dung|day-vao|keo-ra|lia|he-lo
- so-lon:      so (số hoặc chuỗi "5,3"), truoc?, sau?, nhan, nguon_id, svg? (hình nền mờ), huong? len|xuong, dong? (như minh-hoa, mặc định không)
- bieu-do:     nhan (tiêu đề), bieu_do{kieu, nhan_x[], gia_tri[], don_vi, noi_bat?, chu_thich?, nguon_id (một id hoặc danh sách)}
- nhan-vat:    anh (tệp trong anh/), nhan (tên), vai
- trang-nguon: anh (tệp trong nguon/), khung "x,y,w,h" (% vùng trang), nguon_id
- trich-bao:   nguon_id, trich (nguyên văn một đoạn trong trich_dan, ≤ 25 từ), to_vang (cụm trong trich)
- quy-trinh:   tieu_de?, buoc [3–6 phần tử {nhan, svg?}], noi_bat? (chỉ số bước), nguon_id?, dong? (cho bước nổi bật, mặc định dap)
- so-sanh:     trai, phai {nhan, svg, so?, don_vi?, to? (0–1, cỡ hình tương đối)}, don_vi?, ti_le? ("gấp ~700 lần"),
               nguon_id (bắt buộc nếu có so), dong? (cho huy hiệu VS, mặc định dap)
- thoi-gian:   tieu_de?, truc {tu, den, don_vi}, hang [2–5 phần tử {nhan, tu, den, noi_bat?}], nguon_id (năm phải có trong nguồn)
- b-roll:      video (tệp trong broll/, tải bằng tttc.broll), nhan, so? ("01")
Mọi mẫu: nhip? [cụm từ trong lời đọc của cảnh, theo thứ tự bước của mẫu – xem DEFAULT_STEPS]; null giữ mốc mặc định.
Nền tự gán: chương vàng, nhân vật kem, còn lại tối/kem đổi theo chương. Chuyển cảnh tự gán (transitions()).
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

from tttc import grain, theme
from tttc.canh import cues, phrase_time
from tttc.kiem import vi_value
from tttc.tron_am import tron

PIPE = Path(__file__).resolve().parent.parent
TPL, SVG, CONFIG = PIPE / "templates" / "canh", PIPE / "svg", PIPE / "config.json"
SFX = PIPE / "am-thanh" / "sfx"
PREFIX = {"minh-hoa": "mh-", "bieu-do": "bd-", "so-lon": "sl-", "nhan-vat": "nv-", "trang-nguon": "tn-",
          "chuong": "ch-", "trich-bao": "tb-", "b-roll": "br-", "quy-trinh": "qt-", "so-sanh": "ss-", "thoi-gian": "tg-"}
# Mốc mặc định (giây tính từ đầu cảnh) của các bước trong mỗi mẫu, theo thứ tự canh.json:nhip.
DEFAULT_STEPS = {
    "minh-hoa": [0.72, 0.5, 0.58],     # nhãn, đạo cụ 1, đạo cụ 2
    "so-lon": [0.05, 1.6],             # bắt đầu đếm, dòng dưới
    "trang-nguon": [0.8],              # zoom vào số
    "nhan-vat": [0.8],                 # thẻ vai trò
    "so-sanh": [0.5, 1.1, 1.8],        # bên trái, bên phải (+VS), nhãn tỉ lệ
    "chuong": [],
    "trich-bao": [0.9],                # tô vàng
    "b-roll": [0.5],                   # nhãn chương
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


def _vars(c: dict, by_id: dict, credits: dict, broll_credits: dict | None = None) -> dict:
    broll_credits = broll_credits or {}
    src = lambda nid: " · ".join(_source_line(by_id[n]) for n in (nid if isinstance(nid, list) else [nid])
                                 if n in by_id)
    m = c["mau"]
    if m == "chuong":
        return {"so": c.get("so", ""), "ten": c.get("chuong", "")}
    if m == "minh-hoa":
        phu = c.get("phu", [])
        sk = c.get("san_khau", "nen-dat")
        return {"svg": f"assets/svg/{c['svg']}.svg", "nhan": c.get("nhan", ""), "nguon": src(c.get("nguon_id")),
                "phu1": f"assets/svg/{phu[0]}.svg" if len(phu) > 0 else "",
                "phu2": f"assets/svg/{phu[1]}.svg" if len(phu) > 1 else "", "dong": c.get("dong", "bob"),
                "phong": f"assets/svg/{'nen-dat' if sk == 'nen-dat' else 'phong-' + sk}.svg",
                "bo_cuc": json.dumps([{**b, "svg": f"assets/svg/{b['svg']}.svg"} for b in c.get("bo_cuc", [])],
                                     ensure_ascii=False),
                "may_quay": c.get("may_quay") or "dung", "thoi_luong": round(c.get("end", 0) - c.get("start", 0), 3)}
    if m == "so-lon":
        return {"so": _num(c["so"]), "so_hien": vi_number(c["so"]), "truoc": c.get("truoc", ""),
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
                "tieu_de": c["trich"], "to_vang": c.get("to_vang", "")}
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
    if m == "b-roll":
        return {"nhan": c.get("nhan", ""), "so": c.get("so", ""), "ghi_cong": broll_credits.get(c["video"], "")}
    raise ValueError(f"mẫu không có: {m}")


def steps(c: dict, words: list[dict]) -> list[float]:
    """Mốc từng bước của cảnh: từ khoá trong nhip (khớp giọng đọc) hoặc mặc định của mẫu."""
    if c["mau"] == "bieu-do":
        n = len(c["bieu_do"]["gia_tri"])
        base = [0.4 + i * 0.18 for i in range(n)] + [0.4 + n * 0.18 + 0.5]
    elif c["mau"] == "quy-trinh":
        base = [round(0.5 + 0.55 * i, 3) for i in range(len(c["buoc"]))]
    elif c["mau"] == "thoi-gian":
        base = [round(0.5 + 0.6 * i, 3) for i in range(len(c["hang"]))]
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
    if m == "so-sanh":
        return [("pop", st[0], 0.3), ("pop", st[1], 0.3)] + ([("chime", st[2] + 0.1, 0.3)] if c.get("ti_le") else [])
    if m == "trang-nguon":
        return [("whoosh-short", st[0], 0.3)]
    if m == "nhan-vat":
        return [("whoosh-short", 0.05, 0.25)]
    if m == "trich-bao":
        return [("click-soft", st[0], 0.35)]
    return []


def grounds(scenes: list[dict]) -> list[str]:
    """Nền mỗi cảnh: chương vàng, nhân vật kem, còn lại đổi tối/kem theo chương chẵn/lẻ; canh.json ghi đè được."""
    out, chap = [], 0
    for c in scenes:
        if c["mau"] == "chuong":
            chap += 1
        auto = "vang" if c["mau"] == "chuong" else "kem" if c["mau"] == "nhan-vat" else ("kem" if chap % 2 else "toi")
        out.append(c.get("nen") or auto)
    return out


def transitions(scenes: list[dict]) -> list[tuple[int, str]]:
    """(chỉ số cảnh sau đường nối, kiểu): vào chương quét vàng, rời chương quét mực, cứ 3 đường nối có 1 lần chớp tối."""
    out = []
    for k in range(1, len(scenes)):
        a, b = scenes[k - 1]["mau"], scenes[k]["mau"]
        kind = "vang" if b == "chuong" else "muc" if a == "chuong" else "dip" if k % 3 == 0 else ""
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
    nhac = _read_json(CONFIG, {}).get("nhac_nen")
    if nhac and not (PIPE / nhac).is_file():
        raise FileNotFoundError(f"Không thấy nhạc nền {nhac} (config.json:nhac_nen)")
    if nhac:  # nhạc trộn sẵn vào một bản giọng: tự hạ khi có tiếng (tron_am), Shorts cắt cùng một tệp
        tron(d / "giong.mp3", PIPE / nhac, o / "assets" / "giong.mp3")
    else:
        shutil.copy(d / "giong.mp3", o / "assets" / "giong.mp3")
    shutil.copytree(SFX, o / "assets" / "sfx")
    do_grain = float(_render_cfg().get("grain") or 0)
    if do_grain > 0:  # hạt nhiễu mịn chống banding: PNG xám phủ overlay với độ mờ thấp
        grain.tao_grain(o / "assets" / "grain.png")

    hosts = []
    sfx = []
    for idx, (c, nen) in enumerate(zip(scenes, nens)):
        sid = c["id"]
        (o / "compositions" / f"{sid}.html").write_text(_scene_file(c["mau"], sid, c.get("video", "")), encoding="utf-8")
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
        cls = "tr-dip" if kind == "dip" else f"tr-{kind}"
        if kind != "dip":
            sfx.append(("whoosh-short", seam - 0.3, 0.35))
        trs.append(f'<div id="tr-{k}" class="clip tr" data-start="{a}" data-duration="0.6" data-track-index="4">'
                   f'<div id="tr-{k}-p" class="tr-p {cls}"></div></div>')
        if kind == "dip":  # tối nhanh 3 khung trước cú cắt rồi sáng lại
            tr_js.append(f'tl.fromTo("#tr-{k}-p", {{ opacity: 0 }}, {{ opacity: 0.6, duration: 0.1 }}, {seam - 0.1:.3f}); '
                         f'tl.to("#tr-{k}-p", {{ opacity: 0, duration: 0.15 }}, {seam:.3f});')
        else:  # tấm màu quét qua che cú cắt
            tr_js.append(f'tl.fromTo("#tr-{k}-p", {{ xPercent: -101 }}, {{ xPercent: 0, duration: 0.3, ease: "power3.in" }}, {a:.3f}); '
                         f'tl.to("#tr-{k}-p", {{ xPercent: 101, duration: 0.3, ease: "power3.out" }}, {seam:.3f});')

    caps = [f'<div id="cap-{k}" class="clip cap" data-start="{round(a - t0, 3)}" data-duration="{round(b - a, 3)}">'
            f"<span>{escape(t)}</span></div>"
            for k, (a, b, t) in enumerate(cues(timing)) if a >= t0 - 0.01 and b <= t0 + total + 0.01]

    dan_tags, dan_js = [], []
    if h <= w:  # shortcut: Shorts (khung dọc) chưa có nhân vật; thêm khi có nhu cầu
        for k, c in enumerate(scenes):
            d = c.get("dan")
            if not d:
                continue
            a, dur = round(c["start"] - t0, 3), round(c["end"] - c["start"], 3)
            ra = phrase_time(timing.get("words", []), d["tu"], c["start"], c["end"]) if d.get("tu") else None
            vao = round(a + (ra - c["start"] if ra is not None else 0.3), 3)
            the = d["the"]
            dan_tags.append(
                f'<div id="dan-{k}" class="clip dan dan-{d.get("goc", "phai")}" data-start="{a}" data-duration="{dur}" '
                f'data-track-index="3"><img src="assets/svg/tui-{the}.svg" alt="">'
                f'<img id="dan-{k}-nham" src="assets/svg/tui-{the}-nham.svg" alt="" style="opacity:0"></div>')
            dan_js.append(f'tl.fromTo("#dan-{k}", {{ scale: 0, y: 40, transformOrigin: "50% 100%" }}, '
                          f'{{ scale: 1, y: 0, duration: 0.45, ease: "back.out(2)" }}, {vao});')
            dan_js.append(f'tl.to("#dan-{k}", {{ y: -10, duration: 1.2, ease: "sine.inOut", yoyo: true, '
                          f'repeat: {max(0, int((a + dur - vao - 0.5) / 1.2) - 1)} }}, {vao + 0.5:.3f});')  # hữu hạn, đủ phủ hết cảnh
            t = vao + 1.8
            while t < a + dur - 0.3:  # chớp mắt: ảnh nhắm mắt phủ lên ảnh mở mắt (cùng hình dáng) trong 0,14 s
                dan_js.append(f'tl.set("#dan-{k}-nham", {{ opacity: 1 }}, {t:.3f}); '
                              f'tl.set("#dan-{k}-nham", {{ opacity: 0 }}, {t + 0.14:.3f});')
                t += 2.8
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
      .tr {{ position: absolute; inset: 0; z-index: 8; overflow: hidden; pointer-events: none; }}
      .tr-p {{ position: absolute; inset: 0; }}
      .tr-vang {{ background: {nhan0}; }} .tr-muc {{ background: {nen}; }} .tr-dip {{ background: #000; opacity: 0; }}
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
      {chr(10).join(dan_tags)}
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
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
    (o / "index.html").write_text(html, encoding="utf-8")
    return o


def _probe(path: Path, stream: str | None = None) -> float:
    sel = ["-select_streams", stream, "-show_entries", "stream=duration"] if stream else ["-show_entries", "format=duration"]
    r = subprocess.run(["ffprobe", "-v", "error", *sel, "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip().splitlines()[0])


def check_av(video_mp4, audio, tol: float = 0.5) -> list[str]:
    v, a = _probe(Path(video_mp4), "v:0"), _probe(Path(audio))
    return [] if abs(v - a) <= tol else [f"Hình {v:.2f} s lệch tiếng {a:.2f} s quá {tol} s"]


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
