from tttc import gop


def test_tom_gon_giu_loi_cat_canh_bao_va_bo_bang_so_do():
    dong = ["  ti_le_broll: 0.1", "- Lỗi: thiếu nguon_id ở c003"] + [f"- cảnh báo {i}" for i in range(12)] + ["1 lỗi, 12 cảnh báo"]
    ra = gop.tom_gon("chat_luong", 1, dong, toi_da=3)
    assert ra[0] == "== chat_luong: LỖI (1 lỗi, 12 cảnh báo)"
    assert "- Lỗi: thiếu nguon_id ở c003" in ra
    assert "- cảnh báo 2" in ra and "- cảnh báo 3" not in ra
    assert "còn 9 cảnh báo" in ra[-1]
    assert not any("ti_le_broll" in d for d in ra)


def test_tom_gon_day_du_giu_nguyen():
    dong = ["  a: 1", "- x", "0 lỗi"]
    assert gop.tom_gon("canh", 0, dong, day_du=True) == ["== canh", *dong]


def test_kiem_1_gom_ba_lenh(tmp_path, monkeypatch):
    (tmp_path / "kich-ban.md").write_text("# Grab giảm phí gần 3.000 tỷ: tiền về túi ai?\n", encoding="utf-8")
    monkeypatch.setattr(gop.phong_cach, "main", lambda d: print("- cảnh báo nhịp\n0 Lỗi, 1 cảnh báo") or 0)
    monkeypatch.setattr(gop.kiem, "main", lambda d: print("- Lỗi: số 5 thiếu [#id]\n1 lỗi") or 1)
    rc, ra = gop.kiem_1(tmp_path)
    assert rc == 1
    assert ra[0].startswith("== phong_cach: đạt")
    assert "== kiem: LỖI (1 lỗi)" in ra and "- Lỗi: số 5 thiếu [#id]" in ra
    assert any(d.startswith("== tieu_de:") for d in ra)


def test_render_dung_khi_kiem_canh_con_loi(tmp_path, monkeypatch):
    monkeypatch.setattr(gop, "kiem_canh", lambda d, day_du=False: (1, ["== canh: LỖI"]))
    monkeypatch.setattr(gop.dung, "compose", lambda d: (_ for _ in ()).throw(AssertionError("không được compose")))
    rc, ra = gop.render(tmp_path)
    assert rc == 1 and ra[-1].startswith("Dừng")


def test_thieu_tep_thanh_loi_khong_nem(tmp_path):
    rc, ra = gop.kiem_canh(tmp_path)
    assert rc == 1 and any("thiếu" in d for d in ra)
