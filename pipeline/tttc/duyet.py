"""Trang duyệt HTML tĩnh cho 2 điểm duyệt của người."""
import json
import re
from html import escape
from pathlib import Path
from string import Template

from tttc import chat_luong, dang, phong_cach, theme, thumb, tieu_de, trang_thai
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
        if n["trang_thai"] == "tu-tinh":
            trich = f'Tự tính: {n.get("cong_thuc", "")} (từ {", ".join("#" + i for i in n.get("dau_vao", []))})'
        else:
            trich = n["trich_dan"]
        url = f'<a href="{escape(n["url"])}">{escape(n["url"])}</a>' if n.get("url") else "—"
        rows.append(
            f'<tr><td class="tag">#{escape(n["id"])}</td><td>{escape(n["gia_tri"])}</td>'
            f'<td>{escape(trich)}</td><td>{url}</td>'
            f'<td>{escape(n.get("ngay_truy_cap", "—"))}</td><td class="st-{escape(n["trang_thai"])}">'
            f'{escape(n["trang_thai"])}</td><td>{shot}</td></tr>')
    return ('<div class="scroll"><table><tr><th>ID</th><th>Giá trị</th><th>Trích dẫn</th><th>URL</th>'
            '<th>Ngày</th><th>Trạng thái</th><th>Chụp</th></tr>' + "".join(rows) + "</table></div>")


def _script_html(md: str) -> str:
    return "<pre>" + re.sub(r"\[#([\w-]+)\]", r'<span class="tag">[#\1]</span>', escape(md)) + "</pre>"


def _page(video_dir: Path, name: str, title: str, meta: str, body: str) -> Path:
    out = video_dir / name
    out.write_text(Template(theme.cssify(TEMPLATE.read_text(encoding="utf-8"))).substitute(
        title=escape(title), meta=escape(meta), body=body), encoding="utf-8", newline="\n")
    return out


def _phan_bien(d: Path, note: str) -> str:
    links = "".join(f' <a href="{n}">{n}</a>' for n in ("phan-bien-giong-1.md", "phan-bien-giong-2.md")
                    if (d / n).exists())
    red = ('<div class="canh-bao do"><strong>agy lỗi</strong>: phản biện giọng văn do subagent thay thế, xem kỹ.</div>'
           if "agy lỗi" in note else "")
    audio = ('<h2>Nghe thử 60 giây</h2><audio controls src="nghe-thu.mp3"></audio>'
             if (d / "nghe-thu.mp3").exists() else "")
    return f'{red}<div class="phan-bien"><h2>Phản biện giọng văn</h2><p>{escape(note)}{links}</p></div>{audio}'


def render_review_1(video_dir) -> Path:
    d = Path(video_dir)
    nguon = json.loads(_read(d / "nguon.json", "[]"))
    script = _read(d / "kich-ban.md")
    buoc = trang_thai.load(d)["steps"]["phan-bien-giong"]
    if buoc["status"] != "xong":
        raise ValueError("chưa phản biện giọng văn với agy (2 vòng): chạy tttc.phan_bien vong 1 rồi vong 2")
    loi_giong = [m for m in phong_cach.kiem(script) if m.startswith("Lỗi")]
    if loi_giong:
        raise ValueError(f"giọng văn còn {len(loi_giong)} Lỗi: " + "; ".join(loi_giong))
    cfg = json.loads(phong_cach.CONFIG.read_text(encoding="utf-8")) if phong_cach.CONFIG.exists() else {}
    wpm = float(cfg.get("vieneu", {}).get("wpm_du_kien") or 145)
    warns = (
        check(script, nguon)
        + phong_cach.kiem(script, check_cta=True, check_dai_chung=True)
        + phong_cach.kiem_loai_bai_chinh(script)
        + phong_cach.kiem_thoi_luong_thuc(script, wpm=wpm)
    )
    body = (_warnings(warns)
            + _phan_bien(d, buoc["note"])
            + "<h2>Chủ đề</h2><pre>" + escape(_read(d / "chu-de.md")) + "</pre>"
            + "<h2>Số → nguồn</h2>" + _sources_table(nguon)
            + "<h2>Kịch bản</h2>" + _script_html(script))
    return _page(d, "duyet-1.html", f"Duyệt 1 · {d.name}",
                 "Kiểm từng số với nguồn, rồi trả lời 'duyệt' hoặc ghi chỗ cần sửa.", body)


