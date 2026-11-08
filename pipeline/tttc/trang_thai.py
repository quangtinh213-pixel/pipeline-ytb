"""Sổ trạng thái của một video: videos/<slug>/trang-thai.json."""
import json
import os
from pathlib import Path

STEPS = ["chu-de", "nguon", "kich-ban", "kiem", "duyet-1", "giong", "canh", "hinh",
         "render", "shorts", "dong-goi", "duyet-2", "dang"]
STATUSES = {"chua-chay", "xong", "loi", "cho-duyet", "da-duyet"}
FILE = "trang-thai.json"


def load(video_dir) -> dict:
    p = Path(video_dir) / FILE
    data = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    data.setdefault("steps", {})
    for s in STEPS:
        data["steps"].setdefault(s, {"status": "chua-chay", "note": ""})
    return data


def _save(video_dir, data: dict) -> None:
    p = Path(video_dir) / FILE
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, p)  # ghi nguyên tử: lỗi giữa chừng không làm hỏng sổ


def set_step(video_dir, step: str, status: str, note: str = "") -> None:
    if step not in STEPS:
        raise ValueError(f"bước không tồn tại: {step}")
    if status not in STATUSES:
        raise ValueError(f"trạng thái không hợp lệ: {status}")
    data = load(video_dir)
    data["steps"][step] = {"status": status, "note": note}
    _save(video_dir, data)


def set_field(video_dir, key: str, value) -> None:
    data = load(video_dir)
    data[key] = value
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


def is_approved(video_dir) -> bool:
    steps = load(video_dir)["steps"]
    return all(steps[s]["status"] == "da-duyet" for s in ("duyet-1", "duyet-2"))
