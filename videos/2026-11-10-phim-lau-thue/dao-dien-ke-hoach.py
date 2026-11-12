"""Sinh dao-dien.json (bước đạo diễn) cho video phim lậu và thuế hàng Việt.
Mỗi cảnh chọn mẫu theo điều nó phải làm cho người xem, không ưu tiên mẫu nào. Cảnh "br:<nhóm>" lấy clip thật trong kho theo nhóm.
Chạy trong pipeline/: uv run python ../videos/2026-11-10-phim-lau-thue/dao-dien-ke-hoach.py
rồi: uv run python -m tttc.dao_dien ../videos/2026-11-10-phim-lau-thue"""
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
    "xuong": ["nha-may-chip-32386617", "nha-may-chip-32386530", "day-chuyen-robot-32386529"],
    "tainghe": ["tai-nghe-laptop-8865637"],
}
DU = {"cang": "kho", "kho": "cang", "mang": "laptop", "xuong": "kho", "tainghe": "dt", "tien": "giay", "dt": "laptop", "giay": "laptop", "laptop": "giay"}


def T(i, trich, vang, vi=None, vang_vi=None, **k):
    d = {"mau": "trich-bao", "nguon_id": i, "trich": trich, "to_vang": vang, **k}
    if vi:
        d.update(trich_vi=vi, to_vang_vi=vang_vi)
    return d


H1 = T("h1", "extend for three months the ongoing Section 301 investigation", "three months",
       "Gia hạn thêm ba tháng cuộc điều tra đang diễn ra theo Điều 301", "Gia hạn thêm ba tháng")
H1b = T("h1", "extend for three months the ongoing Section 301 investigation", "ongoing Section 301 investigation",
        "Gia hạn thêm ba tháng cuộc điều tra đang diễn ra theo Điều 301", "cuộc điều tra đang diễn ra")
L2 = T("l2", "without regard to whether or not such goods or economic sector were involved", "without regard",
       "Bất kể hàng hóa hay ngành kinh tế đó có liên quan đến vụ việc hay không", "Bất kể hàng hóa hay ngành kinh tế đó có liên quan")
F1 = T("f1", "impose 12.5 percent tariffs on products of Vietnam, except as provided", "12.5 percent",
       "Áp thuế 12,5% đối với sản phẩm của Việt Nam, trừ các ngoại lệ được quy định", "12,5%")
U2 = T("u2", "extensive libraries of pirated movies and TV shows.", "pirated movies and TV shows",
       "Những thư viện lớn chứa phim và chương trình truyền hình phát trái phép.", "phát trái phép")
U1 = T("u1", "the failure to provide persistent and effective enforcement to combat online piracy.", "persistent and effective enforcement",
       "Việc không bảo đảm thực thi bền bỉ và hiệu quả để chống vi phạm bản quyền trực tuyến.", "bền bỉ và hiệu quả")
H2 = T("h2", "no later than February 28, 2027.", "February 28, 2027", "Chậm nhất ngày 28/02/2027.", "28/02/2027")
L1 = T("l1", "impose duties or other import restrictions", "duties or other import restrictions",
       "Áp thuế hoặc các hạn chế nhập khẩu khác", "thuế hoặc các hạn chế nhập khẩu khác")
L3 = T("l3", "enter into binding agreements", "binding agreements", "Ký kết các thỏa thuận có tính ràng buộc", "thỏa thuận có tính ràng buộc")


def C(so, ten): return {"mau": "chuong", "so": so, "chuong": ten, "dan": {"the": "chao"}}
def MH(nhan, **k): return {"mau": "minh-hoa", "nhan": nhan, **k}
def SS(a, sa, b, sb, ta=0.8, **k): return {"mau": "so-sanh", "trai": {"nhan": a, "svg": sa, "to": ta}, "phai": {"nhan": b, "svg": sb}, **k}


