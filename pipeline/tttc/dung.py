"""Ghép canh.json + giọng thành dự án HyperFrames, bảng soi hình, kiểm hình–tiếng.

Trường canh.json theo mẫu (ngoài id, mau, start, end):
- chuong:      so (vd "Phần 2"), chuong (tên chương)
- minh-hoa:    svg (tên trong pipeline/svg), nhan, nguon_id?
- so-lon:      so (số), truoc?, sau?, nhan, nguon_id?
- bieu-do:     nhan (tiêu đề), bieu_do{kieu, nhan_x[], gia_tri[], don_vi, noi_bat?, nguon_id}
- nhan-vat:    anh (tệp trong anh/), nhan (tên), vai
- trang-nguon: anh (tệp trong nguon/), khung "x,y,w,h" (%), nguon_id?
"""
import json
import re
import shutil
import subprocess
import tempfile
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import urlparse

from PIL import Image

from tttc.canh import cues

PIPE = Path(__file__).resolve().parent.parent
TPL, SVG, CONFIG = PIPE / "templates" / "canh", PIPE / "svg", PIPE / "config.json"
PREFIX = {"minh-hoa": "mh-", "bieu-do": "bd-", "so-lon": "sl-", "nhan-vat": "nv-", "trang-nguon": "tn-", "chuong": "ch-"}
GSAP = "https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"
NHAC_DB = 0.1  # ≈ −20 dB dưới giọng
TILE_W, TILE_H, COLS = 384, 216, 10


def _read_json(p: Path, default):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default


def _source_line(nguon: dict) -> str:
    host = urlparse(nguon["url"]).netloc.removeprefix("www.")
    d = date.fromisoformat(nguon["ngay_truy_cap"])
    return f"Nguồn: {host}, {d:%d/%m/%Y}"


def _vars(c: dict, by_id: dict, credits: dict) -> dict:
    src = lambda nid: _source_line(by_id[nid]) if nid in by_id else ""
    m = c["mau"]
    if m == "chuong":
        return {"so": c.get("so", ""), "ten": c.get("chuong", "")}
    if m == "minh-hoa":
        return {"svg": f"assets/svg/{c['svg']}.svg", "nhan": c.get("nhan", ""), "nguon": src(c.get("nguon_id"))}
    if m == "so-lon":
        return {"so": c["so"], "truoc": c.get("truoc", ""), "sau": c.get("sau", ""), "nhan": c.get("nhan", ""),
                "nguon": src(c.get("nguon_id"))}
    if m == "bieu-do":
        b = c["bieu_do"]
        return {"tieu_de": c.get("nhan", ""), "nhan_x": json.dumps(b["nhan_x"], ensure_ascii=False),
                "gia_tri": json.dumps(b["gia_tri"]), "don_vi": b.get("don_vi", ""),
                "noi_bat": b.get("noi_bat", -1), "nguon": src(b.get("nguon_id"))}
    if m == "nhan-vat":
        return {"anh": f"assets/anh/{c['anh']}", "ten": c.get("nhan", ""), "vai": c.get("vai", ""),
                "ghi_cong": "Ảnh: " + credits[c["anh"]] if c["anh"] in credits else ""}
    if m == "trang-nguon":
        return {"anh": f"assets/nguon/{c['anh']}", "khung": c.get("khung", "0,0,0,0"), "nguon": src(c.get("nguon_id"))}
    raise ValueError(f"mẫu không có: {m}")


def _scene_file(mau: str, sid: str) -> str:
    s = (TPL / f"{mau}.html").read_text(encoding="utf-8")
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
    i, j = scene_range or (0, len(scenes))
    scenes = scenes[i:j]
    t0 = scenes[0]["start"]
    total = round(scenes[-1]["end"] - t0, 3) if scene_range else timing["duration"]

    o = d / out
    if o.exists():
        shutil.rmtree(o)
    (o / "compositions").mkdir(parents=True)
    shutil.copytree(SVG, o / "assets" / "svg", ignore=shutil.ignore_patterns("*.py", "*.md"))  # cả thư viện: mẫu dùng ảnh mặc định
    for sub in ("anh", "nguon"):
        if (d / sub).exists():
            shutil.copytree(d / sub, o / "assets" / sub)
    shutil.copy(d / "giong.mp3", o / "assets" / "giong.mp3")

    hosts = []
    for c in scenes:
        sid = c["id"]
        (o / "compositions" / f"{sid}.html").write_text(_scene_file(c["mau"], sid), encoding="utf-8")
        vals = json.dumps(_vars(c, by_id, credits), ensure_ascii=False).replace("'", "&#39;")
        hosts.append(f'<div id="{sid}" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html"\n'
                     f'           data-start="{round(c["start"] - t0, 3)}" data-duration="{round(c["end"] - c["start"], 3)}"'
                     f' data-track-index="1" data-track-kind="graphics" data-width="1920" data-height="1080"\n'
                     f"           data-variable-values='{vals}'></div>")

    caps = [f'<div id="cap-{k}" class="clip cap" data-start="{round(a - t0, 3)}" data-duration="{round(b - a, 3)}">'
            f"<span>{escape(t)}</span></div>"
            for k, (a, b, t) in enumerate(cues(timing)) if a >= t0 - 0.01 and b <= t0 + total + 0.01]

    nhac = _read_json(CONFIG, {}).get("nhac_nen")
    audio = [f'<audio id="giong" src="assets/giong.mp3" data-start="0" data-media-start="{t0}" '
             f'data-duration="{total}" data-volume="1"></audio>']
    if nhac:
        shutil.copy(PIPE / nhac, o / "assets" / "nhac.mp3")
        audio.append(f'<audio id="nhac" src="assets/nhac.mp3" data-start="0" data-duration="{total}" '
                     f'data-volume="{NHAC_DB}" data-fade-in="1" data-fade-out="2"></audio>')

    vertical = h > w
    # Shorts: sân khấu ngang thu nhỏ 0,5625 đặt giữa khung dọc, phụ đề to bên dưới.
    stage_open = ('<div id="san-khau" style="position:absolute;left:0;top:560px;width:1920px;height:1080px;'
                  'transform:scale(0.5625);transform-origin:0 0">') if vertical else ""
    stage_close = "</div>" if vertical else ""
    cap_css = ("bottom: 420px; font-size: 64px; max-width: 980px;" if vertical
               else "bottom: 36px; font-size: 44px; max-width: 1500px;")
    base = (TPL / "base.css").read_text(encoding="utf-8").replace("1920px", f"{w}px").replace("1080px", f"{h}px")
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
      .cap span {{ display: inline; background: rgba(17,17,17,0.82); color: #FFFFFF; padding: 6px 16px;
                  border-radius: 10px; font-weight: 700; line-height: 1.5; box-decoration-break: clone;
                  -webkit-box-decoration-break: clone; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="{w}" data-height="{h}">
      {stage_open}
      {chr(10).join(hosts)}
      {stage_close}
      <div id="phu-de" class="clip" data-start="0" data-duration="{total}" data-track-index="5" data-track-kind="captions">
        {chr(10).join(caps)}
      </div>
      {chr(10).join(audio)}
    </div>
    <script>
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
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
    sheet.save(out)
    return out
