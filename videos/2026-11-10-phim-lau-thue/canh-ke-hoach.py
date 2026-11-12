"""Sinh canh.json cho video phim lậu và thuế hàng Việt từ canh-khung.json: ưu tiên b-roll, đồ họa chỉ cho số, so sánh, trích dẫn, chương.
Chạy trong pipeline/: uv run python ../videos/2026-11-10-phim-lau-thue/canh-ke-hoach.py"""
import json
from pathlib import Path

from tttc import broll

V = Path(__file__).resolve().parent
KHO = {e["tep"]: e for e in json.loads((broll.KHO / "kho.json").read_text(encoding="utf-8"))}
NHOM = {
    "laptop": ["laptop-go-phim-7252685", "laptop-go-phim-853935", "go-laptop-van-phong-4928295", "laptop-ban-dem-7272375", "man-hinh-code-29458457"],
    "cang": ["cang-container-10391545", "cang-container-30281175"],
    "giay": ["giay-to-7732805", "giay-to-7104084", "giay-to-7841618", "viet-tay-so-tay-4017221", "giay-to-7054942", "ky-van-ban-5311423", "con-dau-7344550"],
    "dt": ["dien-thoai-tay-6611954", "dien-thoai-tay-853794", "luot-anh-dien-thoai-6756650"],
    "mang": ["trung-tam-du-lieu-1085656", "trung-tam-du-lieu-5028622"],
    "kho": ["kho-hang-giao-hang-4156510", "kho-hang-giao-hang-10472351", "bang-chuyen-san-bay-1169852"],
    "tien": ["may-tinh-tay-3860709", "may-tinh-tay-7055396", "the-tin-dung-laptop-6994837", "thanh-toan-the-6755016"],
    "xuong": ["nha-may-chip-32386617", "nha-may-chip-32386530", "day-chuyen-robot-32386529", "bo-mach-chip-6754824"],
    "tainghe": ["tai-nghe-laptop-8865637"],
    "phoxa": ["thanh-pho-viet-nam-31111825", "thanh-pho-viet-nam-31111952", "nha-viet-nam-3783794"],
    "manhinh": ["man-hinh-may-tinh-8346903"],
}
DU = {"cang": "kho", "kho": "cang", "mang": "laptop", "xuong": "kho", "tainghe": "dt", "phoxa": "cang", "manhinh": "laptop",
      "tien": "giay", "dt": "laptop", "giay": "laptop", "laptop": "giay"}


def T(i, trich, vang, vi=None, vang_vi=None, **k):
    d = {"mau": "trich-bao", "nguon_id": i, "trich": trich, "to_vang": vang, **k}
    if vi:
        d.update(trich_vi=vi, to_vang_vi=vang_vi)
    return d


def C(so, ten): return {"mau": "chuong", "so": so, "chuong": ten, "dan": {"the": "chao"}}
def M(svg, nhan, **k): return {"mau": "minh-hoa", "svg": svg, "nhan": nhan, **k}


