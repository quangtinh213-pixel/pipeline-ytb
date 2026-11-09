"""Sổ trạng thái của một video: videos/<slug>/trang-thai.json."""
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

STEPS = ["chu-de", "nguon", "kich-ban", "phan-bien-giong", "kiem", "duyet-1", "giong", "canh", "hinh",
         "render", "shorts", "dong-goi", "duyet-2", "dang"]
STATUSES = {"chua-chay", "dang-chay", "xong", "loi", "cho-duyet", "da-duyet"}
KET_THUC = {"xong", "da-duyet", "cho-duyet", "loi"}  # trạng thái ghi giờ kết thúc
VN = timezone(timedelta(hours=7))
FILE = "trang-thai.json"


def load(video_dir) -> dict:
    p = Path(video_dir) / FILE
    data = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    steps = data.setdefault("steps", {})
    # video đã qua điểm duyệt 1 từ trước khi có bước phan-bien-giong thì coi như đã xong, không bị đẩy lùi
    qua_duyet_1 = any(steps.get(s, {}).get("status", "chua-chay") != "chua-chay" for s in STEPS[STEPS.index("duyet-1"):])
    for s in STEPS:
        steps.setdefault(s, {"status": "xong", "note": "video có trước bước này"}
                         if s == "phan-bien-giong" and qua_duyet_1 else {"status": "chua-chay", "note": ""})
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


if __name__ == "__main__" and len(sys.argv) == 3 and sys.argv[1] == "gio":
    g = gio(sys.argv[2])
    for k, v in g["buoc"].items():
        print(f"{k}: {v // 60:02}:{v % 60:02}")
    print("tổng:", "chưa đủ mốc" if g["tong"] is None else f"{g['tong'] // 3600}h{g['tong'] % 3600 // 60:02}")
