"""Tạo lại demo mẫu cảnh với giọng tạm macOS (Linh). Chạy trong pipeline/: uv run python templates/canh-demo/tao-demo.py

Dữ liệu thật của video 1; ảnh và video lấy sẵn trong anh/, broll/, nguon/.
"""
import json
import subprocess
from pathlib import Path

from tttc import canh, dung

D = Path(__file__).resolve().parent
CAU = [  # (câu đọc, cảnh)
    ("Phần hai. ChatGPT có bốn gói.",
     {"mau": "chuong", "so": "Phần 2", "chuong": "ChatGPT: Free, Go, Plus, Pro"}),
    ("Bạn có đang trả tiền mỗi tháng cho tính năng mình không dùng tới?",
     {"mau": "minh-hoa", "svg": "laptop", "phu": ["dong-xu", "cay"], "nhan": "Trả tiền cho AI mỗi tháng?",
      "nhip": ["trả tiền", "mỗi tháng", "không dùng"]}),
    ("Trang giá của OpenAI mô tả gói Plus là phù hợp nhất cho công việc chuyên sâu và năng suất cao.",
     {"mau": "trich-bao", "nguon_id": "p2", "trich": "Phù hợp nhất cho công việc chuyên sâu và năng suất cao",
      "to_vang": "năng suất cao", "nhip": ["năng suất"]}),
    ("Gói Plus giá năm trăm hai mươi hai nghìn năm trăm đồng mỗi tháng.",
     {"mau": "so-lon", "so": 522500, "sau": " đ", "nhan": "ChatGPT Plus mỗi tháng", "nguon_id": "p1",
      "huong": "len", "svg": "tien", "nhip": ["năm trăm", "mỗi tháng"]}),
    ("Đặt cạnh gói Go và Google AI Pro, Plus là gói đắt nhất trong ba.",
     {"mau": "bieu-do", "nhan": "Giá gói AI trả phí mỗi tháng ở Việt Nam",
      "bieu_do": {"kieu": "cot", "nhan_x": ["ChatGPT Go", "Google AI Pro", "ChatGPT Plus"],
                  "gia_tri": [132000, 489000, 522500], "don_vi": "đ", "noi_bat": 2, "chu_thich": "ĐẮT NHẤT",
                  "nguon_id": ["p1", "g1"]}, "nhip": ["Go", "Google", "Plus", "đắt nhất"]}),
    ("Tiền thuê bao chảy về các trung tâm dữ liệu.",
     {"mau": "b-roll", "video": "trung-tam-du-lieu-5028622.mp4", "nhan": "Trung tâm dữ liệu", "so": "03",
      "nhip": ["trung tâm"]}),
    ("Người đứng sau ChatGPT là Sam Altman, tổng giám đốc OpenAI.",
     {"mau": "nhan-vat", "anh": "sam-altman-cropedit-james-tamim.jpg", "nhan": "Sam Altman", "vai": "Tổng giám đốc OpenAI",
      "nhip": ["tổng giám đốc"]}),
]
NGUON = [
    {"id": "p1", "gia_tri": "Go 132.000 đ; Plus 522.500 đ", "trich_dan": "", "url": "https://chatgpt.com/vi-VN/pricing",
     "ngay_truy_cap": "2026-11-08", "anh_chup": "nguon/p1.png", "trang_thai": "xac-minh"},
    {"id": "p2", "gia_tri": "", "ten": "OpenAI · Trang giá ChatGPT",
     "trich_dan": "Plus: Phù hợp nhất cho công việc chuyên sâu và năng suất cao",
     "url": "https://chatgpt.com/vi-VN/pricing", "ngay_truy_cap": "2026-11-08", "anh_chup": "nguon/p1.png",
     "trang_thai": "xac-minh"},
    {"id": "g1", "gia_tri": "Google AI Pro 489.000 đ", "trich_dan": "", "url": "https://one.google.com/about/plans",
     "ngay_truy_cap": "2026-11-07", "anh_chup": "", "trang_thai": "xac-minh"},
]


def main():
    from tttc import broll
    e = next(x for x in json.loads((broll.KHO / "kho.json").read_text(encoding="utf-8"))
             if x["tep"] == "trung-tam-du-lieu-5028622.mp4")
    broll.nhap(broll.KHO / e["tep"], D, e["ghi_cong"], bat_dau=2, do_dai=6)
    text = " ".join(c for c, _ in CAU)
    subprocess.run(["say", "-v", "Linh", "-r", "185", "-o", str(D / "g.aiff"), text], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(D / "g.aiff"), "-c:a", "libmp3lame", "-b:a", "128k",
                    str(D / "giong.mp3")], check=True)
    (D / "g.aiff").unlink()
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                str(D / "giong.mp3")], capture_output=True, text=True).stdout)
    # shortcut: giọng macOS không có timestamp, chia đều theo số ký tự; giọng ElevenLabs thật có mốc từng từ
    words, t, rate = [], 0.0, dur / len(text)
    for w in text.split():
        words.append({"w": w, "start": round(t, 3), "end": round(t + len(w) * rate, 3)})
        t += (len(w) + 1) * rate
    (D / "giong-timing.json").write_text(json.dumps({"duration": dur, "words": words, "paragraphs": []},
                                                    ensure_ascii=False), encoding="utf-8")
    (D / "nguon.json").write_text(json.dumps(NGUON, ensure_ascii=False, indent=1), encoding="utf-8")
    scenes, k = [], 0
    for i, (cau, sc) in enumerate(CAU):
        start = words[k]["start"] if i else 0.0
        k += len(cau.split())
        end = words[k]["start"] if k < len(words) else dur
        scenes.append(dict(sc, id=f"c{i + 1:02}", start=round(start, 3), end=round(end, 3)))
    (D / "canh.json").write_text(json.dumps({"scenes": scenes}, ensure_ascii=False, indent=1), encoding="utf-8")
    msgs = canh.validate({"scenes": scenes}, {"duration": dur, "words": words}, canh.SVG_DIR, NGUON, video_dir=D)
    print("\n".join(msgs) or "canh.json sạch")
    print(dung.compose(D), round(dur, 2), [(s["id"], s["start"], s["end"]) for s in scenes])


if __name__ == "__main__":
    main()
