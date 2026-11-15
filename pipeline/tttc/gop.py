"""Lệnh gộp: chạy một chuỗi bước cố định trong một lần gọi, chỉ in phần cần đọc.

Mục đích là tiết kiệm token: mỗi lần Claude gọi lệnh là một lượt đọc lại cả ngữ cảnh, nên gom các lệnh kiểm/dựng
thường chạy liền nhau vào một lệnh, và chỉ in dòng Lỗi + vài Cảnh báo đầu thay cho toàn bộ bảng số đo.

Chạy trong pipeline/:
    uv run python -m tttc.gop kiem-1 V      # phong_cach + kiem + chấm tiêu đề (chặng 1, trước duyệt 1)
    uv run python -m tttc.gop kiem-canh V   # canh + chat_luong (chặng 2, trước render)
    uv run python -m tttc.gop render V      # cổng kiem-canh → compose → render.sh → soi-hinh.png → check_av
Thêm --day-du để in toàn bộ đầu ra của từng lệnh con. Mã thoát 1 khi còn Lỗi.
"""
import contextlib
import io
import json
import subprocess
import sys
from pathlib import Path

from tttc import canh, chat_luong, dung, kiem, phong_cach, tieu_de

GOC = Path(__file__).resolve().parent.parent
TOI_DA_CANH_BAO = 8  # shortcut: cắt ở 8 cảnh báo mỗi lệnh con, nâng lên nếu hay phải chạy lại với --day-du


def _chay(ten: str, ham, *args) -> tuple[int, list[str]]:
    """Chạy một hàm main(), bắt stdout, trả (mã thoát, các dòng)."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            rc = ham(*args)
        except FileNotFoundError as e:
            print(f"Lỗi: thiếu {Path(e.filename).name}")
            rc = 1
    return rc or 0, buf.getvalue().splitlines()


def tom_gon(ten: str, rc: int, dong: list[str], day_du: bool = False, toi_da: int = TOI_DA_CANH_BAO) -> list[str]:
    """Giữ mọi dòng Lỗi, tối đa `toi_da` dòng cảnh báo ('- ...' không phải Lỗi), và dòng tổng kết cuối."""
    if day_du:
        return [f"== {ten}", *dong]
    loi = [d for d in dong if d.lstrip("- ").startswith("Lỗi")]
    cb = [d for d in dong if d.startswith("- ") and d not in loi]
    tong = next((d for d in reversed(dong) if d and not d.startswith(("- ", "  "))), "")
    ra = [f"== {ten}: {'LỖI' if rc else 'đạt'}" + (f" ({tong})" if tong else ""), *loi, *cb[:toi_da]]
    if len(cb) > toi_da:
        ra.append(f"  … còn {len(cb) - toi_da} cảnh báo (--day-du để xem hết)")
    return ra


def _tieu_de(d: Path) -> tuple[int, list[str]]:
    kb = d / "kich-ban.md"
    dong = kb.read_text(encoding="utf-8").splitlines() if kb.exists() else []
    t = dong[0].replace("#", "").strip() if dong else ""
    kq = tieu_de.cham_diem(t)
    return (1 if kq.loi else 0), [*(f"- {m}" if m.startswith("Lỗi") else f"- Lỗi: {m}" for m in kq.loi), *(f"- {m}" for m in kq.canh_bao),
                                  f"{kq.diem}/10 – {t}"]


def kiem_1(d: Path, day_du: bool = False) -> tuple[int, list[str]]:
    ra, rc_tong = [], 0
    for ten, chay in (("phong_cach", lambda: _chay("phong_cach", phong_cach.main, str(d))),
                      ("kiem", lambda: _chay("kiem", kiem.main, str(d))),
                      ("tieu_de", lambda: _tieu_de(d))):
        rc, dong = chay()
        rc_tong |= rc
        ra += tom_gon(ten, rc, dong, day_du)
    return rc_tong, ra


def kiem_canh(d: Path, day_du: bool = False) -> tuple[int, list[str]]:
    # chat_luong.main in cả bảng số đo (dòng thụt 2 dấu cách); tom_gon bỏ các dòng đó khi không --day-du
    ra, rc_tong = [], 0
    for ten, ham in (("canh", canh.main), ("chat_luong", chat_luong.main)):
        rc, dong = _chay(ten, ham, str(d))
        rc_tong |= rc
        ra += tom_gon(ten, rc, dong, day_du)
    return rc_tong, ra


def render(d: Path, day_du: bool = False, chat: str = "delivery") -> tuple[int, list[str]]:
    rc, ra = kiem_canh(d, day_du)
    if rc:
        return rc, ra + ["Dừng: còn Lỗi, chưa render (render tốn cả chục phút)."]
    comp = dung.compose(str(d))
    out = d / "final.mp4"
    p = subprocess.run(["bash", str(GOC / "scripts" / "render.sh"), str(comp), str(out), chat],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if p.returncode:
        duoi = (p.stdout + p.stderr).strip().splitlines()[-15:]
        return 1, ra + ["== render: LỖI", *duoi]
    soi = dung.contact_sheet(out, json.loads((d / "canh.json").read_text(encoding="utf-8")), d / "frames" / "soi-hinh.png")
    av = dung.check_av(out, d / "giong.mp3")
    return (1 if av else 0), ra + [f"== render: xong {out}", f"== soi-hinh: {soi} (xem ảnh này)",
                                   "== check_av: " + ("đạt" if not av else "LỖI"), *av]


VIEC = {"kiem-1": kiem_1, "kiem-canh": kiem_canh, "render": render}


def main(argv: list[str]) -> int:
    day_du = "--day-du" in argv
    argv = [a for a in argv if a != "--day-du"]
    if len(argv) != 2 or argv[0] not in VIEC:
        print(__doc__)
        return 2
    rc, ra = VIEC[argv[0]](Path(argv[1]), day_du)
    print("\n".join(ra))
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