def render_review_2(video_dir) -> Path:
    d = Path(video_dir)
    nguon = json.loads(_read(d / "nguon.json", "[]"))
    goi = json.loads(_read(d / "dong-goi.json", "{}"))
    warns = check(_read(d / "kich-ban.md"), nguon)
    warns += [f"Nguồn [#{n['id']}] là số sơ bộ ({n['gia_tri']}): video phải nói rõ 'sơ bộ'"
              for n in nguon if n["trang_thai"] == "so-bo"]
    giay = dang.thoi_luong(d / "final.mp4")
    if giay is not None and giay < dang.DAI_TOI_THIEU:
        warns.append(f"Lỗi: Video dài {dang.mmss(giay)} < {dang.mmss(dang.DAI_TOI_THIEU)} – cổng đăng sẽ từ chối dạng video dài; "
                     "nên cắt thành Shorts, hoặc khi đăng ghi --cho-phep-ngan \"<lý do>\"")
    if (d / "canh.json").exists() and (d / "giong-timing.json").exists():
        dd, cham = d / "dao-dien.json", d / "dao-dien-cham.json"
        warns += chat_luong.kiem(chat_luong.do(json.loads(_read(d / "canh.json")), json.loads(_read(d / "giong-timing.json")),
                                               json.loads(_read(dd)) if dd.exists() else None,
                                               json.loads(_read(cham)) if cham.exists() else None,
                                               chat_luong.doc_ghi_cong(d)))
    opts_html = []
    for i, o in enumerate(goi.get("phuong_an", []), 1):
        kq = tieu_de.cham_diem(o["tieu_de"])
        for msg in [*kq.loi, *kq.canh_bao, *tieu_de.kiem_khop_nguon(o["tieu_de"], nguon)]:
            warns.append(f"Phương án {i}: {msg}")
        if o.get("khuon") != thumb.KHUON:
            warns.append(f"Phương án {i}: Lỗi: thumbnail không theo khuôn đã khóa «{thumb.KHUON}» "
                         f"(đang ghi: {o.get('khuon') or 'không ghi'}); dựng lại bằng thumb.ho_so")
        dong_dai = [line for line in o.get("chu_thumb", []) if len(line.split()) > 4]
        if dong_dai:
            warns.append(f"Phương án {i}: Chữ thumbnail dài quá 4 từ ({', '.join(dong_dai)}) — nên rút gọn ≤ 3 từ/dòng")
        opts_html.append(
            f'<div class="opt"><strong>Phương án {i}</strong><img src="{escape(o["file_thumb"])}" alt="">'
            f'<p>{escape(o["tieu_de"])}</p><p class="meta">Chữ thumbnail: {escape(" / ".join(o.get("chu_thumb", [])))} · '
            f'Điểm tiêu đề: {kq.diem}/10</p></div>')
    opts = "".join(opts_html)
    shorts = "".join(
        f'<div class="opt"><video controls src="{escape(s["file"])}"></video><p>{escape(s["tieu_de"])}</p>'
        f'<p class="meta">Đăng {escape(s["ngay"])} {escape(s["gio"])}</p></div>' for s in goi.get("shorts", []))
    mo_ta_hien = dang.gan_hashtag(goi.get("mo_ta", ""), goi.get("tags", []))
    body = (_warnings(warns)
            + '<h2>Video</h2><video controls src="final.mp4"></video>'
            + f'<h2>Tiêu đề + thumbnail</h2><div class="opts">{opts}</div>'
            + f'<h2>Shorts</h2><div class="opts">{shorts}</div>'
            + "<h2>Mô tả</h2><pre>" + escape(mo_ta_hien) + "</pre>"
            + "<h2>Tags</h2><pre>" + escape(", ".join(goi.get("tags", []))) + "</pre>")
    return _page(d, "duyet-2.html", f"Duyệt 2 · {d.name}",
                 "Xem video, chọn phương án 1/2/3, rồi trả lời 'duyệt phương án N' hoặc ghi chỗ cần sửa.", body)
