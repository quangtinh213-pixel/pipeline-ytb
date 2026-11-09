"""Chạy thử chuỗi dựng không cần khoá API: giọng macOS + cảnh giả theo mẫu quay vòng, để đo thời gian render.
Dùng: uv run python scripts/thu-render.py ../videos/thu-nghiem [số_từ=380]
Nội dung cảnh là giả (số, nguồn lấy từ demo); chỉ mục đích đo chi phí render và soi lỗi hình, không đánh giá nội dung.
"""
import json
import shutil
import sys
from pathlib import Path

from tttc import broll, canh, chat_luong, chia, dung, giong_tam, tts

PIPE = Path(__file__).resolve().parent.parent
DEMO = PIPE / "templates" / "canh-demo"
KICH_BAN = PIPE.parent / "kich-ban-video-1-antigravity.md"
VONG = ["minh-hoa", "so-lon", "quy-trinh", "minh-hoa", "so-sanh", "trich-bao", "minh-hoa", "thoi-gian", "bieu-do", "b-roll"]
SVGS = ["chip", "laptop", "may-chu", "nha-may", "tien", "dien-thoai", "container", "tai-lieu"]


def _nhan(loi: str, n: int = 4) -> str:
    return " ".join(loi.split()[:n]).strip(".,?!").capitalize()


def noi_dung(i: int, mau: str, loi: str) -> dict:
    svg = SVGS[i % len(SVGS)]
    if mau == "chuong":
        return {"so": f"Phần {i // 10 + 1}", "chuong": _nhan(loi, 5)}
    if mau == "minh-hoa":
        return {"svg": svg, "phu": ["dong-xu", "cay"], "nhan": _nhan(loi)}
    if mau == "so-lon":
        return {"so": 522500, "sau": " đ", "nhan": _nhan(loi), "nguon_id": "p1", "huong": "len", "svg": "tien"}
    if mau == "quy-trinh":
        return {"tieu_de": _nhan(loi, 6), "noi_bat": 1, "buoc": [{"nhan": w.capitalize(), "svg": SVGS[(i + k) % 4]}
                                                                  for k, w in enumerate((loi.split() + ["a"] * 4)[:4])]}
    if mau == "so-sanh":
        return {"nguon_id": "p1", "ti_le": "gấp ~4 lần",
                "trai": {"nhan": "Gói Go", "svg": "laptop", "so": 132000, "don_vi": "đ"},
                "phai": {"nhan": "Gói Plus", "svg": "laptop", "so": 522500, "don_vi": "đ", "to": 0.5}}
    if mau == "trich-bao":
        return {"nguon_id": "p2", "trich": "Phù hợp nhất cho công việc chuyên sâu và năng suất cao", "to_vang": "năng suất cao"}
    if mau == "thoi-gian":
        return {"nguon_id": "t1", "tieu_de": _nhan(loi, 6), "truc": {"tu": 2024, "den": 2030, "don_vi": "năm"},
                "hang": [{"nhan": "A", "tu": 2024, "den": 2026}, {"nhan": "B", "tu": 2024, "den": 2028},
                         {"nhan": "C", "tu": 2026, "den": 2030, "noi_bat": True}]}
    if mau == "bieu-do":
        return {"nhan": _nhan(loi, 6), "bieu_do": {"kieu": "cot", "nhan_x": ["Go", "Google AI Pro", "Plus"],
                "gia_tri": [132000, 489000, 522500], "don_vi": "đ", "noi_bat": 2, "chu_thich": "ĐẮT NHẤT",
                "nguon_id": ["p1", "g1"]}}
    return {"video": "trung-tam-du-lieu-5028622.mp4", "nhan": _nhan(loi), "so": f"{i % 9 + 1:02}"}


def main(video_dir: str, so_tu: int = 380) -> int:
    V = Path(video_dir)
    V.mkdir(parents=True, exist_ok=True)
    text = ""
    for p in tts.spoken_paragraphs(KICH_BAN.read_text(encoding="utf-8")):
        text += " " + p
        if len(text.split()) >= so_tu:
            break
    timing = giong_tam.giong_tam(text.strip(), V)
    (V / "giong-timing.json").write_text(json.dumps(timing, ensure_ascii=False), encoding="utf-8")
    for sub in ("anh", "broll", "nguon"):
        shutil.copytree(DEMO / sub, V / sub, dirs_exist_ok=True)
    nguon = json.loads((DEMO / "nguon.json").read_text(encoding="utf-8"))
    nguon.append({"id": "t1", "gia_tri": "2024 2026 2028 2030", "trich_dan": "", "url": "https://example.com/t",
                  "ngay_truy_cap": "2026-11-09", "anh_chup": "", "trang_thai": "xac-minh"})
    (V / "nguon.json").write_text(json.dumps(nguon, ensure_ascii=False, indent=1), encoding="utf-8")
    scenes = []
    for i, s in enumerate(chia.chia(timing)):
        mau = "chuong" if i % 10 == 0 else VONG[i % len(VONG)]
        scenes.append(dict(noi_dung(i, mau, s["loi"]), id=s["id"], mau=mau, start=s["start"], end=s["end"]))
    canh_json = {"scenes": scenes}
    (V / "canh.json").write_text(json.dumps(canh_json, ensure_ascii=False, indent=1), encoding="utf-8")
    for m in canh.validate(canh_json, timing, canh.SVG_DIR, nguon, video_dir=V):
        print("-", m)
    chat_luong.main(str(V))
    print(dung.compose(V), f"{timing['duration']:.1f} s, {len(scenes)} cảnh")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 380))
