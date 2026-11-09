"""Cổng đo chất lượng theo chuẩn kênh mẫu (docs/nghien-cuu/kenh-mau-motcongnghe-2026-11-09.md mục 4).

Chạy trước khi render (render mất cả giờ): uv run python -m tttc.chat_luong ../videos/<slug>
"""
import json
import sys
from pathlib import Path

from tttc import dung

NHOM = {
    "do-hoa": {"minh-hoa", "quy-trinh", "so-sanh", "thoi-gian", "so-lon", "bieu-do", "chuong"},
    "bang-chung": {"trich-bao", "trang-nguon"},
    "doi-that": {"b-roll", "nhan-vat"},
}
MUC_TIEU = {
    "tb_giay": (2.8, 4.5), "duoi_1_5_max": 0, "tren_8_max": 0.03, "do_hoa_min": 0.70,
    "bang_chung": (0.08, 0.18), "doi_that_max": 0.15, "chay_max": 2,
    "su_kien_phut_min": 30, "sfx_phut_min": 15, "toc_do": (130, 160),
}
EMPTY = "Lỗi: canh.json không có cảnh nào"


def _buoc(c: dict, words: list[dict]) -> list[float]:
    try:
        return dung.steps(c, words)
    except KeyError:  # shortcut: mẫu chưa khai báo bước thì tính 0 bước; canh.validate báo mẫu lạ riêng
        return []


def do(canh: dict, timing: dict) -> dict:
    sc = canh["scenes"]
    words = timing.get("words", [])
    n = len(sc)
    if not n:
        return {"so_canh": 0}
    durs = [c["end"] - c["start"] for c in sc]
    phut = max((sc[-1]["end"] - sc[0]["start"]) / 60, 1e-9)
    ti_le = {g: sum(c["mau"] in maus for c in sc) / n for g, maus in NHOM.items()}
    chay = best = 0
    prev = None
    for c in sc:
        chay = chay + 1 if c["mau"] == prev else 1
        best, prev = max(best, chay), c["mau"]
    steps = [_buoc(c, words) for c in sc]
    sfx = sum(len(dung.sfx_events(c, st)) for c, st in zip(sc, steps))
    sfx += sum(kind != "dip" for _, kind in dung.transitions(sc))
    dan = sum(1 for c in sc if c.get("dan"))
    return {"so_canh": n, "tb_giay": sum(durs) / n, "duoi_1_5": sum(d < 1.5 for d in durs),
            "tren_8": sum(d > 8 for d in durs), "ti_le": ti_le, "chay_dai_nhat": best,
            "su_kien_phut": (n + sum(map(len, steps)) + dan) / phut, "sfx_phut": sfx / phut,
            "toc_do": len(words) / phut}


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
        out.append(f"Cảnh báo: {so_do['tren_8']} cảnh dài hơn 8 s (quá {muc['tren_8_max']:.0%} số cảnh)")
    t = so_do["ti_le"]
    if t["do-hoa"] < muc["do_hoa_min"]:
        out.append(f"Cảnh báo: Đồ họa tự dựng {t['do-hoa']:.0%}, chuẩn ≥ {muc['do_hoa_min']:.0%}")
    lo, hi = muc["bang_chung"]
    if not lo <= t["bang-chung"] <= hi:
        out.append(f"Cảnh báo: Cảnh bằng chứng {t['bang-chung']:.0%}, chuẩn {lo:.0%}–{hi:.0%}")
    if t["doi-that"] > muc["doi_that_max"]:
        out.append(f"Cảnh báo: Ảnh/video đời thật {t['doi-that']:.0%}, chuẩn ≤ {muc['doi_that_max']:.0%}")
    if so_do["chay_dai_nhat"] > muc["chay_max"]:
        out.append(f"Cảnh báo: {so_do['chay_dai_nhat']} cảnh liền cùng một mẫu (tối đa {muc['chay_max']})")
    if so_do["su_kien_phut"] < muc["su_kien_phut_min"]:
        out.append(f"Cảnh báo: {so_do['su_kien_phut']:.0f} sự kiện hình/phút, chuẩn ≥ {muc['su_kien_phut_min']}")
    if so_do["sfx_phut"] < muc["sfx_phut_min"]:
        out.append(f"Cảnh báo: {so_do['sfx_phut']:.0f} hiệu ứng âm thanh/phút, chuẩn ≥ {muc['sfx_phut_min']}")
    lo, hi = muc["toc_do"]
    if not lo <= so_do["toc_do"] <= hi:
        out.append(f"Cảnh báo: Tốc độ đọc {so_do['toc_do']:.0f} từ/phút, chuẩn {lo}–{hi}")
    return out


def main(video_dir: str) -> int:
    d = Path(video_dir)
    canh = json.loads((d / "canh.json").read_text(encoding="utf-8"))
    timing = json.loads((d / "giong-timing.json").read_text(encoding="utf-8"))
    so_do = do(canh, timing)
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
