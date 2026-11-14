from tttc import tieu_de


# Luật 15/11/2026 (docs/nghien-cuu/de-xuat-phat-trien-2026-11-15.md mục 1.1): một móc, không giật gân.
CHUAN = "Nvidia mất 190 tỷ USD vì một lá thư: Việt Nam mua chip AI khó hơn?"


def test_tieu_de_chuan_mot_moc_co_so_hop_le_va_diem_cao():
    assert tieu_de.kiem(CHUAN) == []
    kq = tieu_de.cham_diem(CHUAN)
    assert kq.hop_le is True and kq.canh_bao == [] and kq.diem == 10


def test_tieu_de_giat_gan_bi_loi():
    for t in ("SỐC: Ông chủ Nvidia bất ngờ từ chức! Lời hứa biến Việt Nam thành cứ điểm AI có tan thành mây khói?",
              "Sự thật vụ Microsoft nâng cấp mạng: người dùng Việt Nam chịu trận 18 giờ",
              "Lỗ hổng 7-Zip chấn động: hàng triệu máy Việt Nam có nguy cơ?"):
        assert any("giật gân" in l for l in tieu_de.kiem(t)), t


def test_nhan_canh_bao_o_dau_bi_loi_nhung_dong_tu_canh_bao_thi_khong():
    assert any("giật gân" in l for l in tieu_de.kiem("CẢNH BÁO: lỗ hổng 7-Zip 8,5/10, máy Việt Nam có dính?"))
    assert tieu_de.kiem("Microsoft cảnh báo lỗ hổng 7-Zip 8,5/10: máy Việt Nam có dính?") == []


def test_dau_cham_than_bi_loi():
    assert any("dấu chấm than" in l for l in tieu_de.kiem("Grab giảm phí 3.000 tỷ: tiền về túi tài xế!"))


def test_hai_moc_chong_nhau_bi_loi():
    assert any("hai móc" in l.lower() for l in tieu_de.kiem("Grab giảm phí 3.000 tỷ? Tiền về túi ai ở Việt Nam?"))
    assert any("hai móc" in l.lower() for l in tieu_de.kiem("Grab: giảm phí 3.000 tỷ: tiền về túi ai ở Việt Nam?"))


def test_chu_in_hoa_ca_tu_tieng_viet_bi_loi_nhung_viet_tat_thi_khong():
    assert any("in hoa" in l for l in tieu_de.kiem("Nvidia TỰ TAY mất 190 tỷ USD: Việt Nam mua chip khó hơn?"))
    assert tieu_de.kiem("CEO Nvidia mất 190 tỷ USD vì RAM, GPU: Việt Nam mua chip AI khó hơn?") == []


def test_thieu_so_thieu_goc_viet_nam_thieu_thuc_the_chi_la_canh_bao():
    t = "Jensen Huang rời Nvidia: ai cầm lái tiếp?"
    assert tieu_de.kiem(t) == []
    cb = tieu_de.cham_diem(t).canh_bao
    assert any("con số" in c for c in cb) and any("Việt Nam" in c for c in cb)
    assert any("thực thể" in c for c in tieu_de.cham_diem("Một lá thư làm mất 190 tỷ USD: Việt Nam mua chip khó hơn?").canh_bao)


def test_cham_diem_tru_theo_loi_va_canh_bao():
    xau = tieu_de.cham_diem("SỐC: Ông chủ Nvidia bất ngờ từ chức! Lời hứa biến Việt Nam thành cứ điểm AI có tan thành mây khói?")
    assert xau.hop_le is False and xau.diem <= 3


def test_tieu_de_qua_dai_100_ky_tu():
    t = "Nvidia " + "a" * 95 + " Việt Nam 190 tỷ?"
    loi = tieu_de.kiem(t)
    assert any("tối đa 100 ký tự" in l for l in loi)


def test_kiem_khop_nguon_canh_bao_cum_cuc_doan_va_danh_tu_chung():
    nguon = [{"gia_tri": "18 giờ", "trich_dan": "Service disruption lasted around 18 hours globally."}]
    warns = tieu_de.kiem_khop_nguon("SỐC: Ông chủ Microsoft bất ngờ từ chức khiến hệ thống sập hoàn toàn!", nguon)
    assert any("lệch nguồn" in w and "từ chức" in w for w in warns)
    assert any("lệch nguồn" in w and "sập hoàn toàn" in w for w in warns)
    assert any("Gợi ý tìm kiếm" in w and "danh từ chung" in w for w in warns)


def test_kiem_khop_nguon_khong_bao_sai_khi_trich_dan_khop_anh_viet():
    nguon_en = [{"gia_tri": "CEO", "trich_dan": "The CEO announced he will step down next quarter."}]
    assert tieu_de.kiem_khop_nguon("SỐC: CEO Nvidia bất ngờ từ chức!", nguon_en) == []

    nguon_vi = [{"gia_tri": "18 giờ", "trich_dan": "Hệ thống Microsoft 365 tê liệt hoàn toàn suốt 18 giờ."}]
    assert tieu_de.kiem_khop_nguon("CẢNH BÁO: Microsoft 365 sập hoàn toàn 18 giờ!", nguon_vi) == []


def test_kiem_bat_dau_nho_lon():
    from tttc.tieu_de import kiem
    assert any("<" in l for l in kiem("iPhone giá <10 triệu: người dùng Việt Nam mừng?"))


def test_nhan_in_hoa_mo_dau_bat_ky_bi_loi_va_bao_ca_cum():
    loi = tieu_de.kiem("NGUY CƠ: Hollywood tố web lậu 12,5 tỷ view, hàng Việt Nam bị đánh thuế?")
    assert any("giật gân" in l and "nguy cơ" in l for l in loi)
    assert any("in hoa" in l and "NGUY CƠ" in l for l in loi)


def test_hai_cham_khong_co_khoang_trang_sau_khong_tach_ve():
    t = "Việt Nam nằm sẵn trong nhóm D:1 của luật chip AI Mỹ?"
    assert tieu_de.kiem(t) == [] and not any("thực thể" in c for c in tieu_de.canh_bao(t))
    assert tieu_de.kiem("Nvidia 15:30 mất 190 tỷ USD: Việt Nam mua chip khó hơn?") == []


def test_gia_phi_tai_xe_la_goc_tui_tien():
    for t in ("Grab hạ trần phí 32%: tài xế và khách được gì?", "Cấm nhập điện thoại cũ 2027: giá iPhone cũ sẽ ra sao?"):
        assert not any("Việt Nam hoặc túi tiền" in c for c in tieu_de.canh_bao(t)), t
