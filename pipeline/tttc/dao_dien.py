"""Bước "đạo diễn": kiểm dao-dien.json và sinh canh.json từ đó (phần cơ học: mốc, bố cục đạo cụ, nhịp).

dao-dien.json: {"scenes": [{id, y, nhip_cam_xuc, trong_diem, an_du?, san_khau?, vat_chinh?, dao_cu? [≤ 4 tên], may_quay?,
am_thanh?, dan? {the, huong?, goc?, tu?}, canh: {mau: ..., ...trường của mẫu}}]}; mỗi cảnh một mục theo canh-khung.json.
Chạy: uv run python -m tttc.dao_dien ../videos/<slug>   (ghi canh.json, hinh-thieu.json; canh.json cũ lưu canh-truoc-dao-dien.json)
"""
import copy
import json
import shutil
import sys
from pathlib import Path

from tttc import canh, dung

SVG_DIR = Path(__file__).resolve().parent.parent / "svg"
NHIP_CAM_XUC = {"mo", "leo", "dinh", "dao-chieu", "ha", "chot"}
SLOT = [(0.2, 0.62), (0.8, 0.66), (0.24, 0.3), (0.76, 0.3)]  # vị trí đạo cụ trên sàn, chừa trống vùng giữa cho vật chính


def validate(dd: dict, khung: dict, svg_dir: Path = SVG_DIR) -> list[str]:
    if not isinstance(dd.get("scenes"), list):
        return ['Lỗi: dao-dien.json phải có "scenes": [...] (mỗi cảnh của canh-khung.json một mục)']
    out, ids = [], [c["id"] for c in khung["scenes"]]
    out += [f"Lỗi: một mục trong dao-dien.json thiếu id: {json.dumps(s, ensure_ascii=False)[:60]}"
            for s in dd["scenes"] if not isinstance(s, dict) or "id" not in s]
    dd = {**dd, "scenes": [s for s in dd["scenes"] if isinstance(s, dict) and "id" in s]}
    have = {s["id"] for s in dd["scenes"]}
    out += [f"Lỗi: dao-dien.json thiếu cảnh {i}" for i in ids if i not in have]
    out += [f"Lỗi: dao-dien.json có cảnh {s['id']} không có trong canh-khung.json" for s in dd["scenes"] if s["id"] not in ids]
    stages = canh.san_khau_hop_le(svg_dir)
    for s in dd["scenes"]:
        i, mau = s["id"], (s.get("canh") or {}).get("mau")
        if not s.get("y"):
            out.append(f"Lỗi: {i} thiếu y (người xem phải hiểu hoặc cảm thấy gì)")
        if s.get("nhip_cam_xuc") not in NHIP_CAM_XUC:
            out.append(f"Lỗi: {i} nhip_cam_xuc '{s.get('nhip_cam_xuc')}' không hợp lệ (chọn {', '.join(sorted(NHIP_CAM_XUC))})")
        if not isinstance(s.get("trong_diem"), bool):
            out.append(f"Lỗi: {i} trong_diem phải là true hoặc false")
        if mau not in canh.MAU:
            out.append(f"Lỗi: {i} canh.mau '{mau}' không có")
        if s.get("san_khau", "nen-dat") not in stages:
            out.append(f"Lỗi: {i} san_khau '{s['san_khau']}' không có (chọn {', '.join(sorted(stages))})")
        if s.get("may_quay", "") not in canh.MAY_QUAY:
            out.append(f"Lỗi: {i} may_quay '{s['may_quay']}' không hợp lệ")
        if len(s.get("dao_cu") or []) > 4:
            out.append(f"Lỗi: {i} dao_cu tối đa 4 đạo cụ")
        if s.get("trong_diem") is True:
            if not s.get("an_du"):
                out.append(f"Lỗi: {i} là cảnh trọng điểm nhưng thiếu an_du (ẩn dụ hình và vì sao đúng với nguồn)")
            if mau == "minh-hoa" and s.get("may_quay") in (None, "", "dung"):
                out.append(f"Lỗi: {i} là cảnh trọng điểm minh-hoa nhưng thiếu may_quay khác dung")
    out += [f"Cảnh báo: hình {n} chưa có trong thư viện (đã ghi hinh-thieu.json)" for n in hinh_thieu(dd, svg_dir)]
    return out


