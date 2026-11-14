from tttc import tieu_de


def test_tieu_de_hop_le_chuan_pipeline_2():
    t = "SỐC: Ông chủ Nvidia bất ngờ từ chức! Lời hứa biến Việt Nam thành cứ điểm AI có tan thành mây khói?"
    loi = tieu_de.kiem(t)
    assert loi == []
    kq = tieu_de.cham_diem(t)
    assert kq.hop_le is True
    assert kq.diem >= 8


def test_tieu_de_thieu_tu_cam_xuc_bi_loi():
    t = "Jensen Huang rời Nvidia: ai cầm lái, khách hàng có bị gián đoạn?"
    loi = tieu_de.kiem(t)
    assert any("từ kích thích cảm xúc" in l for l in loi)


def test_tieu_de_thieu_goc_viet_nam_bi_loi():
    t = "SỐC: Lá thư chấn động làm Nvidia bốc hơi 190 tỷ USD cổ phiếu!"
    loi = tieu_de.kiem(t)
    assert any("góc liên quan Việt Nam" in l for l in loi)


def test_tieu_de_thieu_thuc_the_bi_loi():
    t = "CẢNH BÁO: Người dùng Việt Nam sắp phải chịu trận với mức giá đắt gấp đôi!"
    loi = tieu_de.kiem(t)
    assert any("thực thể/thương hiệu" in l for l in loi)


def test_tieu_de_qua_dai_100_ky_tu():
    t = "SỐC: " + "a" * 95 + " Nvidia Việt Nam túi tiền?"
    loi = tieu_de.kiem(t)
    assert any("tối đa 100 ký tự" in l for l in loi)


def test_tieu_de_iphone_cu_chuan():
    t = "Cấm bán iPhone cũ: Dân buôn ôm nợ, người dùng sắp phải mua máy đắt gấp đôi?"
    loi = tieu_de.kiem(t)
    assert loi == []
    kq = tieu_de.cham_diem(t)
    assert kq.hop_le is True


def test_tieu_de_nhan_dien_thuc_the_moi():
    for entity in ("Microsoft 365", "Outlook", "Copilot"):
        t = f"CẢNH BÁO: {entity} sập 18 giờ, người dùng Việt Nam làm việc thế nào?"
        assert tieu_de.kiem(t) == [], f"Entity {entity} phải được nhận diện"


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
