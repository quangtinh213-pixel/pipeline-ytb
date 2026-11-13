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
