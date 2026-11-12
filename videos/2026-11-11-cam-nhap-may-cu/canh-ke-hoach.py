"""Sinh canh.json từ canh-khung.json: ưu tiên b-roll, đồ họa chỉ cho số, trích dẫn, chương.
Chạy trong pipeline/: uv run python ../videos/2026-11-11-cam-nhap-may-cu/canh-ke-hoach.py"""
import difflib
import json
from pathlib import Path

from tttc import broll

V = Path(__file__).resolve().parent
KHO = {e["tep"]: e for e in json.loads((broll.KHO / "kho.json").read_text(encoding="utf-8"))}
NHOM = {  # nhóm hình thật → các clip trong kho
    "dt": ["dien-thoai-tay-6611954", "dien-thoai-tay-853794", "luot-anh-dien-thoai-6756650", "dien-thoai-nen-trang-4884231", "dien-thoai-ban-853987"],
    "sua": ["sua-dien-thoai-6754825", "sua-dien-thoai-6754815"],
    "rac": ["rac-dien-tu-14593616"],
    "mach": ["bo-mach-chip-6755170", "bo-mach-chip-6754824", "han-mach-3866849"],
    "sanbay": ["bang-chuyen-san-bay-1169852"],
    "tainghe": ["tai-nghe-laptop-8865637"],
    "pho": ["pho-36082304", "pho-6645673"],
    "cattoc": ["cat-toc-29256985"],
    "giay": ["giay-to-7054942", "giay-to-7104084", "giay-to-7732805", "giay-to-7841618", "ky-van-ban-5311423", "viet-tay-so-tay-4017221", "con-dau-7344550"],
    "phoxa": ["duong-pho-viet-nam-35306363", "nha-viet-nam-3783794", "thanh-pho-viet-nam-31111825", "thanh-pho-viet-nam-31111952"],
    "manhinh": ["man-hinh-may-tinh-8346903"],
    "mayanh": ["may-anh-1787376"],
    "cang": ["cang-container-10391545", "cang-container-30281175"],
    "kho": ["kho-hang-giao-hang-4156510", "kho-hang-giao-hang-10472351"],
    "laptop": ["laptop-go-phim-7252685", "laptop-go-phim-853935", "go-laptop-van-phong-4928295", "laptop-ban-dem-7272375", "man-hinh-code-29458457"],
    "chip": ["nha-may-chip-32386530", "nha-may-chip-32386617", "day-chuyen-robot-32386529"],
    "tien": ["thanh-toan-the-6755016", "thanh-toan-the-11158789", "the-tin-dung-laptop-6994837", "may-tinh-tay-3860709", "may-tinh-tay-7055396"],
    "cap": ["trung-tam-du-lieu-1085656"],
    "in": ["may-in-855469"],
}
DU = {"dt": "laptop", "giay": "laptop", "laptop": "giay", "tien": "dt", "phoxa": "cang", "cang": "kho", "kho": "cang",
      "sua": "mach", "mach": "sua", "sanbay": "cang", "in": "giay", "chip": "mach", "rac": "mach"}  # nhóm dự phòng khi hết clip


def T(i, trich, vang, **k): return {"mau": "trich-bao", "nguon_id": i, "trich": trich, "to_vang": vang, **k}
def C(so, ten): return {"mau": "chuong", "so": so, "chuong": ten, "dan": {"the": "chao"}}
def M(svg, nhan, **k): return {"mau": "minh-hoa", "svg": svg, "nhan": nhan, **k}


GIA = {"trai": {"nhan": "Máy cũ đẹp", "svg": "dien-thoai", "so": 15890000, "don_vi": "đ", "to": 0.8},
       "phai": {"nhan": "Giá gạch cửa hàng ghi", "svg": "dien-thoai", "so": 22990000, "don_vi": "đ"}}