# (nhịp, trọng điểm, y, mẫu hoặc "br:nhóm", an_du, phần thêm cho cấp trên: san_khau/vat_chinh/dao_cu/may_quay)
S = [
    # ---- Beat 1: mở
    ("mo", True, "Người xem thấy ngay câu hỏi của cả video xuất phát từ một thông báo chính thức, không phải lời đồn", H1,
     "Trích nguyên văn thông báo gia hạn làm hình đầu tiên, khớp h1; không thêm hình ngoài trang nguồn", {}),
    ("leo", False, "Cho người xem thấy chỗ đời thường nhất của chuyện phim lậu: một thao tác trên máy tính", "br:laptop", None, {}),
    ("leo", True, "Người xem hiểu hai thứ tưởng xa nhau (trang xem phim, lô hàng) đang bị nối bằng một dòng luật",
     MH("Hai chuyện, một dòng nối"), "Máy tính và container ở hai đầu, một đường nối giữa: chỉ biểu thị câu hỏi 'luật nối thế nào', khớp l2; không ngụ ý đã có thuế",
     {"san_khau": "nen-dat", "vat_chinh": "laptop", "dao_cu": ["container"], "may_quay": "lia"}),
    ("leo", False, "Đặt chuyện vào văn bản luật có thật", "br:giay", None, {}),
    ("dinh", True, "Người xem đọc được chính câu luật cho phép phạm vi vượt ra ngoài vụ việc", L2,
     "Trích nguyên văn l2, tô cụm 'without regard' để chữ luật tự nói; không thêm hình ẩn dụ", {}),
    ("ha", False, "Một nhịp thở: tờ thông báo dời hạn", "br:giay", None, {}),
    ("dao-chieu", True, "Người xem thấy mức 12,5% có thật nhưng thuộc hồ sơ khác", F1,
     "Trích f1 đặt ngay sau câu về hạn mới để thấy hai tờ giấy khác nhau; không dán nhãn 'sẽ áp'", {}),
    ("chot", False, "Hai hồ sơ cạnh nhau: cái nào đã áp dụng, cái nào còn phải đợi",
     SS("Bản quyền: đang điều tra", "tai-lieu", "Lao động: đã có thuế", "tai-lieu"), None, {}),
    # ---- Beat 2: chương bản quyền
    ("mo", False, "Mở chương", C("Phần 1", "Vì sao nói tới phim lậu?"), None, {}),
    ("leo", False, "Cho thấy Mỹ đang xem cách thực thi chứ chưa nói về một website cụ thể",
     MH("Họ xem cách thực thi", dan={"the": "nghi"}), None, {"san_khau": "co-quan", "vat_chinh": "kinh-lup", "dao_cu": ["tai-lieu"], "may_quay": "dung"}),
    ("leo", False, "Chồng hồ sơ để người xem biết mình đang đọc văn bản", "br:giay", None, {}),
    ("dinh", False, "Người xem đọc được phần nói về phim lậu đúng chữ", U2, None, {}),
    ("dao-chieu", True, "Đảo kỳ vọng: phim lậu chỉ là một phần trong hồ sơ rộng hơn",
     MH("Chỉ một phần thôi"), "Một tờ hồ sơ có một ngăn sáng, nhiều ngăn mờ: khớp u1/u2 (hàng giả, biên giới và vấn đề khác cùng nằm trong thông báo); không ngụ ý tỉ lệ",
     {"san_khau": "co-quan", "vat_chinh": "tai-lieu", "dao_cu": ["kinh-lup", "container"], "may_quay": "keo-ra"}),
    ("ha", False, "Nhắc hàng hóa ở biên giới", "br:cang", None, {}),
    ("leo", False, "Đặt câu hỏi về quy mô trước khi đưa số",
     MH("Quy mô một mạng", dan={"the": "nghi"}), None, {"san_khau": "may-chu", "vat_chinh": "may-chu", "dao_cu": [], "may_quay": "dung"}),
    ("leo", False, "Cho thấy mạng nằm trên hạ tầng máy chủ", "br:mang", None, {}),
    ("dinh", True, "Người xem nhận con số lớn đúng phạm vi: lượt truy cập của cả mạng",
     {"mau": "so-lon", "so": "6,7", "sau": " tỷ lượt", "nhan": "Fmovies và tên miền liên quan: hơn mức này, 2023–2024", "nguon_id": "a1", "svg": "may-chu"},
     "Số đứng một mình trên nền tối, nhãn nêu đủ đối tượng và kỳ đo của ACE; không vẽ đám đông hay hình tiền", {}),
    ("ha", False, "Một nhịp thở sau số lớn", "br:mang", None, {}),
    ("leo", False, "Phân biệt lượt vào trang với vé đã bán", MH("Lượt vào trang"), None,
     {"san_khau": "nen-dat", "vat_chinh": "laptop", "dao_cu": [], "may_quay": "dung"}),
    ("leo", False, "Cho thấy phép nhân giá vé là cách tính nhanh", "br:tien", None, {}),
    ("dao-chieu", False, "Chỉ ra chỗ phép tính nhanh sai: một lượt không bằng một vé", MH("Một lượt, một vé?"), None,
     {"san_khau": "nen-dat", "vat_chinh": "tien", "dao_cu": [], "may_quay": "dung"}),
    ("dao-chieu", False, "Cho thấy một người có thể mở lại nhiều lần", "br:laptop", None, {}),
    ("dinh", True, "Người xem thấy dấu hỏi nằm đúng chỗ: nguồn không cho biết ai sẽ mua vé",
     MH("Ai thật sự mua vé?", dan={"the": "bo-ngo"}),
     "Kính lúp trên túi tiền, ô giá trị để trống: khớp a1 (nguồn chỉ có lượt truy cập, không có doanh thu hay số vé); không vẽ số tiền hay đám đông",
     {"san_khau": "nen-dat", "vat_chinh": "kinh-lup", "dao_cu": ["tien"], "may_quay": "day-vao"}),
    ("ha", False, "Nhịp thở: tay lật hồ sơ", "br:giay", None, {}),
    ("chot", False, "Chốt: số này trả lời quy mô, không trả lời thiệt hại", MH("Cần dữ liệu khác"), None,
     {"san_khau": "nen-dat", "vat_chinh": "tai-lieu", "dao_cu": [], "may_quay": "dung"}),
    ("mo", False, "Mở đoạn giải thích lớp phía sau nút phát", "br:mang", None, {}),
    ("leo", True, "Người xem thấy tên trang đổi nhưng nơi lưu vẫn ở chỗ cũ",
     MH("Đổi tên, cùng nơi lưu"), "Thẻ trang đổi tên còn khối máy chủ giữ nguyên chỗ: sơ đồ cấu trúc minh họa, dán nhãn; không nói Fmovies đã làm thế",
     {"san_khau": "may-chu", "vat_chinh": "may-chu", "dao_cu": ["laptop"], "may_quay": "lia"}),
    ("dinh", True, "Người xem nhìn ba lớp: người xem, trang phát, nơi lưu video",
     {"mau": "quy-trinh", "tieu_de": "Minh họa cấu trúc", "buoc": [{"nhan": "Người xem", "svg": "nguoi"}, {"nhan": "Trang phát", "svg": "laptop"}, {"nhan": "Nơi lưu video", "svg": "may-chu"}]},
     "Ba bước nối nhau dán nhãn 'Minh họa cấu trúc'; không số liệu, không tên trang", {}),
    ("leo", False, "Đặt câu hỏi ai đứng sau", MH("Ai vận hành?"), None,
     {"san_khau": "nen-dat", "vat_chinh": "kinh-lup", "dao_cu": ["nguoi"], "may_quay": "dung"}),
    ("dao-chieu", True, "Người xem thấy hai việc khác phạm vi: chặn địa chỉ và xử lý mạng phía sau",
     SS("Chặn địa chỉ", "o-khoa", "Xử lý mạng phía sau", "may-chu"), "Hai vật cạnh nhau, vật bên phải lớn hơn: chỉ về phạm vi, không về hiệu quả; không số liệu", {}),
    ("leo", False, "Cho thấy thông tin do phía liên minh công bố", MH("Do liên minh công bố"), None,
     {"san_khau": "co-quan", "vat_chinh": "khien", "dao_cu": [], "may_quay": "dung"}),
    ("ha", False, "Nhịp thở", "br:giay", None, {}),
    ("leo", False, "Mở câu hỏi rộng hơn một trang còn mở hay không", MH("Câu hỏi rộng hơn"), None,
     {"san_khau": "co-quan", "vat_chinh": "kinh-lup", "dao_cu": ["tai-lieu"], "may_quay": "dung"}),
    ("dinh", True, "Người xem đọc được chữ 'thực thi bền bỉ và hiệu quả' từ nguồn", U1,
     "Trích nguyên văn u1; chỉ đưa câu hồ sơ nêu, không thêm lời kết luận", {}),
    ("ha", False, "Nhịp thở", "br:giay", None, {}),
    ("leo", False, "Nhắc đối tượng của điều tra là chính sách", H1b, None, {}),
    ("leo", False, "Cho thấy một website và hành vi những người liên quan", MH("Một website"), None,
     {"san_khau": "co-quan", "vat_chinh": "laptop", "dao_cu": [], "may_quay": "dung"}),
    ("dao-chieu", True, "Đổi cấp độ câu hỏi: từ một trang sang cả hệ thống",
     SS("Một website", "laptop", "Cả hệ thống thực thi", "cao-oc", ta=0.6), "Hai vật khác cỡ: nhỏ là một trang, lớn là hệ thống; chỉ cấp độ, không ngụ ý Việt Nam yếu hay mạnh", {}),
    # ---- Beat 3: chương thương mại
    ("mo", False, "Mở chương", C("Phần 2", "Vì sao một lô hàng liên quan?"), None, {}),
    ("leo", True, "Người xem thấy lại cặp đầu video: website nằm trên mạng, thuế nằm ở cửa khẩu",
     SS("Website trên mạng", "laptop", "Thuế ở cửa khẩu", "container", ta=0.7), "Cùng cặp hình ở đầu video, lần này thêm vai: cầu nối là thẩm quyền theo luật Mỹ; không thêm khẳng định", {}),
    ("leo", False, "Cho biết cầu nối là thẩm quyền theo luật", MH("Thẩm quyền theo luật Mỹ"), None,
     {"san_khau": "co-quan", "vat_chinh": "bua-phan-quyet", "dao_cu": [], "may_quay": "day-vao"}),
    ("leo", False, "Cho thấy đây là bước xem xét trên giấy", "br:giay", None, {}),
    ("leo", False, "Cho thấy việc cần xác định có cơ sở hành động hay chưa", "br:giay", None, {}),
    ("ha", False, "Cần thêm thời gian", MH("Cần thêm thời gian"), None,
     {"san_khau": "nen-dat", "vat_chinh": "dong-ho", "dao_cu": [], "may_quay": "dung"}),
    ("dinh", True, "Người xem đọc đúng ngày hạn mới", H2,
     "Trích nguyên văn h2, nhân vật xác nhận số khớp nguồn", {"dan": {"the": "xac-nhan"}}),
    ("leo", False, "Cho thấy doanh nghiệp xuất hàng làm việc với giấy tờ", "br:giay", None, {}),
    ("dinh", False, "Người xem đọc điều luật liệt kê loại biện pháp", L1, None, {}),
    ("dinh", True, "Người xem thấy phạm vi luật cho phép có thể rộng hơn ngành bị điều tra",
     MH("Cả ngành ngoài vụ việc"), "Khung mở rộng từ một ngành sang nhiều ngành: chỉ phạm vi luật cho phép (l2), không nói đã có thuế",
     {"san_khau": "cang", "vat_chinh": "tai-lieu", "dao_cu": ["container", "laptop"], "may_quay": "keo-ra"}),
    ("dao-chieu", False, "Nhắc phạm vi có thể vượt ra ngoài bản quyền số", "br:cang", None, {}),
    ("leo", False, "Báo trước còn một đường khác", "br:giay", None, {}),
    ("dinh", False, "Người xem đọc điều luật về thỏa thuận ràng buộc", L3, None, {}),
    ("ha", False, "Cho thấy hai bên đọc văn bản cam kết", "br:giay", None, {}),
    ("ha", False, "Cho thấy hướng thứ hai: danh sách hàng hóa", MH("Danh sách hàng hóa"), None,
     {"san_khau": "nen-dat", "vat_chinh": "tai-lieu", "dao_cu": [], "may_quay": "dung"}),
    ("leo", False, "Mở ví dụ giả định về một sản phẩm", "br:tainghe", None, {}),
    ("leo", False, "Cho thấy món hàng trong ví dụ", "br:tainghe", None, {}),
    ("leo", False, "Cho thấy nơi lắp ráp", "br:xuong", None, {}),
    ("dinh", True, "Người xem thấy chuyện quyết định nằm ở mã hàng có trong danh sách hay không",
     MH("Mã hàng: cần đối chiếu"), "Container thay cho lô hàng giả định, bên cạnh tờ danh sách và kính lúp, nhãn 'giả định'; không nêu hãng hay mã cụ thể",
     {"san_khau": "cang", "vat_chinh": "container", "dao_cu": ["tai-lieu", "kinh-lup"], "may_quay": "day-vao"}),
    ("leo", False, "Cho thấy chi phí nhập có thể đổi", "br:tien", None, {}),
    ("dao-chieu", False, "Nhánh khác: miễn hoặc biện pháp khác", "br:giay", None, {}),
    ("leo", True, "Người xem thấy ai đứng đầu chuỗi chịu chi phí trước và ai ở sau",
     {"mau": "quy-trinh", "tieu_de": "Ví dụ giả định", "buoc": [{"nhan": "Nhà nhập khẩu", "svg": "container"}, {"nhan": "Nhà máy", "svg": "nha-may"}, {"nhan": "Người mua", "svg": "nguoi"}]},
     "Chuỗi ba bên nối bằng mũi tên, mỗi bên có thể chia hoặc không chia chi phí: khớp lời đọc ví dụ, dán nhãn giả định; không số liệu", {}),
    ("leo", False, "Cho thấy việc thương lượng chi phí", "br:tien", None, {}),
    ("ha", False, "Nhịp thở sau chuỗi ví dụ", "br:xuong", None, {}),
    ("leo", False, "Cho thấy giá trên kệ phụ thuộc người bán", "br:tien", None, {}),
    ("ha", False, "Giá không tự nhảy bằng thuế suất", MH("Giá không tự nhảy"), None,
     {"san_khau": "nen-dat", "vat_chinh": "thue-phan-tram", "dao_cu": [], "may_quay": "dung"}),
    ("chot", False, "Đưa mắt về cảng", "br:cang", None, {}),
    ("dinh", True, "Người xem nhận quy mô nhập khẩu một tháng, gắn đúng nguồn",
     {"mau": "so-lon", "so": "28,7", "sau": " tỷ USD", "nhan": "Mỹ nhập từ Việt Nam · tháng 9/2026", "nguon_id": "c1", "svg": "container"},
     "Số lớn trên nền tối có hình container mờ, nhãn nêu tháng và hướng nhập; không so với mức thuế", {}),
    ("ha", False, "Nhịp thở sau số lớn", "br:cang", None, {}),
    ("leo", False, "Nhắc cần xem danh sách đi kèm", MH("Cần xem danh sách"), None,
     {"san_khau": "nen-dat", "vat_chinh": "tai-lieu", "dao_cu": [], "may_quay": "dung"}),
    ("dao-chieu", True, "Người xem thấy số nhập lớn không đồng nghĩa mọi hàng chịu thuế",
     MH("Số lớn chưa đủ"), "Container lớn đứng sau tấm khiên mờ: chỉ 'số nhập ≠ phạm vi biện pháp'; không nói hàng nào được miễn",
     {"san_khau": "cang", "vat_chinh": "container", "dao_cu": ["khien"], "may_quay": "lia"}),
    ("ha", False, "Nhịp thở", "br:giay", None, {}),
    ("leo", False, "Cho thấy góc nhìn bảng thương mại", "br:tien", None, {}),
    ("leo", False, "Cho thấy góc nhìn bàn đàm phán", "br:laptop", None, {}),
    ("ha", False, "Cùng lô hàng hai cách nhìn", "br:giay", None, {}),
    ("chot", False, "Chốt: hàng gì, điều kiện nào, chạm hay không", MH("Hàng gì, điều kiện nào?"), None,
     {"san_khau": "nen-dat", "vat_chinh": "kinh-lup", "dao_cu": ["tai-lieu"], "may_quay": "dung"}),
    # ---- Beat 4: chương Việt Nam
    ("mo", False, "Mở chương, câu hỏi người xem hay hỏi", C("Phần 3", "Hai hồ sơ cùng tên điều luật"), None, {"dan": None}),
    ("dinh", True, "Người xem đọc mức 12,5% và biết nó thuộc vụ lao động cưỡng bức",
     {"mau": "so-lon", "so": "12,5", "sau": " %", "nhan": "thuộc vụ lao động cưỡng bức, có ngoại lệ", "nguon_id": "f1", "svg": "thue-phan-tram"},
     "Số lớn mang nhãn vụ lao động cưỡng bức, ghi rõ có ngoại lệ; không nhãn 'sẽ áp thêm'", {}),
    ("leo", False, "Mở đúng hồ sơ", "br:giay", None, {}),
    ("leo", False, "Cho thấy đây là hồ sơ riêng", "br:giay", None, {}),
    ("dao-chieu", True, "Người xem thấy hai hồ sơ cạnh nhau, cùng tên điều luật nhưng khác vụ",
     SS("Vụ bản quyền", "tai-lieu", "Vụ lao động cưỡng bức", "tai-lieu"), "Hai tờ giống nhau về dáng, nhãn khác nhau: chỉ 'cùng điều luật, khác vụ' (h1, f1); không số liệu", {}),
    ("leo", False, "Một bên đã công bố, một bên chờ", "br:giay", None, {}),
    ("leo", False, "Cho thấy hồ sơ vừa dời hạn", "br:laptop", None, {}),
    ("leo", False, "Cảnh báo nhầm kết quả", MH("Đừng gán nhầm hồ sơ"), None,
     {"san_khau": "co-quan", "vat_chinh": "kinh-lup", "dao_cu": ["tai-lieu"], "may_quay": "dung"}),
    ("ha", False, "Nhịp thở", "br:giay", None, {}),
    ("leo", False, "Mở ví dụ đơn hàng nội thất", "br:kho", None, {}),
    ("leo", False, "Bên mua gửi một đường dẫn", "br:dt", None, {}),
    ("leo", False, "Việc đầu tiên: xem văn bản nói vụ nào", "br:giay", None, {}),
    ("leo", False, "Bên kế toán cần tờ có thuế suất", "br:tien", None, {}),
    ("leo", False, "Bên hợp đồng cần mốc theo dõi", "br:giay", None, {}),
    ("ha", False, "Thống nhất lúc mở lại báo giá", "br:laptop", None, {}),
    ("chot", False, "Hai việc, hai loại thông tin", SS("Để tính giá", "tien", "Để biết mốc", "lich"), None, {}),
    ("mo", False, "Nêu câu dễ trượt: hạn mới đến, thuế tự chạy", MH("Hạn đến, thuế chạy?", dan={"the": "nghi"}), None,
     {"san_khau": "co-quan", "vat_chinh": "lich", "dao_cu": [], "may_quay": "dung"}),
    ("leo", False, "Người xem đọc lại đúng ngày hạn", H2, None, {}),
    ("dinh", True, "Người xem thấy lịch ở trước còn ô biện pháp còn trống",
     MH("Hạn mới, chưa phải thuế"), "Tờ lịch đã đánh dấu, ô thuế bên cạnh để trống: khớp h2 và l1 (biện pháp chỉ là khả năng); không điền mức thuế nào",
     {"san_khau": "co-quan", "vat_chinh": "lich", "dao_cu": ["thue-phan-tram"], "may_quay": "he-lo"}),
    ("ha", False, "Thông báo chưa đưa danh sách mã hàng", "br:giay", None, {}),
    ("leo", False, "Hình dung hai email đến cùng lúc", MH("Hai email", dan={"the": "nghi"}), None,
     {"san_khau": "nen-dat", "vat_chinh": "hop-thu", "dao_cu": [], "may_quay": "dung"}),
    ("leo", False, "Email thứ nhất: dời lịch họp", "br:laptop", None, {}),
    ("leo", False, "Email thứ hai: phụ lục hợp đồng", "br:laptop", None, {}),
    ("dinh", True, "Người xem thấy chỉ một trong hai tờ đủ thông tin để đổi giá",
     SS("Email dời lịch", "hop-thu", "Phụ lục giá mới", "tai-lieu", ta=0.6), "Hai thư cạnh nhau, tờ phụ lục dày hơn: ví dụ giả định về loại văn bản, không số liệu", {}),
    ("chot", False, "Đọc đúng loại giấy trước", "br:giay", None, {}),
    # ---- Beat 5: hai tín hiệu
    ("mo", False, "Mở chương hai tín hiệu", C("Phần 4", "Hai tín hiệu cần theo dõi"), None, {}),
    ("leo", True, "Người xem biết tín hiệu đầu là phần quyết định của văn bản kết luận",
     MH("Tìm phần quyết định"), "Cán cân đặt giữa tờ văn bản, chưa nghiêng bên nào: chỉ nói 'đọc phần quyết định trước'; không dự báo kết quả",
     {"san_khau": "co-quan", "vat_chinh": "bua-phan-quyet", "dao_cu": ["tai-lieu"], "may_quay": "day-vao"}),
    ("leo", False, "Đoạn về biện pháp", "br:giay", None, {}),
    ("leo", False, "Chữ thuế mới chưa phải điểm dừng", MH("Thuế mới, rồi sao?"), None,
     {"san_khau": "nen-dat", "vat_chinh": "thue-phan-tram", "dao_cu": [], "may_quay": "dung"}),
    ("dinh", False, "Ba câu hỏi cần hỏi tiếp", MH("Hàng nào, ngoại lệ?"), None,
     {"san_khau": "nen-dat", "vat_chinh": "kinh-lup", "dao_cu": ["tai-lieu"], "may_quay": "day-vao"}),
    ("ha", False, "Giữ đúng chữ khi kể lại", "br:giay", None, {}),
    ("leo", False, "Chuyển sang tín hiệu thứ hai", MH("Tín hiệu thứ hai"), None,
     {"san_khau": "may-chu", "vat_chinh": "may-chu", "dao_cu": [], "may_quay": "dung"}),
    ("leo", False, "Vụ đóng web trên hạ tầng mạng", "br:mang", None, {}),
    ("leo", False, "Theo dõi thông báo cơ quan và bên giữ quyền", "br:laptop", None, {}),
    ("ha", False, "Người làm phim thấy ngay một đường dẫn biến mất", "br:dt", None, {}),
    ("dinh", True, "Người xem thấy khác biệt giữa địa chỉ biến mất và mạng đứng sau ngừng hẳn",
     SS("Địa chỉ biến mất", "o-khoa", "Mạng ngừng hoạt động", "may-chu", ta=0.5), "Hai trạng thái cạnh nhau, không mũi tên nhân quả: đúng với lời 'mới cho biết xử lý sâu đến đâu'; không khẳng định vụ nào đã ngừng hẳn", {}),
    ("leo", False, "Ví dụ hãng phim đã cấp quyền", "br:giay", None, {}),
    ("leo", False, "Cần đầu mối để gửi bằng chứng", "br:laptop", None, {}),
    ("leo", False, "Việc xử lý có theo được khi trang đổi địa chỉ", MH("Đổi địa chỉ, theo được?"), None,
     {"san_khau": "may-chu", "vat_chinh": "kinh-lup", "dao_cu": ["laptop"], "may_quay": "lia"}),
    ("dao-chieu", False, "Người xem chỉ thấy nút phát biến mất", "br:dt", None, {}),
    ("ha", False, "Đáng theo dõi dù chưa có quyết định mới", "br:giay", None, {}),
    ("mo", False, "Giữ đúng thứ tự khi nhìn hai tín hiệu", MH("Giữ đúng thứ tự"), None,
     {"san_khau": "nen-dat", "vat_chinh": "bac-thang", "dao_cu": [], "may_quay": "dung"}),
    ("leo", False, "Một vụ đóng trang là sự kiện thực thi", "br:mang", None, {}),
    ("dinh", True, "Người xem thấy hai loại sự kiện cùng chủ đề nhưng khác hồ sơ, khác cơ quan",
     SS("Sự kiện thực thi", "bua-phan-quyet", "Sự kiện thương mại", "thue-phan-tram", ta=0.85), "Hai vật cạnh nhau, không mũi tên giữa chúng: đúng lời 'hồ sơ, cơ quan, hệ quả khác nhau'; không ngụ ý cái này gây ra cái kia", {}),
    ("ha", False, "Khác hồ sơ, khác cơ quan, khác hệ quả", MH("Khác hồ sơ, khác hệ"), None,
     {"san_khau": "co-quan", "vat_chinh": "tai-lieu", "dao_cu": [], "may_quay": "dung"}),
    ("chot", False, "Mở đúng văn bản là cách nhanh nhất", "br:laptop", None, {}),
    # ---- Beat 6: kết
    ("mo", False, "Mở chương kết", C("Phần 5", "Web phim lậu dính gì tới thuế?"), None, {}),
    ("leo", False, "Việc thực thi bản quyền nằm trong điều tra thương mại", "br:cang", None, {}),
    ("dinh", True, "Người xem đọc lại câu luật làm lý do nhà xuất khẩu theo dõi", L2,
     "Nhắc lại trích l2 đã dùng ở đầu video để khép vòng; không hình mới", {}),
    ("ha", False, "Bởi vậy nhà xuất khẩu có lý do theo dõi", "br:cang", None, {}),
    ("ha", False, "Lần tới: kết luận, đề xuất hay quyết định chốt", "br:giay", None, {}),
    ("chot", False, "Mời bình luận số một hoặc số hai", MH("Bình luận 1 hoặc 2"), None,
     {"san_khau": "nen-dat", "vat_chinh": "hop-thu", "dao_cu": [], "may_quay": "dung"}),
    ("chot", False, "Khép video", "br:dt", None, {}),
]


