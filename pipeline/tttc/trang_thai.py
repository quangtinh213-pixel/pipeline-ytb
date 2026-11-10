"""Sổ trạng thái của một video: videos/<slug>/trang-thai.json."""
import hashlib
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

STEPS = ["chu-de", "nguon", "kich-ban", "phan-bien-giong", "kiem", "duyet-1", "giong", "dao-dien", "canh", "hinh",
         "render", "dong-goi", "duyet-2", "dang", "shorts"]  # shorts dựng sau khi đăng video dài, không nằm trên đường găng
STATUSES = {"chua-chay", "dang-chay", "xong", "loi", "cho-duyet", "da-duyet"}
KET_THUC = {"xong", "da-duyet", "cho-duyet", "loi"}  # trạng thái ghi giờ kết thúc
VN = timezone(timedelta(hours=7))
FILE = "trang-thai.json"


# Bước thêm sau này: tệp cũ mà đã có bước nào từ mốc này trở đi khác chua-chay thì coi như xong, không bị đẩy lùi.
CO_TRUOC = {"phan-bien-giong": "duyet-1", "dao-dien": "canh"}


def load(video_dir) -> dict:
    p = Path(video_dir) / FILE
    data = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    steps = data.setdefault("steps", {})
    qua = {s: any(steps.get(t, {}).get("status", "chua-chay") != "chua-chay" for t in STEPS[STEPS.index(tu):])
           for s, tu in CO_TRUOC.items()}  # tính trước vòng lặp để không phụ thuộc thứ tự điền mặc định
    for s in STEPS:
        steps.setdefault(s, {"status": "xong", "note": "video có trước bước này"}
                         if qua.get(s) else {"status": "chua-chay", "note": ""})
    return data


def _save(video_dir, data: dict) -> None:
    p = Path(video_dir) / FILE
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, p)  # ghi nguyên tử: lỗi giữa chừng không làm hỏng sổ


def set_step(video_dir, step: str, status: str, note: str = "", now: datetime | None = None) -> None:
    if step not in STEPS:
        raise ValueError(f"bước không tồn tại: {step}")
    if status not in STATUSES:
        raise ValueError(f"trạng thái không hợp lệ: {status}")
    t = (now or datetime.now(VN)).isoformat()
    data = load(video_dir)
    cur = {**data["steps"][step], "status": status, "note": note}  # giữ bat_dau/ket_thuc đã có
    if step in ("duyet-1", "duyet-2"):
        cur.pop("ban_duyet", None)
        cur.pop("chon", None)
    if status == "dang-chay" and data["steps"][step].get("status") != "dang-chay":
        cur["bat_dau"] = t
        cur.pop("ket_thuc", None)
    if status in KET_THUC:
        cur["ket_thuc"] = t
    data["steps"][step] = cur
    _save(video_dir, data)


def gio(video_dir) -> dict:
    """{"buoc": {bước: giây}, "tong": giây từ bat_dau của chu-de đến ket_thuc của duyet-2, hoặc None}."""
    steps = load(video_dir)["steps"]
    sec = lambda a, b: round((datetime.fromisoformat(b) - datetime.fromisoformat(a)).total_seconds())
    buoc = {s: sec(v["bat_dau"], v["ket_thuc"]) for s, v in steps.items() if "bat_dau" in v and "ket_thuc" in v}
    a, b = steps["chu-de"].get("bat_dau"), steps["duyet-2"].get("ket_thuc")
    return {"buoc": buoc, "tong": sec(a, b) if a and b else None}


def set_field(video_dir, key: str, value) -> None:
    set_fields(video_dir, **{key: value})


def set_fields(video_dir, **fields) -> None:
    data = load(video_dir)
    data.update(fields)
    _save(video_dir, data)


def next_step(video_dir):
    """Bước đầu tiên chưa xong; None khi đang chờ người duyệt hoặc đã hết bước."""
    steps = load(video_dir)["steps"]
    for s in STEPS:
        st = steps[s]["status"]
        if st == "cho-duyet":
            return None
        if st not in ("xong", "da-duyet"):
            return s
    return None


def kho(videos_root) -> list[Path]:
    """Kho dự trữ: video evergreen đã qua duyệt 2 nhưng chưa đăng, sắp theo tên thư mục."""
    out = []
    for d in sorted(Path(videos_root).iterdir()):
        if not (d / FILE).exists():
            continue
        data = load(d)
        if (data.get("loai") == "evergreen" and not data.get("video_id")
                and data["steps"]["dang"]["status"] != "xong" and review_current(d, "duyet-2")):
            out.append(d)
    return out


def is_approved(video_dir) -> bool:
    steps = load(video_dir)["steps"]
    return all(steps[s]["status"] == "da-duyet" for s in ("duyet-1", "duyet-2"))