# chỉ số cảnh → nhóm b-roll (chuỗi, có thể kèm "|nhãn") hoặc cảnh đồ họa/bằng chứng (dict)
KE = {
    0: "dt|Cấm nhập từ 1/1/2027", 1: "laptop", 2: "giay",
    3: T("t3", "Thông tư số 11/2018/TT-BTTTT ngày 15 tháng 10 năm 2018", "ngày 15 tháng 10 năm 2018"),
    4: T("t13", "Danh mục sản phẩm công nghệ thông tin đã qua sử dụng cấm nhập khẩu", "đã qua sử dụng cấm nhập khẩu"),
    5: {"mau": "so-lon", "so": 8, "truoc": "hơn ", "sau": " năm", "nhan": "từ văn bản cũ tới ngày hiệu lực, kênh tự tính", "nguon_id": "n1", "svg": "lich"},
    6: "laptop", 7: "sua|Tiệm máy cũ có phải lo?",
    8: T("t1", "Thông tư số 63/2026/TT-BKHCN ngày 27 tháng 10 năm 2026", "63/2026/TT-BKHCN"),
    9: C("Phần 1", "Thông tư cấm nhập cái gì?"), 10: "giay|Phụ lục mã HS", 11: "cang",
    12: {"mau": "so-lon", "so": 13, "sau": " nhóm", "nhan": "mã HS bốn chữ số, kênh tự tính", "nguon_id": "t4", "svg": "tai-lieu"},
    13: "dt", 14: T("t5", "Bộ điện thoại, kể cả điện thoại thông minh", "điện thoại thông minh"),
    15: T("t6", "Máy xử lý dữ liệu tự động và các khối chức năng của chúng", "Máy xử lý dữ liệu tự động"),
    16: "tainghe|Loa, tai nghe", 17: "mayanh|Camera kỹ thuật số", 18: "manhinh|Màn hình, máy chiếu", 19: "laptop",
    20: "mach|Mạch in, mạch tích hợp", 21: "cap|Dây và cáp điện", 22: "giay",
    23: M("kinh-lup", "Quy tắc đọc bảng", dan={"the": "nghi"}),
    24: T("t14", "áp dụng đối với toàn bộ các mã số hàng hóa (mã HS) 08 chữ số thuộc nhóm đó", "toàn bộ"),
    25: "dt", 26: "laptop", 27: "cang|Hàng cũ từ nước ngoài",
    28: C("Phần 2", "Tân trang và linh kiện"),
    29: T("t7", "Sản phẩm công nghệ số tân trang có mã số hàng hóa (mã HS) thuộc Danh mục cấm nhập khẩu", "tân trang"),
    30: T("t15", "được sửa chữa, thay thế linh kiện để phục hồi chức năng, chất lượng và hình thức tương đương sản phẩm mới", "tương đương sản phẩm mới"),
    31: "sua|Đẹp như mới vẫn là máy cũ",
    32: T("t8", "linh kiện điện tử đã qua sử dụng của các sản phẩm thuộc Danh mục cấm nhập khẩu cũng bị cấm nhập khẩu", "cũng bị cấm nhập khẩu"),
    33: "sua", 34: "giay", 35: "tien", 36: "chip|Ngoại lệ: dự án bán dẫn",
    37: T("t9", "sản xuất, đóng gói, kiểm thử sản phẩm vi mạch bán dẫn", "vi mạch bán dẫn"),
    38: "chip", 39: "in|Máy in, máy photocopy",
    40: T("t11", "có tốc độ in/copy từ 35 bản/phút khổ giấy A4 trở lên", "35 bản/phút"),
    41: "phoxa", 42: T("t10", "trong thời hạn hiệu lực của văn bản cho phép nhập khẩu", "thời hạn hiệu lực"), 43: "giay",
    44: C("Phần 3", "Lệnh cấm này mới tới đâu?"), 45: "giay", 46: "laptop",
    47: {"mau": "so-sanh", "trai": {"nhan": "Cũ: công nghệ thông tin", "svg": "tai-lieu", "to": 0.85},
         "phai": {"nhan": "Bản mới: công nghệ số", "svg": "tai-lieu"}, "nguon_id": "t13"},
    48: M("kinh-lup", "Khác đúng một chỗ"), 49: "cang", 50: "giay", 51: "laptop",
    52: T("v1", "Hiện các cơ quan chức năng chỉ đồng bộ lại về mặt pháp lý.", "đồng bộ lại về mặt pháp lý"),
    53: "laptop", 54: "giay|Mở bản cũ ra so", 55: "laptop",
    56: T("o1", "Refurbished IT products with their HS Codes on the List provided in the Appendix hereof are prohibited", "prohibited",
          trich_vi="Sản phẩm công nghệ thông tin tân trang có mã HS thuộc Danh mục ở Phụ lục bị cấm", to_vang_vi="bị cấm"),
    57: "mach", 58: "dt",
    59: T("d4", "Thông tư 11/2018/TT-BTTTT đã quy định cấm nhập khẩu nhiều loại điện thoại, máy tính và linh kiện đã qua sử dụng.", "điện thoại, máy tính"),
    60: "giay", 61: T("t16", "Căn cứ Luật Công nghiệp công nghệ số; Căn cứ Luật Quản lý ngoại thương;", "Luật Công nghiệp công nghệ số"),
    62: "phoxa", 63: "phoxa|Đổi biển tên", 64: "cang|Hàng rào có từ trước", 65: "pho|Ví dụ: quán phở đổi biển", 66: "pho",
    67: C("Phần 4", "Vì sao lại cấm?"), 68: "giay", 69: "laptop",
    70: T("v2", "Nếu tất cả hàng hóa, thiết bị cũ được nhập khẩu vào Việt Nam sẽ sinh ra rác thải điện tử", "rác thải điện tử"),
    71: "dt", 72: "rac|Rác thải điện tử", 73: M("khien", "Dữ liệu cá nhân", dan={"the": "nghi"}), 74: "mach", 75: "laptop", 76: "rac", 77: "giay",
    78: T("h1", "Không nên đánh đồng tất cả điện thoại, máy tính cũ với rác thải điện tử.", "Không nên đánh đồng"),
    79: "dt",
    80: C("Phần 5", "Người mua máy cũ bị gì?"), 81: "dt", 82: "phoxa|Tiệm thu mua máy cũ", 83: "cang|Chỉ nói về nhập khẩu", 84: "giay", 85: "laptop",
    86: T("d1", "Việc mua bán thiết bị cũ đang lưu hành hợp pháp tại Việt Nam không thuộc phạm vi cấm nhập khẩu của Thông tư 63.", "không thuộc phạm vi cấm"),
    87: "dt", 88: "sua", 89: "sanbay|Hàng xách tay", 90: "kho",
    91: T("d2", "dù mang theo hành lý, gửi chuyển phát hay có khai báo hải quan", "mang theo hành lý"),
    92: "sanbay", 93: "laptop", 94: "giay|Biên nhận ghi số IMEI", 95: "tien", 96: "sua", 97: "cang", 98: "sanbay|Người giữ cửa: hải quan",
    99: C("Phần 6", "Giá máy cũ có lên không?"), 100: "laptop", 101: "dt",
    102: {"mau": "so-lon", "so": 15890000, "sau": " đ", "nhan": "iPhone 15 Plus 128GB cũ đẹp, CellphoneS 10/11/2026", "nguon_id": "c1", "svg": "dien-thoai"},
    103: {"mau": "so-sanh", **GIA, "ti_le": "chênh 7.100.000 đ, kênh tự tính", "nguon_id": ["c1", "c2", "c3"]},
    104: "tien", 105: "tien", 106: "dt", 107: "tien", 108: "laptop",
    109: {"mau": "so-sanh", "trai": {"nhan": "Nhập từ nước ngoài", "svg": "container"}, "phai": {"nhan": "Thu gom trong nước", "svg": "dien-thoai"}, "nguon_id": "r1"},
    110: "cang", 111: "dt",
    112: T("r3", "nguồn cung co hẹp thì khả năng mặt bằng giá máy cũ khó giảm, thậm chí nhích nhẹ theo giá máy mới", "khó giảm, thậm chí nhích nhẹ"),
    113: "kho", 114: T("r2", "khó có khả năng xảy ra đợt tăng giá đồng loạt hay khan hàng diện rộng từ đầu năm 2027", "khó có khả năng"),
    115: "laptop", 116: "sua", 117: "cattoc", 118: "giay", 119: "cang", 120: "giay", 121: "kho|Kiểm tra gắt hơn?",
    122: M("can-cung-cau", "Quy định có đổi thật?", dan={"the": "nghi"}),
    123: C("Phần 7", "Hai việc cần ngóng"), 124: "kho",
    125: T("r4", "nguy cơ các đầu nậu gom hàng trước hạn", "gom hàng trước hạn"),
    126: "cang", 127: "phoxa", 128: "giay", 129: "phoxa|Nguồn máy trong nước", 130: "dt", 131: "tien|Thu cũ đổi mới", 132: "tien", 133: "dt",
    134: C("Phần 8", "Vậy cái gì thật sự đổi?"), 135: "giay",
    136: M("tai-lieu", "Đổi tên và căn cứ", dan={"the": "xac-nhan"}),
    137: "laptop", 138: "sua", 139: "giay", 140: "tien",
    141: {"mau": "so-lon", "so": 15890000, "sau": " đ", "nhan": "hôm nay. Ngày 1/1 năm sau còn bao nhiêu?", "nguon_id": "c1", "svg": "dien-thoai"},
    142: "dt",
}


