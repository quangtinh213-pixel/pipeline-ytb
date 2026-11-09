"""Cổng chạy khô: kiểm 7 tiêu chí của một ngày chạy khô (docs/superpowers/specs/2026-11-09-dinh-vi-doi-dau-van-hanh-design.md mục 7).

Chạy: uv run python -m tttc.chay_kho ../videos/<slug>
Mỗi tiêu chí là một hàm nhỏ trả thông báo "Chưa đạt n: ..." hoặc None; tệp thiếu thì báo thiếu, không ném lỗi.
"""
import json
import sys
from datetime import datetime
from pathlib import Path

from tttc import chat_luong, dung, phong_cach
from tttc import trang_thai as tt
from tttc.kiem import check

HAN = (15, 0)  # duyệt 2 xong trước 15:00 giờ Việt Nam


def _json(p: Path):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _msgs_chat_luong(d: Path) -> list[str] | None:
    canh, timing = _json(d / "canh.json"), _json(d / "giong-timing.json")
    return None if canh is None or timing is None else chat_luong.kiem(chat_luong.do(canh, timing))


def _c1(d: Path):
    kt = tt.load(d)["steps"]["duyet-2"].get("ket_thuc")
    if not kt:
        return "Chưa đạt 1: duyệt 2 chưa xong (chưa có giờ kết thúc)"
    t = datetime.fromisoformat(kt).astimezone(tt.VN)
    if (t.hour, t.minute) > HAN:
        return f"Chưa đạt 1: duyệt 2 xong lúc {t:%H:%M}, mục tiêu trước 15:00"


def _c2(d: Path):
    ds = tt.load(d).get("can_thiep_tay") or []
    if ds:
        return f"Chưa đạt 2: {len(ds)} can thiệp tay ngoài hai điểm duyệt: " + "; ".join(map(str, ds))


def _c3(d: Path):
    loi = []
    script, nguon = d / "kich-ban.md", _json(d / "nguon.json")
    if script.exists() and nguon is not None:
        errs = check(script.read_text(encoding="utf-8"), nguon)
        if errs:
            loi.append(f"tttc.kiem còn {len(errs)} lỗi")
    else:
        loi.append("thiếu kich-ban.md hoặc nguon.json")
    msgs = _msgs_chat_luong(d)
    if msgs is None:
        loi.append("thiếu canh.json hoặc giong-timing.json")
    elif errs := [m for m in msgs if m.startswith("Lỗi")]:
        loi.append(f"chat_luong còn {len(errs)} Lỗi")
    if (d / "final.mp4").exists() and (d / "giong.mp3").exists():
        if bad := dung.check_av(d / "final.mp4", d / "giong.mp3"):
            loi.append(f"check_av báo {len(bad)} lệch hình–tiếng")
    else:
        loi.append("thiếu final.mp4 hoặc giong.mp3")
    return "Chưa đạt 3: " + "; ".join(loi) if loi else None


def _c4(d: Path):
    t = _json(d / "giong-timing.json")
    if t is None:
        return "Chưa đạt 4: thiếu giong-timing.json"
    wpm = len(t["words"]) / (t["duration"] / 60) if t.get("duration") else 0
    lo, hi = chat_luong.MUC_TIEU["toc_do"]
    if not lo <= wpm <= hi:
        return f"Chưa đạt 4: tốc độ đọc {wpm:.0f} từ/phút, chuẩn {lo}–{hi}"


def _c5(d: Path):
    steps = tt.load(d)["steps"]
    thieu = [s for s in tt.STEPS[: tt.STEPS.index("duyet-2") + 1] if "ket_thuc" not in steps[s]]
    if thieu:
        return "Chưa đạt 5: thiếu giờ kết thúc ở các bước " + ", ".join(thieu)


def _c6(d: Path):
    ds = [m for m in (_msgs_chat_luong(d) or []) if "độ khô" in m]  # chỉ số của kế hoạch hình ảnh; chưa có thì không có thông báo
    if ds:
        return "Chưa đạt 6: " + "; ".join(ds)


def _c7(d: Path):
    loi = [f"thiếu {n}" for n in ("phan-bien-giong-1.md", "phan-bien-giong-2.md") if not (d / n).exists()]
    script = d / "kich-ban.md"
    if not script.exists():
        loi.append("thiếu kich-ban.md")
    elif errs := [m for m in phong_cach.kiem(script.read_text(encoding="utf-8")) if m.startswith("Lỗi")]:
        loi.append(f"giọng văn còn {len(errs)} Lỗi")
    return "Chưa đạt 7: " + "; ".join(loi) if loi else None


def kiem(video_dir) -> list[str]:
    d = Path(video_dir)
    return [m for f in (_c1, _c2, _c3, _c4, _c5, _c6, _c7) if (m := f(d))]


def main(video_dir: str) -> int:
    msgs = kiem(video_dir)
    for m in msgs:
        print("-", m)
    print("Đạt cả 7 tiêu chí" if not msgs else f"{len(msgs)} tiêu chí chưa đạt")
    return 1 if msgs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