def _digest(path: Path) -> str:
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def _review_files(video_dir, step: str, state: dict) -> dict:
    d = Path(video_dir)
    if step == "duyet-1":
        sources = json.loads((d / "nguon.json").read_text(encoding="utf-8"))
        files = ["kich-ban.md", "nguon.json", "nghe-thu.mp3", *(s["anh_chup"] for s in sources if s.get("anh_chup"))]
        return {name: _digest(d / name) for name in files}
    if step != "duyet-2":
        raise ValueError(f"Bước duyệt không hợp lệ: {step}")
    if not review_current(d, "duyet-1"):
        raise ValueError("Kịch bản hoặc nguồn thay đổi, cần duyệt 1 lại")
    package = json.loads((d / "dong-goi.json").read_text(encoding="utf-8"))
    package.pop("shorts", None)  # Shorts được làm và xác nhận riêng sau video dài.
    return {
        "duyet-1": state["steps"]["duyet-1"]["ket_thuc"],
        "final.mp4": _digest(d / "final.mp4"),
        "phu-de.srt": _digest(d / "phu-de.srt"),
        "dong-goi": package,
        "thumbnails": [_digest(d / opt["file_thumb"]) for opt in package["phuong_an"]],
    }


def review_current(video_dir, step: str) -> bool:
    state = load(video_dir)
    cur = state["steps"][step]
    if cur["status"] != "da-duyet" or "ban_duyet" not in cur:
        return False
    try:
        return (cur["ban_duyet"] == _review_files(video_dir, step, state)
                and (step != "duyet-2" or cur["chon"] == state.get("chon")))
    except (OSError, ValueError, KeyError):
        return False


def prepare_review(video_dir, step: str) -> None:
    state = load(video_dir)
    if state.get("video_id"):
        raise ValueError("Video đã có ID YouTube, chỉ dùng hồ sơ này để đối chiếu")
    if step == "duyet-2":
        from tttc.dung import check_av

        if any(state["steps"][s]["status"] != "xong" for s in ("giong", "render", "dong-goi")):
            raise ValueError("Cần hoàn tất giọng, render và đóng gói trước khi gửi duyệt 2")
        d = Path(video_dir)
        if errors := check_av(d / "final.mp4", d / "giong.mp3"):
            raise ValueError("Kiểm hình–tiếng chưa đạt: " + " / ".join(errors))
    snapshot = _review_files(video_dir, step, state)
    cur = state["steps"][step]
    cur.update(status="cho-duyet", ban_duyet=snapshot)
    cur.pop("ket_thuc", None)
    _save(video_dir, state)


def approve_review(video_dir, step: str, choice: int | None = None) -> None:
    state = load(video_dir)
    cur = state["steps"][step]
    if cur["status"] != "cho-duyet" or cur.get("ban_duyet") != _review_files(video_dir, step, state):
        raise ValueError("Bản gửi duyệt đã thay đổi hoặc chưa được gửi, hãy tạo lại trang duyệt")
    if step == "duyet-2":
        if choice is None or not 1 <= choice <= len(cur["ban_duyet"]["thumbnails"]):
            raise ValueError("Chọn một phương án tiêu đề và thumbnail đã gửi")
        cur["chon"] = state["chon"] = choice
    else:
        from tttc.kiem import check

        d = Path(video_dir)
        errors = check((d / "kich-ban.md").read_text(encoding="utf-8"),
                       json.loads((d / "nguon.json").read_text(encoding="utf-8")))
        if errors:
            raise ValueError("Kiểm nguồn chưa đạt:\n" + "\n".join(errors))
        for s in STEPS[STEPS.index("giong"):STEPS.index("duyet-2") + 1]:
            state["steps"][s] = {"status": "chua-chay", "note": ""}
        state.pop("chon", None)
    cur.update(status="da-duyet", ket_thuc=datetime.now(VN).isoformat())
    _save(video_dir, state)


if __name__ == "__main__" and len(sys.argv) == 3 and sys.argv[1] == "gio":
    g = gio(sys.argv[2])
    for k, v in g["buoc"].items():
        print(f"{k}: {v // 60:02}:{v % 60:02}")
    print("tổng:", "chưa đủ mốc" if g["tong"] is None else f"{g['tong'] // 3600}h{g['tong'] % 3600 // 60:02}")
elif __name__ == "__main__" and len(sys.argv) == 4 and sys.argv[1] == "gui-duyet":
    prepare_review(sys.argv[2], sys.argv[3])
elif __name__ == "__main__" and len(sys.argv) in (4, 5) and sys.argv[1] == "duyet":
    approve_review(sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) == 5 else None)
