"""Sổ trạng thái của một video: videos/<slug>/trang-thai.json."""
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


def kho(videos_root) -> list[Path]:
    """Kho dự trữ: video evergreen đã qua duyệt 2 nhưng chưa đăng, sắp theo tên thư mục."""
    out = []
    for d in sorted(Path(videos_root).iterdir()):
        if not (d / FILE).exists():
            continue
        data = load(d)
        if (data.get("loai") == "evergreen" and data["steps"]["duyet-2"]["status"] == "da-duyet"
                and data["steps"]["dang"]["status"] != "xong"):
            out.append(d)
    return out


def is_approved(video_dir) -> bool:
    steps = load(video_dir)["steps"]
    return all(steps[s]["status"] == "da-duyet" for s in ("duyet-1", "duyet-2"))


if __name__ == "__main__" and len(sys.argv) == 3 and sys.argv[1] == "gio":
    g = gio(sys.argv[2])
    for k, v in g["buoc"].items():
        print(f"{k}: {v // 60:02}:{v % 60:02}")
    print("tổng:", "chưa đủ mốc" if g["tong"] is None else f"{g['tong'] // 3600}h{g['tong'] % 3600 // 60:02}")