# Cảnh đồ họa / bằng chứng (chỉ số cảnh theo canh-khung.json hiện tại)
DO_HOA = {
    0: T("h1", "extend for three months the ongoing Section 301 investigation", "three months",
         "Gia hạn thêm ba tháng cuộc điều tra đang diễn ra theo Điều 301", "Gia hạn thêm ba tháng"),
    4: T("l2", "without regard to whether or not such goods or economic sector were involved", "without regard",
         "Bất kể hàng hóa hay ngành kinh tế đó có liên quan đến vụ việc hay không", "Bất kể hàng hóa hay ngành kinh tế đó có liên quan"),
    6: T("f1", "impose 12.5 percent tariffs on products of Vietnam, except as provided", "12.5 percent",
         "Áp thuế 12,5% đối với sản phẩm của Việt Nam, trừ các ngoại lệ được quy định", "12,5%"),
    8: C("Phần 1", "Vì sao nói tới phim lậu?"),
    11: T("u2", "extensive libraries of pirated movies and TV shows.", "pirated movies and TV shows",
          "Những thư viện lớn chứa phim và chương trình truyền hình phát trái phép.", "phát trái phép"),
    14: M("kinh-lup", "Quy mô một mạng", dan={"the": "nghi"}),
    16: {"mau": "so-lon", "so": "6,7", "sau": " tỷ lượt", "nhan": "Fmovies và tên miền liên quan: hơn mức này, 2023–2024",
         "nguon_id": "a1", "svg": "may-chu"},
    22: M("kinh-lup", "Ai thật sự mua vé?", dan={"the": "bo-ngo"}),
    26: M("may-chu", "Đổi tên, cùng đầu lưu"),
    27: {"mau": "quy-trinh", "tieu_de": "Minh họa cấu trúc", "buoc": [{"nhan": "Người xem", "svg": "nguoi"}, {"nhan": "Trang phát", "svg": "laptop"},
                                                                  {"nhan": "Nơi lưu video", "svg": "may-chu"}]},
    33: T("u1", "the failure to provide persistent and effective enforcement to combat online piracy.", "persistent and effective enforcement",
          "Việc không bảo đảm thực thi bền bỉ và hiệu quả để chống vi phạm bản quyền trực tuyến.", "bền bỉ và hiệu quả"),
    35: T("h1", "extend for three months the ongoing Section 301 investigation", "ongoing Section 301 investigation",
          "Gia hạn thêm ba tháng cuộc điều tra đang diễn ra theo Điều 301", "cuộc điều tra đang diễn ra"),
    38: C("Phần 2", "Vì sao một lô hàng liên quan?"),
    39: {"mau": "so-sanh", "trai": {"nhan": "Website trên mạng", "svg": "laptop", "to": 0.7}, "phai": {"nhan": "Thuế ở cửa khẩu", "svg": "container"}},
    44: T("h2", "no later than February 28, 2027.", "February 28, 2027", "Chậm nhất ngày 28/02/2027.", "28/02/2027", dan={"the": "xac-nhan"}),
    46: T("l1", "impose duties or other import restrictions", "duties or other import restrictions",
          "Áp thuế hoặc các hạn chế nhập khẩu khác", "thuế hoặc các hạn chế nhập khẩu khác"),
    50: T("l3", "enter into binding agreements", "binding agreements", "Ký kết các thỏa thuận có tính ràng buộc", "thỏa thuận có tính ràng buộc"),
    52: M("tai-lieu", "Danh sách hàng hóa"),
    65: {"mau": "so-lon", "so": "28,7", "sau": " tỷ USD", "nhan": "Mỹ nhập từ Việt Nam · tháng 9/2026", "nguon_id": "c1", "svg": "container"},
    74: C("Phần 3", "Hai hồ sơ cùng tên điều luật"),
    75: {"mau": "so-lon", "so": "12,5", "sau": " %", "nhan": "thuộc vụ lao động cưỡng bức, có ngoại lệ", "nguon_id": "f1", "svg": "thue-phan-tram"},
    78: {"mau": "so-sanh", "trai": {"nhan": "Vụ bản quyền", "svg": "tai-lieu", "to": 0.85}, "phai": {"nhan": "Vụ lao động cưỡng bức", "svg": "tai-lieu"}},
    91: T("h2", "no later than February 28, 2027.", "February 28, 2027", "Chậm nhất ngày 28/02/2027.", "28/02/2027"),
    92: M("lich", "Hạn mới, chưa phải thuế"),
    94: M("hop-thu", "Hai email, hai việc", dan={"the": "nghi"}),
    99: C("Phần 4", "Hai tín hiệu cần theo dõi"),
    103: M("kinh-lup", "Hàng nào, ngoại lệ, khi nào"),
    117: {"mau": "so-sanh", "trai": {"nhan": "Sự kiện thực thi", "svg": "bua-phan-quyet", "to": 0.85}, "phai": {"nhan": "Sự kiện thương mại", "svg": "thue-phan-tram"}},
    120: C("Phần 5", "Web phim lậu dính gì tới thuế?"),
    122: T("l2", "without regard to whether or not such goods or economic sector were involved", "without regard",
           "Bất kể hàng hóa hay ngành kinh tế đó có liên quan đến vụ việc hay không", "Bất kể hàng hóa hay ngành kinh tế đó có liên quan"),
}