GHI_DE = {  # cụm lời đọc của bản V5 → cảnh (lời đã đổi so với V4)
    "Máy tân trang thì sao?": C("Phần 2", "Tân trang và linh kiện"),
    "Vậy lệnh cấm này mới tới đâu?": C("Phần 3", "Lệnh cấm này mới tới đâu?"),
    "Còn người mua máy cũ thì sao?": C("Phần 5", "Người mua máy cũ bị gì?"),
    "Câu khó hơn": C("Phần 6", "Giá máy cũ có lên không?"),
    "Vậy rốt cuộc lần này đổi cái gì?": C("Phần 8", "Vậy cái gì thật sự đổi?"),
    "Infonet của VietNamNet": T("i1", "Bộ điện thoại, kể cả điện thoại cho mạng di động tế bào hoặc mạng không dây khác", "điện thoại cho mạng di động"),
    "ký ngày mười lăm tháng mười": KE[3],
    "Hàng tân trang thuộc danh mục thì bản cũ": KE[56],
    "Giá mười lăm triệu tám trăm chín mươi nghìn đồng.": KE[102],
    "Ngay cạnh là một mức giá bị gạch": {"mau": "so-lon", "so": 22990000, "sau": " đ", "nhan": "giá gạch cửa hàng ghi bên cạnh", "nguon_id": "c2", "svg": "dien-thoai"},
    "Tính ra khoản chênh": KE[103],
    "bảng năm hai nghìn không trăm mười tám đều đã cấm": M("tai-lieu", "Bảng cũ đã cấm sẵn", dan={"the": "xac-nhan"}),
    "một bảng trong thông tư": T("i2", "Thông tư 11 của Bộ TT&TT sẽ thay thế Điều 3 và Phụ lục 1 của Thông tư 31 ngày 29/10/2015", "Thông tư 31 ngày 29/10/2015"),
}