# Điều chỉnh sau số đo: đồ họa ≤ 40%, thêm một phông, bớt lặp hình chính
def _br(i, g): S[i] = (S[i][0], S[i][1], S[i][2], "br:" + g, None, {})
_br(20, "tien"); _br(67, "giay"); _br(81, "giay"); _br(115, "mang"); _br(125, "giay")
def _vc(i, vc, dc=None):
    S[i] = (*S[i][:5], {**S[i][5], "vat_chinh": vc, "dao_cu": dc if dc is not None else S[i][5].get("dao_cu", [])})
_vc(28, "nguoi", ["kinh-lup"]); _vc(32, "cao-oc", []); _vc(90, "dong-ho", [])
S[63] = (*S[63][:5], {**S[63][5], "san_khau": "thanh-pho"})


def main():
    khung = json.loads((V / "canh-khung.json").read_text(encoding="utf-8"))["scenes"]
    assert len(S) == len(khung), (len(S), len(khung))
    con_tro, dung_lan, out = {}, {}, []

    def cap(nhom, can):
        for g in (nhom, DU.get(nhom), "laptop", "giay", "dt", "kho"):
            for ten in sorted(NHOM.get(g, []), key=lambda t: dung_lan.get(t, 0)):
                bd = con_tro.get(ten, 0.0)
                if bd + can <= KHO[ten + ".mp4"]["do_dai"]:
                    con_tro[ten], dung_lan[ten] = bd + can + 0.1, dung_lan.get(ten, 0) + 1
                    return ten, bd
        return None

    for i, (k, (nhip, td, y, spec, an_du, extra)) in enumerate(zip(khung, S)):
        d = {"id": k["id"], "y": y, "nhip_cam_xuc": nhip, "trong_diem": td}
        if an_du:
            d["an_du"] = an_du
        if isinstance(spec, str):
            dai = k["end"] - k["start"] + 0.5
            got = cap(spec.split(":")[1], dai)
            if got is None:
                raise SystemExit(f"hết clip cho cảnh {i} ({spec})")
            ten, bd = got
            e = KHO[ten + ".mp4"]
            f = broll.nhap(broll.KHO / e["tep"], V, e["ghi_cong"], bat_dau=bd, do_dai=dai, hau_to=f"-{i:03d}")
            d["canh"] = {"mau": "b-roll", "video": f.name, "nhan": ""}
        else:
            d["canh"] = dict(spec)
        for key in ("san_khau", "vat_chinh", "dao_cu", "may_quay"):
            if key in extra:
                d[key] = extra[key]
        if extra.get("dan"):
            d["canh"]["dan"] = extra["dan"]
        out.append(d)
    (V / "dao-dien.json").write_text(json.dumps({"scenes": out}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(out), "cảnh;", sum(d["trong_diem"] for d in out), "trọng điểm;", sum(d["canh"]["mau"] == "b-roll" for d in out), "b-roll")


if __name__ == "__main__":
    main()
