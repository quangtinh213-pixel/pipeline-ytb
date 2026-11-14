"""Cổng đo chất lượng theo chuẩn kênh mẫu (docs/nghien-cuu/kenh-mau-motcongnghe-2026-11-09.md mục 4).

Chạy trước khi render (render mất cả giờ): uv run python -m tttc.chat_luong ../videos/<slug>
"""
import json
import sys
from pathlib import Path

from tttc import dung

NHOM = {
    "do-hoa": {"minh-hoa", "quy-trinh", "so-sanh", "thoi-gian", "so-lon", "bieu-do", "chuong", "ban-do", "xep-hang",
               "chu-dong", "phan-tram", "mo-dau", "ket-thuc"},
    "bang-chung": {"trich-bao", "trang-nguon"},
    "doi-that": {"b-roll", "nhan-vat"},
}
# user chốt 14/11/2026 (docs/nghien-cuu/cach-doi-thu-dung-video-2026-11-14.md mục 6, P0): đối thủ 88–92% đồ họa,
# 0% stock chung chung; thay chuẩn 10/11 (≥ 45% đời thật). Sau 60 s được giữ một sân khấu lâu nếu bồi dần đủ dày.
MUC_TIEU = {
    "tb_giay": (2.8, 12.0), "duoi_1_5_max": 0, "tren_8_max": 0.03, "do_hoa_min": 0.70, "stock_max": 0.10,
    "bang_chung": (0.08, 0.35),  # user 11/11/2026: muốn nhiều ảnh chụp bài báo hơn, nới trần từ 18%
    "san_khau_tu": 60.0, "san_khau_su_kien_phut": 20, "chay_max": 2,
    "su_kien_phut_min": 30, "sfx_phut_min": 15, "toc_do": (180, 265)  # từ/phút; tiếng Việt tính theo âm tiết: kênh mẫu đo 196–222,
}
# Chỉ số "độ khô" (spec 2026-11-09-chat-luong-hinh-anh-design.md mục 7): cảnh báo, hiệu chỉnh sau chạy khô.
MUC_TIEU["do_kho"] = {"phong_min": 5, "phong_lien_max": 2, "lap_max": 0, "may_quay_min": 0.15, "cham_min": 3,
                      "cham_tb_min": 4.0}
NHIP_CAM_XUC_DU = {"mo", "dinh", "dao-chieu", "chot"}
EMPTY = "Lỗi: canh.json không có cảnh nào"
STOCK = ("pexels", "pixabay")  # kho clip chung; ảnh báo/hãng/user và "Minh họa" không tính


def doc_ghi_cong(video_dir: Path) -> dict | None:
    """broll/ghi-cong.json → {tệp: dòng ghi công}; chưa có thì None (bỏ qua đo stock)."""
    f = Path(video_dir) / "broll" / "ghi-cong.json"
    return {x["tep"]: x["ghi_cong"] for x in json.loads(f.read_text(encoding="utf-8"))} if f.exists() else None


def _buoc(c: dict, words: list[dict]) -> list[float]:
    try:
        return dung.steps(c, words)
    except KeyError:  # shortcut: mẫu chưa khai báo bước thì tính 0 bước; canh.validate báo mẫu lạ riêng
        return []


