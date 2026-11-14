"""Sinh canh.json từ canh-khung.json: ưu tiên b-roll, đồ họa cho số liệu, trích trang nguồn, quy trình và kết thúc.
Chạy trong pipeline/: uv run python ../videos/2026-11-15-lo-hong-7zip-ai/canh-ke-hoach.py"""
import json
from pathlib import Path

from tttc import broll

V = Path(__file__).resolve().parent
KHO = {e["tep"]: e for e in json.loads((broll.KHO / "kho.json").read_text(encoding="utf-8"))}

def C(so, ten):
    return {"mau": "chuong", "so": so, "chuong": ten, "dan": {"the": "chao"}}

def B(clip, tu_khoa=None, **k):
    return {"_clip": clip, "tu_khoa": tu_khoa, **k}

QT = [
    {"nhan": "Mở Giới thiệu", "svg": "hop-thu"},
    {"nhan": "Cập nhật v26.06", "svg": "may-chu"},
    {"nhan": "Tránh tệp lạ", "svg": "tai-lieu"}
]

KE = {
    0: {"mau": "so-lon", "so": 8.5, "truoc": "Điểm ", "sau": "/10", "nhan": "Điểm nguy hiểm CVSS",
        "nguon_id": "v1", "dan": {"the": "ngac-nhien", "goc": "phai"}},
    1: {"mau": "trang-nguon", "nguon_id": "v1", "anh": "v1.png", "khung": "15.7,38.0,46.3,24.0",
        "nhan": "VnExpress · Đánh giá CVSS v4.0"},
    2: B("singapore-dem-30570498", "Sinh viên Việt & AI"),
    3: {"mau": "mo-dau", "cau": "Lỗ hổng 7-Zip: máy bạn có dính?"},
    4: B("go-laptop-van-phong-4928295", "Hầu như máy nào cũng cài"),
    5: {"mau": "so-lon", "so": 787, "nhan": "Mã lỗi CWE-787 ghi vượt vùng nhớ", "nguon_id": "v6"},
    6: B("man-hinh-code-29458457", "Giải nén tệp CAB Microsoft"),
    7: B("vi-mach-phat-sang-36382300", "Bộ nhớ thu nhỏ"),
    8: {"mau": "chu-dong", "cau": "cấp phát vùng nhớ mới nhưng giữ nguyên vị trí ghi cũ", "nhan_tu": "vị trí ghi cũ", "nho": "Bản chất lỗi"},
    9: B("bo-mach-chip-6754824", "Ghi tràn ra ngoài vùng nhớ"),
    10: B("o-khoa-10241357", "Khai thác tệp độc hại"),
    11: B("trung-tam-du-lieu-1085656", "Kết nối về máy chủ tin tặc"),
    12: B("laptop-go-phim-7252685", "Điều khiển từ xa", dan={"the": "nghi", "goc": "trai"}),
    13: C("Phần 1", "Sinh viên Việt & AI"),
    14: {"mau": "trang-nguon", "nguon_id": "v4", "anh": "v4.png", "khung": "15.7,39.7,46.3,20.5",
         "nhan": "VnExpress · Sinh viên NTU Singapore"},
    15: {"mau": "trang-nguon", "nguon_id": "v6", "anh": "v6.png", "khung": "15.7,51.8,46.3,10.0",
         "nhan": "VnExpress · Hỗ trợ từ Claude Opus 5"},
    16: B("man-hinh-code-29458457", "VulnCheck ghi nhận"),
    17: B("thiet-bi-dien-tu-7140931", "Cấp mã CVE toàn cầu"),
    18: {"mau": "so-lon", "so": 7.8, "truoc": "gần ", "sau": "/10", "nhan": "CVSS theo chuẩn cũ",
         "nguon_id": "v2", "dan": {"the": "xac-nhan", "goc": "phai"}},
    19: B("cuon-man-hinh-6258096", "Ít ai để ý cảnh báo"),
    20: B("dien-thoai-tay-853794", "Bảo vệ máy tính & dữ liệu"),
    21: B("dung-dien-thoai-12692095", "Đăng ký Nhịp Công Nghệ"),
    22: C("Phần 2", "3 việc kiểm tra ngay"),
    23: {"mau": "quy-trinh", "tieu_de": "3 việc cần làm", "buoc": QT, "noi_bat": 0},
    24: B("man-hinh-may-tinh-8346903", "Kiểm tra phiên bản"),
    25: {"mau": "so-lon", "so": 26.06, "truoc": "Bản vá v", "nhan": "Bản vá chính thức vá lỗi", "nguon_id": "v3"},
    26: {"mau": "trang-nguon", "nguon_id": "v3", "anh": "v3.png", "khung": "15.7,43.2,46.3,13.5",
         "nhan": "VnExpress · Bản vá từ 7-Zip 26.06"},
    27: {"mau": "quy-trinh", "tieu_de": "3 việc cần làm", "buoc": QT, "noi_bat": 2},
    28: B("day-cap-bo-mach-7140937", "Cảnh giác tệp lạ"),
    29: {"mau": "so-lon", "so": 27, "truoc": "~", "sau": " năm", "nhan": "Tính ra 27 năm (từ 1999)",
         "nguon_id": "t1", "dan": {"the": "tinh-toan", "goc": "phai"}},
    30: B("laptop-ban-dem-7272375", "Lâu đời mà vẫn sót lỗi"),
    31: B("singapore-dem-30570498", "Soi ra trước khi bị tấn công"),
    32: B("dung-dien-thoai-12692095", "Đăng ký kênh & xem tiếp"),
    33: {"mau": "ket-thuc", "cau": "Xem tiếp các cảnh báo nhé!"}
}

def main():
    khung = json.loads((V / "canh-khung.json").read_text(encoding="utf-8"))["scenes"]
    assert len(khung) == 35, f"canh-khung.json có {len(khung)} cảnh, kế hoạch viết cho 35"
    # Gộp cảnh 33 và 34 thành màn hình kết thúc dài 8.93s
    khung = khung[:33] + [{**khung[33], "end": khung[-1]["end"], "loi": " ".join(k["loi"] for k in khung[33:])}]
    scenes = []
    for i, k in enumerate(khung):
        ke = dict(KE[i])
        if "_clip" in ke:
            e = KHO[ke.pop("_clip") + ".mp4"]
            dai = k["end"] - k["start"] + 0.5
            assert e["do_dai"] >= dai, f"clip {e['tep']} ngắn hơn cảnh {i}"
            out = broll.nhap(broll.KHO / e["tep"], V, e["ghi_cong"], bat_dau=0, do_dai=dai, hau_to=f"-{i:03d}")
            tk = ke.pop("tu_khoa")
            ke = {"mau": "b-roll", "video": out.name, "nhan": "", **({"tu_khoa": tk} if tk else {}), **ke}
        scenes.append({"id": k["id"], **ke, "start": k["start"], "end": k["end"]})
    (V / "canh.json").write_text(json.dumps({"scenes": scenes}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(scenes), "cảnh;", sum(s["mau"] == "b-roll" for s in scenes), "b-roll")

if __name__ == "__main__":
    main()