def hinh_thieu(dd: dict, svg_dir: Path = SVG_DIR) -> list[str]:
    names = {n for s in dd["scenes"] for n in [s.get("vat_chinh"), *(s.get("dao_cu") or [])] if n}
    return sorted(n for n in names if not (Path(svg_dir) / f"{n}.svg").exists())


def _nhip_tu_dong(words: list[dict], start: float, end: float, n: int) -> list:
    """n cụm 3 từ của lời đọc trong cảnh, bắt đầu ở các vị trí cách đều; ngắn quá thì không điền (mốc mặc định)."""
    ws = [w for w in words if start - 0.01 <= w["start"] < end]
    if len(ws) < 3 + n:
        return [None] * n
    return [" ".join(w["w"] for w in ws[min(round((k + 1) * len(ws) / (n + 1)), len(ws) - 3):][:3]) for k in range(n)]


def sinh_canh(dd: dict, khung: dict, timing: dict) -> dict:
    by, words, out = {s["id"]: s for s in dd["scenes"]}, timing.get("words", []), []
    for k in khung["scenes"]:
        d = by[k["id"]]
        c = {"id": k["id"], "start": k["start"], "end": k["end"], **copy.deepcopy(d["canh"])}
        if c["mau"] == "minh-hoa":
            if d.get("vat_chinh") and "svg" not in c:
                c["svg"] = d["vat_chinh"]
            if d.get("san_khau"):
                c["san_khau"] = d["san_khau"]
            if d.get("may_quay"):
                c["may_quay"] = d["may_quay"]
            if d.get("dao_cu") and "bo_cuc" not in c and "phu" not in c:
                c["bo_cuc"] = [{"svg": n, "x": SLOT[i][0], "y": SLOT[i][1], "to": 1.0} for i, n in enumerate(d["dao_cu"][:4])]
        if d.get("dan"):
            c["dan"] = d["dan"]
        if d.get("trong_diem"):
            c["trong_diem"] = True  # dung.dan_cua cho Nhịp ló ra ở cảnh số trọng điểm
        n = len(dung.DEFAULT_STEPS.get(c["mau"], []))
        if n and "nhip" not in c:
            c["nhip"] = _nhip_tu_dong(words, k["start"], k["end"], n)
        out.append(c)
    return {"scenes": out}


def main(video_dir: str) -> int:
    d = Path(video_dir)
    rd = lambda n: json.loads((d / n).read_text(encoding="utf-8"))
    try:
        dd, khung, timing = rd("dao-dien.json"), rd("canh-khung.json"), rd("giong-timing.json")
    except FileNotFoundError as e:
        print(f"Lỗi: thiếu {Path(e.filename).name} (canh-khung.json do `tttc.chia` sinh, giong-timing.json do bước giong)")
        return 1
    msgs = validate(dd, khung, SVG_DIR)
    for m in msgs:
        print("-", m)
    if any(m.startswith("Lỗi") for m in msgs):
        print("Có Lỗi: không ghi canh.json")
        return 1
    if (d / "canh.json").exists():
        shutil.copy(d / "canh.json", d / "canh-truoc-dao-dien.json")
    (d / "canh.json").write_text(json.dumps(sinh_canh(dd, khung, timing), ensure_ascii=False, indent=1), encoding="utf-8")
    thieu = hinh_thieu(dd, SVG_DIR)
    (d / "hinh-thieu.json").write_text(json.dumps(thieu, ensure_ascii=False), encoding="utf-8")
    td = sum(bool(s.get("trong_diem")) for s in dd["scenes"])
    print(f"{len(dd['scenes'])} cảnh, {td} cảnh trọng điểm ({td / len(dd['scenes']):.0%}), {len(thieu)} hình còn thiếu")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