def do_kho(canh: dict, dao_dien: dict | None = None, cham: dict | None = None) -> dict:
    """Đo độ khô: đa dạng phông, hình chính lặp, camera; có dao-dien.json thì thêm cảnh trọng điểm và nhịp cảm xúc;
    có dao-dien-cham.json (điểm giám khảo 1–5) thì thêm điểm."""
    sc = canh["scenes"]
    mh = [c for c in sc if c["mau"] == "minh-hoa"]
    phong = [c.get("san_khau", "nen-dat") if c["mau"] == "minh-hoa" else None for c in sc]
    chay = best = 0
    prev = None
    for p in phong:
        chay = 0 if p is None else chay + 1 if p == prev else 1
        best, prev = max(best, chay), p
    lap = sum(c["mau"] == "minh-hoa" and bool(c.get("svg")) and
              any(x["mau"] == "minh-hoa" and x.get("svg") == c["svg"] for x in sc[max(0, i - 7):i])
              for i, c in enumerate(sc))
    clip_lap = sum(c["mau"] == "b-roll" and bool(c.get("video")) and
                   any(x["mau"] == "b-roll" and x.get("video") == c["video"] for x in sc[max(0, i - 7):i])
                   for i, c in enumerate(sc))
    canh_tinh_dai = sum(c.get("mau") in ("minh-hoa", "so-lon", "bieu-do", "so-sanh", "quy-trinh") and
                        (c.get("end", 0) - c.get("start", 0)) > 4.5 and
                        not c.get("nhip") and c.get("may_quay") in (None, "", "dung")
                        for c in sc)
    out = {"so_phong": len(set(phong) - {None}), "so_canh_minh_hoa": len(mh), "phong_lien_max": best,
           "vat_chinh_lap": lap, "clip_lap": clip_lap, "canh_tinh_dai": canh_tinh_dai,
           "ti_le_may_quay": sum(c.get("may_quay") not in (None, "", "dung") for c in mh) / len(mh) if mh else 0.0}
    if dao_dien is not None:
        mau = {c["id"]: c["mau"] for c in sc}
        thieu = 0
        for d in dao_dien["scenes"]:
            if d.get("trong_diem"):
                can_camera = mau.get(d["id"]) == "minh-hoa" and d.get("may_quay") in (None, "", "dung")
                thieu += not d.get("an_du") or can_camera
        out["trong_diem_thieu"] = thieu
        out["nhip_cam_xuc_du"] = NHIP_CAM_XUC_DU <= {d.get("nhip_cam_xuc") for d in dao_dien["scenes"]}
    if cham is not None:
        diem = [v for b in cham["beats"] for v in (b["y_nghia"], b["da_dang"], b["chieu_sau"], b["nhip"])]
        out["cham_thap"] = sum(min(b["y_nghia"], b["da_dang"], b["chieu_sau"], b["nhip"]) < 3 for b in cham["beats"])
        out["cham_tb"] = sum(diem) / len(diem) if diem else 0.0
    return out


def do(canh: dict, timing: dict, dao_dien: dict | None = None, cham: dict | None = None,
       ghi_cong: dict | None = None) -> dict:
    sc = canh["scenes"]
    words = timing.get("words", [])
    n = len(sc)
    if not n:
        return {"so_canh": 0}
    durs = [c["end"] - c["start"] for c in sc]
    dau_30 = [c["end"] - c["start"] for c in sc if c.get("start", 0) < 30.0]
    tb_giay_30s = sum(dau_30) / len(dau_30) if dau_30 else 0.0
    phut = max((sc[-1]["end"] - sc[0]["start"]) / 60, 1e-9)
    ti_le = {g: sum(c["mau"] in maus for c in sc) / n for g, maus in NHOM.items()}
    chay = best = 0
    prev = None
    for c in sc:
        chay = chay + 1 if c["mau"] == prev and c["mau"] != "b-roll" else 1  # b-roll liền nhau là clip khác nhau
        best, prev = max(best, chay), c["mau"]
    steps = [_buoc(c, words) for c in sc]
    sfx = sum(len(dung.sfx_events(c, st)) for c, st in zip(sc, steps))
    # b-roll chỉ tính bước thật sự hiện: nhãn, từ khoá, khung chia
    steps = [[t for t, co in zip(st, (c.get("nhan"), c.get("tu_khoa"), c.get("chia"))) if co] if c["mau"] == "b-roll" else st
             for c, st in zip(sc, steps)]
    sfx += sum(kind != "dip" for _, kind in dung.transitions(sc))
    boi = [len(c.get("boi") or []) for c in sc]  # nhãn bồi dần: mỗi nhãn một sự kiện hình và một tiếng pop
    sfx += sum(boi)
    steps = [st + [0.0] * b for st, b in zip(steps, boi)]
    dan = [1 if dung.dan_cua(c) else 0 for c in sc]
    m = MUC_TIEU
    # cảnh > 8 s chỉ bị tính là chậm nếu trong 60 s đầu hoặc bồi chưa đủ dày (sự kiện/phút của riêng cảnh)
    tren_8 = sum(d > 8 and (c["start"] < m["san_khau_tu"] or (1 + len(st) + dn) / d * 60 < m["san_khau_su_kien_phut"])
                 for c, d, st, dn in zip(sc, durs, steps, dan))
    dau = sc[0]  # khung đầu phải có chữ hoặc số để giữ người xem (user duyệt 12/11/2026)
    mo_dau = dau["mau"] in {"so-lon", "so-sanh", "trich-bao", "bieu-do", "trang-nguon", "xep-hang", "phan-tram", "chu-dong"} or (
        dau["mau"] == "b-roll" and bool(dau.get("tu_khoa") or dau.get("chia")))
    return {"so_canh": n, "tb_giay": sum(durs) / n, "tb_giay_30s": tb_giay_30s, "duoi_1_5": sum(d < 1.5 for d in durs),
            "tren_8": tren_8, "ti_le": ti_le, "chay_dai_nhat": best,
            "su_kien_phut": (n + sum(map(len, steps)) + sum(dan)) / phut, "sfx_phut": sfx / phut,
            "toc_do": len(words) / phut, "mo_dau": mo_dau, "do_kho": do_kho(canh, dao_dien, cham),
            **_stock(sc, ghi_cong)}


