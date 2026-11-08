"""Trang duyệt HTML tĩnh cho 2 điểm duyệt của người."""
import json
import re
from html import escape
from pathlib import Path
from string import Template

from tttc.kiem import check

TEMPLATE = Path(__file__).resolve().parent.parent / "templates" / "duyet.html"


def _read(p: Path, default: str = "") -> str:
    return p.read_text(encoding="utf-8") if p.exists() else default


def _warnings(errs: list[str]) -> str:
    if not errs:
        return ""
    items = "".join(f"<li>{escape(e)}</li>" for e in errs)
    return f'<div class="canh-bao"><strong>{len(errs)} cảnh báo</strong><ul>{items}</ul></div>'


def _sources_table(nguon: list[dict]) -> str:
    rows = []
    for n in nguon:
        shot = f'<a href="{escape(n["anh_chup"])}">ảnh</a>' if n.get("anh_chup") else "—"
        rows.append(
            f'<tr><td class="tag">#{escape(n["id"])}</td><td>{escape(n["gia_tri"])}</td>'
            f'<td>{escape(n["trich_dan"])}</td><td><a href="{escape(n["url"])}">{escape(n["url"])}</a></td>'
            f'<td>{escape(n["ngay_truy_cap"])}</td><td class="st-{escape(n["trang_thai"])}">'
            f'{escape(n["trang_thai"])}</td><td>{shot}</td></tr>')
    return ('<div class="scroll"><table><tr><th>ID</th><th>Giá trị</th><th>Trích dẫn</th><th>URL</th>'
            '<th>Ngày</th><th>Trạng thái</th><th>Chụp</th></tr>' + "".join(rows) + "</table></div>")


def _script_html(md: str) -> str:
    return "<pre>" + re.sub(r"\[#([\w-]+)\]", r'<span class="tag">[#\1]</span>', escape(md)) + "</pre>"


def _page(video_dir: Path, name: str, title: str, meta: str, body: str) -> Path:
    out = video_dir / name
    out.write_text(Template(TEMPLATE.read_text(encoding="utf-8")).substitute(
        title=escape(title), meta=escape(meta), body=body), encoding="utf-8")
    return out


def render_review_1(video_dir) -> Path:
    d = Path(video_dir)
    nguon = json.loads(_read(d / "nguon.json", "[]"))
    script = _read(d / "kich-ban.md")
    body = (_warnings(check(script, nguon))
            + "<h2>Chủ đề</h2><pre>" + escape(_read(d / "chu-de.md")) + "</pre>"
            + "<h2>Số → nguồn</h2>" + _sources_table(nguon)
            + "<h2>Kịch bản</h2>" + _script_html(script))
    return _page(d, "duyet-1.html", f"Duyệt 1 · {d.name}",
                 "Kiểm từng số với nguồn, rồi trả lời 'duyệt' hoặc ghi chỗ cần sửa.", body)