def main():
    khung = json.loads((V / "canh-khung.json").read_text(encoding="utf-8"))["scenes"]
    cu = json.loads((V / "canh-khung-v4.json").read_text(encoding="utf-8"))["scenes"]  # KE đánh số theo bản chia V4
    assert set(KE) == set(range(len(cu))), "kế hoạch phải phủ đủ mọi cảnh V4"
    da_dung = set()

    def ke_cho(loi):
        for khoa, ke in GHI_DE.items():
            if khoa in loi and khoa not in da_dung:
                da_dung.add(khoa)
                return ke
        j = max(range(len(cu)), key=lambda t: difflib.SequenceMatcher(None, cu[t]["loi"], loi).ratio())
        ke, giong = KE[j], difflib.SequenceMatcher(None, cu[j]["loi"], loi).ratio()
        if isinstance(ke, str):
            return ke if giong >= 0.5 else "giay"
        khoa = json.dumps(ke, ensure_ascii=False, sort_keys=True)
        if giong < 0.75 or khoa in da_dung or (ke["mau"] == "chuong" and any(c["chuong"] == ke["chuong"] for c in GHI_DE.values() if c["mau"] == "chuong")):
            return "giay"  # lời đã đổi nhiều hoặc cảnh đồ họa này đã dùng: quay về b-roll
        da_dung.add(khoa)
        return ke
    con_tro, dung_lan, scenes, thieu = {}, {}, [], 0

    def cap(nhom, can):
        for g in (nhom, DU.get(nhom), "laptop", "giay", "dt"):
            ds = sorted(NHOM.get(g, []), key=lambda t: dung_lan.get(t, 0))  # xoay vòng: clip ít dùng trước
            for ten in ds:
                bd = con_tro.get(ten, 0.0)
                if bd + can <= KHO[ten + ".mp4"]["do_dai"]:
                    con_tro[ten], dung_lan[ten] = bd + can + 0.1, dung_lan.get(ten, 0) + 1
                    return ten, bd
        return None

    for i, k in enumerate(khung):
        ke = ke_cho(k["loi"])
        if isinstance(ke, str):
            nhom, _, nhan = ke.partition("|")
            dai = k["end"] - k["start"] + 0.5
            got = cap(nhom, dai)
            if got is None:
                thieu += 1
                ke = M("tai-lieu", nhan or "Thông tư 63")  # hết clip thật: bất đắc dĩ dùng đồ họa
            else:
                ten, bd = got
                e = KHO[ten + ".mp4"]
                out = broll.nhap(broll.KHO / e["tep"], V, e["ghi_cong"], bat_dau=bd, do_dai=dai, hau_to=f"-{i:03d}")
                ke = {"mau": "b-roll", "video": out.name, "nhan": nhan}
        scenes.append({"id": k["id"], **ke, "start": k["start"], "end": k["end"]})
    (V / "canh.json").write_text(json.dumps({"scenes": scenes}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(scenes), "cảnh;", sum(s["mau"] == "b-roll" for s in scenes), "b-roll;", thieu, "cảnh hết clip thật")


if __name__ == "__main__":
    main()