def _stock(sc: list[dict], ghi_cong: dict | None) -> dict:
    if ghi_cong is None:
        return {}
    gc = [ghi_cong.get(c.get("video", ""), "").lower() for c in sc if c["mau"] == "b-roll"]
    stock = sum(any(k in g for k in STOCK) for g in gc)
    return {"ti_le_stock": stock / len(sc), "anh_su_kien": sum(bool(g) and not any(k in g for k in STOCK)
                                                               and "minh họa" not in g for g in gc)}


def kiem_30s_dau(so_do: dict, max_tb: float = 3.5) -> list[str]:
    """Cảnh báo nếu 30 giây đầu cắt cảnh chậm (trung bình > max_tb giây/cảnh)."""
    tb = so_do.get("tb_giay_30s", 0)
    if tb > max_tb:
        return [f"Cảnh báo: 30 giây đầu cắt cảnh chậm (trung bình {tb:.1f} s/cảnh, chuẩn ≤ {max_tb:.1f} s để giữ chân người xem)"]
    return []


def kiem(so_do: dict, muc: dict = MUC_TIEU) -> list[str]:
    if not so_do["so_canh"]:
        return [EMPTY]
    out, n = [], so_do["so_canh"]
    if so_do["duoi_1_5"] > muc["duoi_1_5_max"]:
        out.append(f"Lỗi: {so_do['duoi_1_5']} cảnh ngắn dưới 1,5 s (hình giật)")
    lo, hi = muc["tb_giay"]
    if not lo <= so_do["tb_giay"] <= hi:
        out.append(f"Cảnh báo: Độ dài trung bình {so_do['tb_giay']:.1f} s, chuẩn {lo}–{hi} s")
    if so_do["tren_8"] / n > muc["tren_8_max"]:
        out.append(f"Cảnh báo: {so_do['tren_8']} cảnh dài hơn 8 s ở 60 s đầu hoặc bồi dần dưới "
                   f"{muc['san_khau_su_kien_phut']} sự kiện/phút (quá {muc['tren_8_max']:.0%} số cảnh)")
    t = so_do["ti_le"]
    if t["do-hoa"] < muc["do_hoa_min"]:
        out.append(f"Cảnh báo: Đồ họa tự dựng {t['do-hoa']:.0%}, chuẩn ≥ {muc['do_hoa_min']:.0%}")
    lo, hi = muc["bang_chung"]
    if not lo <= t["bang-chung"] <= hi:
        out.append(f"Cảnh báo: Cảnh bằng chứng {t['bang-chung']:.0%}, chuẩn {lo:.0%}–{hi:.0%}")
    if so_do.get("ti_le_stock", 0) > muc["stock_max"]:
        out.append(f"Cảnh báo: B-roll kho chung (Pexels/Pixabay) {so_do['ti_le_stock']:.0%}, chuẩn ≤ {muc['stock_max']:.0%}; "
                   "thiếu hình thật thì đổi sang đồ họa, đừng lấp stock")
    if so_do.get("anh_su_kien") == 0:
        out.append("Cảnh báo: chưa có ảnh/clip thật đúng sự kiện (nên 1–3, ghi nguồn và ngày)")
    if so_do["chay_dai_nhat"] > muc["chay_max"]:
        out.append(f"Cảnh báo: {so_do['chay_dai_nhat']} cảnh liền cùng một mẫu (tối đa {muc['chay_max']})")
    if so_do["su_kien_phut"] < muc["su_kien_phut_min"]:
        out.append(f"Cảnh báo: {so_do['su_kien_phut']:.0f} sự kiện hình/phút, chuẩn ≥ {muc['su_kien_phut_min']}")
    if so_do["sfx_phut"] < muc["sfx_phut_min"]:
        out.append(f"Cảnh báo: {so_do['sfx_phut']:.0f} hiệu ứng âm thanh/phút, chuẩn ≥ {muc['sfx_phut_min']}")
    if so_do.get("mo_dau") is False:
        out.append("Cảnh báo: cảnh đầu chưa có số hoặc chữ (thêm tu_khoa cho b-roll, hoặc mở bằng so-lon/trich-bao)")
    lo, hi = muc["toc_do"]
    if not lo <= so_do["toc_do"] <= hi:
        out.append(f"Cảnh báo: Tốc độ đọc {so_do['toc_do']:.0f} từ/phút, chuẩn {lo}–{hi}")
    k, m = so_do.get("do_kho"), muc["do_kho"]
    if k:
        so_minh_hoa = k.get("so_canh_minh_hoa", m["phong_min"])
        phong_min = min(m["phong_min"], so_minh_hoa)
        if k["so_phong"] < phong_min:
            out.append(f"Cảnh báo: độ khô: {k['so_phong']} phông khác nhau, cần ≥ {phong_min}")
        if k["phong_lien_max"] > m["phong_lien_max"]:
            out.append(f"Cảnh báo: độ khô: {k['phong_lien_max']} cảnh liền cùng phông (tối đa {m['phong_lien_max']})")
        if k["vat_chinh_lap"] > m["lap_max"]:
            out.append(f"Cảnh báo: độ khô: {k['vat_chinh_lap']} cảnh lặp hình chính trong cửa sổ 8 cảnh")
        if so_minh_hoa and k["ti_le_may_quay"] < m["may_quay_min"]:
            out.append(f"Cảnh báo: độ khô: chỉ {k['ti_le_may_quay']:.0%} cảnh minh họa có camera, chuẩn ≥ {m['may_quay_min']:.0%}")
        if k.get("clip_lap"):
            out.append(f"Cảnh báo: độ khô: {k['clip_lap']} cảnh dùng lại cùng tệp b-roll trong cửa sổ 8 cảnh")
        if k.get("canh_tinh_dai"):
            out.append(f"Cảnh báo: độ khô: {k['canh_tinh_dai']} cảnh đồ họa tĩnh dài > 4,5 s không có nhịp con hay camera")
        if k.get("trong_diem_thieu"):
            out.append(f"Cảnh báo: độ khô: {k['trong_diem_thieu']} cảnh trọng điểm thiếu ẩn dụ hoặc camera")
        if k.get("nhip_cam_xuc_du") is False:
            out.append("Cảnh báo: độ khô: bản đồ nhịp cảm xúc thiếu một trong mở, đỉnh, đảo chiều, chốt")
        if k.get("cham_thap"):
            out.append(f"Cảnh báo: độ khô: {k['cham_thap']} beat có tiêu chí giám khảo dưới {m['cham_min']}")
        if "cham_tb" in k and k["cham_tb"] < m["cham_tb_min"]:
            out.append(f"Cảnh báo: độ khô: điểm giám khảo trung bình {k['cham_tb']:.1f} < {m['cham_tb_min']}")
    out += kiem_30s_dau(so_do)
    return out


def main(video_dir: str) -> int:
    d = Path(video_dir)
    canh = json.loads((d / "canh.json").read_text(encoding="utf-8"))
    timing = json.loads((d / "giong-timing.json").read_text(encoding="utf-8"))
    dd = d / "dao-dien.json"
    cham = d / "dao-dien-cham.json"
    so_do = do(canh, timing, json.loads(dd.read_text(encoding="utf-8")) if dd.exists() else None,
               json.loads(cham.read_text(encoding="utf-8")) if cham.exists() else None, doc_ghi_cong(d))
    msgs = kiem(so_do)
    for k, v in so_do.items():
        print(f"  {k}: {v if not isinstance(v, float) else round(v, 2)}")
    for m in msgs:
        print("-", m)
    errs = [m for m in msgs if m.startswith("Lỗi")]
    print(f"{len(errs)} lỗi, {len(msgs) - len(errs)} cảnh báo")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
