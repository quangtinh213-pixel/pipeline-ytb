"""Sinh canh.json từ canh-khung.json: ưu tiên b-roll, đồ họa chỉ cho số, trích dẫn, chương, ba việc nhỏ.
Chạy trong pipeline/: uv run python ../videos/2026-11-14-microsoft-sap-toan-cau/canh-ke-hoach.py"""
import json
from pathlib import Path

from tttc import broll

V = Path(__file__).resolve().parent
KHO = {e["tep"]: e for e in json.loads((broll.KHO / "kho.json").read_text(encoding="utf-8"))}


def T(i, trich, vang, vi, vang_vi, **k):
    return {"mau": "trich-bao", "nguon_id": i, "trich": trich, "to_vang": vang, "trich_vi": vi, "to_vang_vi": vang_vi, **k}


def C(so, ten):
    return {"mau": "chuong", "so": so, "chuong": ten, "dan": {"the": "chao"}}


def B(clip, tu_khoa=None, **k):  # b-roll: tên clip trong kho (không đuôi), từ khoá bật to giữa khung
    return {"_clip": clip, "tu_khoa": tu_khoa, **k}


QT = [{"nhan": "Kênh liên lạc dự phòng", "svg": "dien-thoai"}, {"nhan": "Danh bạ ngoài hộp thư", "svg": "tai-lieu"},
      {"nhan": "Sao lưu độc lập", "svg": "may-chu"}]
# chỉ số cảnh trong canh-khung.json (39 cảnh) → kế hoạch; cảnh 37–38 gộp thành màn hình kết thúc
KE = {
    0: {"mau": "so-lon", "so": 18, "truoc": "gần ", "sau": " giờ", "nhan": "Outlook gần như tê liệt, theo Kentik", "nguon_id": "k2",
        "svg": "hop-thu", "dan": {"the": "ngac-nhien", "goc": "phai"}},
    1: B("o-khoa-10241357", "Không phải hacker, AI"),
    2: B("trung-tam-du-lieu-1085656", "Nâng cấp mạng"),
    # trích VnExpress dựng lại bằng chữ (không chụp cả trang: ảnh lộ đoạn phỏng vấn người khác và thanh địa chỉ)
    3: {"mau": "trich-bao", "nguon_id": "v8", "trich": "không thể sử dụng được các dịch vụ như Outlook, Teams, OneDrive, SharePoint",
        "to_vang": "Outlook, Teams, OneDrive, SharePoint"},
    4: {"mau": "mo-dau", "cau": "Outlook tê liệt: bạn làm gì?"},
    5: C("Phần 1", "Chuyện gì đã xảy ra?"),
    6: B("trung-tam-du-lieu-5028622", "Kentik đo lưu lượng"),
    7: {"mau": "phan-tram", "so": 85, "tieu_de": "Lưu lượng dịch vụ thư", "nhan": "thấp hơn mức dự kiến, theo Kentik", "nguon_id": "k2"},
    8: B("dong-ho-kim-9160922", "Gần 18 giờ", nguon_id="k2"),
    9: B("thanh-pho-viet-nam-31111825", "Ở Việt Nam"),
    10: {"mau": "trich-bao", "nguon_id": "v1",
         "trich": "Tôi cần gửi báo giá cho khách trước 10h, nhưng Outlook cứ quay vòng rồi báo không thể truy cập trên nền web",
         "to_vang": "Outlook cứ quay vòng"},
    11: B("man-hinh-may-tinh-8346903", "Kẹt kiểu khác"),
    12: {"mau": "trich-bao", "nguon_id": "v2", "trich": "dữ liệu nội bộ của công ty chỉ được phép xử lý bằng Copilot",
          "to_vang": "chỉ được phép xử lý bằng Copilot"},
    13: B("laptop-dem-van-phong-30712136", "Chỉ một công cụ AI"),
    14: C("Phần 2", "Microsoft nói gì?"),
    15: T("m1", "This was a technical issue not related to cyber or AI / agents.", "not related to cyber or AI / agents",
          "Đây là một sự cố kỹ thuật, không liên quan tới tấn công mạng hay AI hoặc tác nhân AI.", "không liên quan tới tấn công mạng hay AI"),
    16: T("m2", "The incident was introduced by an issue during an earlier network capacity upgrade that surfaced following a recent network change.",
          "earlier network capacity upgrade",
          "Sự cố bắt nguồn từ một lỗi trong lần nâng cấp dung lượng mạng trước đó, lộ ra sau một thay đổi mạng gần đây.",
          "nâng cấp dung lượng mạng trước đó"),
    17: B("day-cap-bo-mach-7140937", "Thay đổi mạng gần đây"),
    18: T("m3", "We will provide a full post-incident report once our review is complete.", "full post-incident report",
          "Chúng tôi sẽ công bố báo cáo đầy đủ sau sự cố khi xem xét xong.", "báo cáo đầy đủ sau sự cố"),
    19: B("giay-to-7054942", "Báo cáo chưa ra", dan={"the": "bo-ngo", "huong": "truoc"}),
    20: C("Phần 3", "Làm gì ngay?"),
    21: {"mau": "quy-trinh", "tieu_de": "Ba việc nhỏ", "buoc": QT, "noi_bat": 0, "nguon_id": "v5"},
    22: B("dien-thoai-tay-853794", "Nhóm Zalo dự phòng"),
    23: {"mau": "quy-trinh", "tieu_de": "Ba việc nhỏ", "buoc": QT, "noi_bat": 1, "nguon_id": "v4"},
    24: B("viet-tay-so-tay-4017221", "Danh bạ điện thoại"),
    25: B("go-laptop-van-phong-4928295", "Đừng chỉ một hộp thư"),
    26: {"mau": "quy-trinh", "tieu_de": "Ba việc nhỏ", "buoc": QT, "noi_bat": 2, "nguon_id": "v7"},
    27: B("phong-hop-trong-6951393", "Hỏi bộ phận kỹ thuật"),
    28: {"mau": "chu-dong", "cau": "nếu công cụ AI duy nhất ngừng chạy thì phương án B là gì?", "nhan_tu": "phương án B", "nho": "Gợi ý của kênh"},
    29: B("cuon-man-hinh-6258096", "Nhận cảnh báo sớm"),
    30: B("dung-dien-thoai-12692095", "Bấm Đăng ký"),
    31: {"mau": "minh-hoa", "svg": "dam-may", "phu": ["hop-thu"], "nhan": "Dữ liệu lên mây", "san_khau": "may-chu", "may_quay": "day-vao"},
    32: {"mau": "minh-hoa", "svg": "dong-ho", "phu": ["dam-may"], "nhan": "Mây nghỉ hơi dài", "may_quay": "keo-ra"},
    33: B("thiet-bi-dien-tu-7140931", "Không phải tấn công mạng"),
    34: B("giay-to-7732805", "Chờ báo cáo đầy đủ"),
    35: B("laptop-go-phim-7252685", "Có phương án B chưa?", dan={"the": "nghi", "goc": "phai"}),
    36: B("tay-cam-dien-thoai-5220470", "Bình luận cho mình"),
    37: {"mau": "ket-thuc", "cau": "Xem tiếp nhé"},
}


def main():
    khung = json.loads((V / "canh-khung.json").read_text(encoding="utf-8"))["scenes"]
    assert len(khung) == 39, f"canh-khung.json có {len(khung)} cảnh, kế hoạch viết cho 39"
    khung = khung[:37] + [{**khung[37], "end": khung[-1]["end"], "loi": " ".join(k["loi"] for k in khung[37:])}]  # màn hình kết thúc 6,3 s
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