# Nhóm b-roll theo đoạn cảnh [từ, đến] (đóng hai đầu); cảnh không trong DO_HOA lấy nhóm tương ứng
NHOM_THEO_DOAN = [
    (0, 3, "laptop"), (4, 7, "giay"),
    (9, 13, "giay"), (15, 15, "mang"), (17, 21, "laptop"), (23, 24, "giay"), (25, 25, "laptop"), (28, 29, "mang"),
    (30, 32, "phoxa"), (34, 34, "giay"), (36, 37, "giay"),
    (40, 43, "giay"), (45, 45, "giay"), (47, 49, "cang"), (51, 51, "giay"), (53, 53, "giay"),
    (54, 58, "tainghe"), (59, 64, "kho"), (66, 73, "cang"),
    (76, 77, "giay"), (79, 90, "giay"), (93, 93, "giay"),
    (95, 98, "laptop"), (100, 102, "giay"), (104, 109, "mang"), (110, 114, "dt"), (115, 116, "giay"), (118, 119, "laptop"),
    (121, 121, "cang"), (123, 126, "cang"),
]
# cụm cảnh muốn nhóm khác lẻ tẻ để đổi hình
GHI_DE_NHOM = {54: "tainghe", 55: "xuong", 56: "tainghe", 57: "tien", 58: "giay", 60: "tien", 61: "xuong", 62: "tien", 63: "kho",
               84: "dt", 86: "tien", 106: "laptop", 108: "dt", 125: "dt", 126: "giay"}


def nhom_cua(i):
    for a, b, g in NHOM_THEO_DOAN:
        if a <= i <= b:
            return GHI_DE_NHOM.get(i, g)
    raise KeyError(i)


def main():
    khung = json.loads((V / "canh-khung.json").read_text(encoding="utf-8"))["scenes"]
    con_tro, dung_lan, scenes, thieu = {}, {}, [], 0

    def cap(nhom, can):
        for g in (nhom, DU.get(nhom), "laptop", "giay", "dt", "kho"):
            ds = sorted(NHOM.get(g, []), key=lambda t: dung_lan.get(t, 0))
            for ten in ds:
                bd = con_tro.get(ten, 0.0)
                if bd + can <= KHO[ten + ".mp4"]["do_dai"]:
                    con_tro[ten], dung_lan[ten] = bd + can + 0.1, dung_lan.get(ten, 0) + 1
                    return ten, bd
        return None

    for i, k in enumerate(khung):
        if i in DO_HOA:
            ke = DO_HOA[i]
        else:
            dai = k["end"] - k["start"] + 0.5
            got = cap(nhom_cua(i), dai)
            if got is None:
                thieu += 1
                ke = M("tai-lieu", "Hồ sơ")
            else:
                ten, bd = got
                e = KHO[ten + ".mp4"]
                out = broll.nhap(broll.KHO / e["tep"], V, e["ghi_cong"], bat_dau=bd, do_dai=dai, hau_to=f"-{i:03d}")
                ke = {"mau": "b-roll", "video": out.name, "nhan": ""}
        scenes.append({"id": k["id"], **ke, "start": k["start"], "end": k["end"]})
    (V / "canh.json").write_text(json.dumps({"scenes": scenes}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(scenes), "cảnh;", sum(s["mau"] == "b-roll" for s in scenes), "b-roll;", thieu, "cảnh hết clip thật")


if __name__ == "__main__":
    main()
