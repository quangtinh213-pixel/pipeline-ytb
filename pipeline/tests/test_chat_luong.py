import pytest

from tttc import chat_luong as cl

PROFILE = ["minh-hoa", "so-lon", "minh-hoa", "trich-bao", "minh-hoa", "bieu-do", "minh-hoa", "so-lon",
           "b-roll", "minh-hoa", "so-lon", "minh-hoa", "trang-nguon", "minh-hoa", "bieu-do", "minh-hoa",
           "so-lon", "nhan-vat", "minh-hoa", "trich-bao"]


def _canh(maus, durs):
    t, out = 0.0, []
    for i, (m, d) in enumerate(zip(maus, durs)):
        c = {"id": f"c{i}", "mau": m, "start": t, "end": t + d}
        if m == "minh-hoa":
            c["phu"] = ["cay", "dong-xu"]
        if m == "bieu-do":
            c["bieu_do"] = {"gia_tri": [1, 2, 3]}
        out.append(c)
        t += d
    return {"scenes": out}


def _timing(duration, n_words):
    step = duration / max(n_words, 1)
    return {"duration": duration,
            "words": [{"w": "từ", "start": i * step, "end": (i + 1) * step} for i in range(n_words)]}


def test_do_counts_mix_and_average():
    m = cl.do(_canh(["so-lon", "minh-hoa", "trich-bao", "b-roll"], [3, 3, 4, 2]), _timing(12, 30))
    assert m["so_canh"] == 4 and m["tb_giay"] == 3.0
    assert m["ti_le"] == {"do-hoa": 0.5, "bang-chung": 0.25, "doi-that": 0.25}


def test_do_empty_scenes_does_not_divide_by_zero():
    m = cl.do({"scenes": []}, {"duration": 0, "words": []})
    assert m["so_canh"] == 0
    assert cl.kiem(m) == ["Lỗi: canh.json không có cảnh nào"]


def test_do_longest_same_template_run():
    m = cl.do(_canh(["so-lon", "minh-hoa", "minh-hoa", "minh-hoa", "so-lon"], [3] * 5), _timing(15, 40))
    assert m["chay_dai_nhat"] == 3


def test_kiem_error_on_scene_under_1_5s():
    m = cl.do(_canh(PROFILE, [3.5] * 19 + [1.0]), _timing(68.5, 166))
    errs = [e for e in cl.kiem(m) if e.startswith("Lỗi")]
    assert len(errs) == 1 and "1,5" in errs[0]


def test_kiem_warns_on_slow_pace():
    m = cl.do(_canh(PROFILE, [13.0] * 20), _timing(260, 900))
    assert any(e.startswith("Cảnh báo") and "Độ dài trung bình" in e for e in cl.kiem(m))


def test_kiem_passes_channel_like_profile():
    m = cl.do(_canh(PROFILE, [3.5] * 20), _timing(70, 234))
    loi = [e for e in cl.kiem(m) if "độ khô" not in e and "cảnh đầu" not in e]  # mẫu cũ một phông, mở bằng chương: báo đúng ý đo
    # mẫu kênh cũ (70% đồ họa) đạt chuẩn 14/11/2026: đồ họa ≥ 70%
    assert loi == []
    assert m["su_kien_phut"] >= 30 and m["sfx_phut"] >= 15 and 180 <= m["toc_do"] <= 230


def test_main_exit_code_follows_errors(tmp_path):
    import json
    (tmp_path / "canh.json").write_text(json.dumps(_canh(PROFILE, [3.5] * 19 + [1.0])), encoding="utf-8")
    (tmp_path / "giong-timing.json").write_text(json.dumps(_timing(68.5, 166)), encoding="utf-8")
    assert cl.main(str(tmp_path)) == 1
    (tmp_path / "canh.json").write_text(json.dumps(_canh(PROFILE, [3.5] * 20)), encoding="utf-8")
    (tmp_path / "giong-timing.json").write_text(json.dumps(_timing(70, 234)), encoding="utf-8")
    assert cl.main(str(tmp_path)) == 0


def _mh(i, svg, sk="nen-dat", mq=""):
    return {"id": f"c{i}", "mau": "minh-hoa", "start": i * 3.0, "end": i * 3.0 + 3.0, "svg": svg, "san_khau": sk, "may_quay": mq}


def _ok_base():
    return cl.do(_canh(PROFILE, [3.5] * 20), _timing(70, 234))


def test_do_kho_counts_stages_runs_repeats_and_camera():
    sc = [_mh(0, "chip"), _mh(1, "laptop", "may-chu", "day-vao"), _mh(2, "chip", "may-chu"), _mh(3, "tien", "may-chu")]
    d = cl.do_kho({"scenes": sc})
    assert d["so_phong"] == 2 and d["phong_lien_max"] == 3 and d["vat_chinh_lap"] == 1 and d["ti_le_may_quay"] == 0.25


def test_do_kho_defaults_missing_stage_to_nen_dat():
    assert cl.do_kho({"scenes": [_mh(0, "chip"), _mh(1, "laptop")]})["so_phong"] == 1


def test_do_kho_separates_illustration_camera_from_broll():
    clip = {"mau": "b-roll", "video": "one.mp4"}
    scenes = [_mh(0, "chip", mq="day-vao"), clip, clip, _mh(3, "laptop")]
    got = cl.do_kho({"scenes": scenes})
    assert (got["ti_le_may_quay"], got["phong_lien_max"], got["clip_lap"]) == (0.5, 1, 1)


def test_broll_only_does_not_require_illustration_stages():
    result = _ok_base()
    result["do_kho"] = cl.do_kho({"scenes": [{"mau": "b-roll", "video": "one.mp4"}]})
    assert not [m for m in cl.kiem(result) if "độ khô" in m]


def test_do_kho_reads_director_and_judge():
    dd = {"scenes": [{"id": "c0", "trong_diem": True, "an_du": "", "may_quay": "", "nhip_cam_xuc": "mo"},
                     {"id": "c1", "trong_diem": True, "an_du": "cái cân", "may_quay": "day-vao", "nhip_cam_xuc": "chot"}]}
    cham = {"beats": [{"y_nghia": 4, "da_dang": 2, "chieu_sau": 4, "nhip": 4}]}
    d = cl.do_kho({"scenes": [_mh(0, "chip"), _mh(1, "laptop")]}, dd, cham)
    assert d["trong_diem_thieu"] == 1 and d["nhip_cam_xuc_du"] is False
    assert d["cham_thap"] == 1 and d["cham_tb"] == 3.5


def test_kiem_warns_on_each_violated_do_kho_metric():
    so_do = {**_ok_base(), "do_kho": {"so_phong": 1, "phong_lien_max": 5, "vat_chinh_lap": 2, "ti_le_may_quay": 0.0}}
    assert sum(m.startswith("Cảnh báo: độ khô:") for m in cl.kiem(so_do)) == 4


def test_kiem_do_kho_clean_when_all_metrics_met():
    so_do = {**_ok_base(), "do_kho": {"so_phong": 5, "phong_lien_max": 2, "vat_chinh_lap": 0, "ti_le_may_quay": 0.2,
                                      "trong_diem_thieu": 0, "nhip_cam_xuc_du": True, "cham_thap": 0, "cham_tb": 4.2}}
    assert [m for m in cl.kiem(so_do) if "độ khô" in m] == []


def test_camera_threshold_matches_director_rule():
    """Camera chỉ bắt buộc ở cảnh minh-hoa trọng điểm (~30% cảnh, ~một nửa là minh-hoa): chạy thử đo 18,75%, ngưỡng 15%."""
    base = {"so_phong": 5, "phong_lien_max": 2, "vat_chinh_lap": 0}
    assert [m for m in cl.kiem({**_ok_base(), "do_kho": {**base, "ti_le_may_quay": 0.1875}}) if "camera" in m] == []
    assert any("camera" in m for m in cl.kiem({**_ok_base(), "do_kho": {**base, "ti_le_may_quay": 0.10}}))


def test_old_callers_without_director_files_still_work():
    assert "do_kho" in cl.do(_canh(["minh-hoa"], [3]), _timing(3, 8))


def test_kiem_ti_le_uu_tien_do_hoa_va_han_che_stock():
    maus = ["b-roll"] * 5 + ["trich-bao", "so-lon", "b-roll", "bieu-do", "minh-hoa"]  # 60% b-roll
    sc = _canh(maus * 2, [3.5] * 20)
    for i, c in enumerate(sc["scenes"]):
        if c["mau"] == "b-roll":
            c["video"] = f"v{i}.mp4"
    assert any("Đồ họa" in e for e in cl.kiem(cl.do(sc, _timing(70, 234))))
    assert not any("kho chung" in e or "sự kiện" in e for e in cl.kiem(cl.do(sc, _timing(70, 234))))  # chưa có ghi công: bỏ qua
    gc = {f"v{i}.mp4": "Video: An trên Pexels" for i in range(20)} | {"v0.mp4": "Ảnh: VnExpress", "v1.mp4": "Minh họa"}
    m = cl.do(sc, _timing(70, 234), ghi_cong=gc)
    assert m["anh_su_kien"] == 1 and m["ti_le_stock"] == 10 / 20
    assert any("kho chung" in e for e in cl.kiem(m))
    m = cl.do(sc, _timing(70, 234), ghi_cong={"v1.mp4": "Minh họa"})
    assert any("chưa có ảnh/clip thật" in e for e in cl.kiem(m))


def test_long_stage_after_60s_allowed_only_when_layered_densely():
    def sc(buoc, start=60.0):
        dau = [{"id": f"c{i}", "mau": "so-lon", "start": i * 3.0, "end": i * 3.0 + 3.0} for i in range(int(start // 3))]
        san = {"id": "s", "mau": "quy-trinh", "start": start, "end": start + 20, "buoc": [{"nhan": "b"}] * buoc}
        return {"scenes": dau + [san]}
    assert cl.do(sc(6), _timing(80, 300))["tren_8"] == 0     # 7 sự kiện / 20 s = 21/phút
    assert cl.do(sc(3), _timing(80, 300))["tren_8"] == 1     # 4 sự kiện / 20 s = 12/phút: tĩnh
    assert cl.do(sc(6, 0.0), _timing(20, 75))["tren_8"] == 1  # 60 s đầu không được giữ lâu


def test_kiem_warns_when_first_scene_has_no_text_or_number():
    def mo(c0):
        sc = {"scenes": [dict(c0, id="c1", start=0, end=4), {"id": "c2", "mau": "so-lon", "start": 4, "end": 8}]}
        return cl.kiem(cl.do(sc, _timing(8, 30)))
    assert any("cảnh đầu" in e for e in mo({"mau": "b-roll", "video": "a.mp4"}))
    assert not any("cảnh đầu" in e for e in mo({"mau": "b-roll", "video": "a.mp4", "tu_khoa": "Giảm 2.000 đồng"}))
    assert not any("cảnh đầu" in e for e in mo({"mau": "so-lon"}))


def test_broll_counts_only_steps_it_shows():
    tron = {"scenes": [{"id": "c1", "mau": "b-roll", "start": 0, "end": 60, "video": "a.mp4"}]}
    co = {"scenes": [dict(tron["scenes"][0], tu_khoa="x", chia={"so": 1})]}
    assert cl.do(tron, _timing(60, 200))["su_kien_phut"] == 1      # chỉ cảnh, không bước nào hiện
    assert cl.do(co, _timing(60, 200))["su_kien_phut"] == 3        # cảnh + từ khoá + khung chia


def test_do_kho_warns_on_long_static_scenes():
    sc = {"scenes": [{"id": "c1", "mau": "minh-hoa", "start": 0, "end": 5.0, "svg": "tien"}]}
    so_do = {**_ok_base(), "do_kho": cl.do_kho(sc)}
    assert any("cảnh đồ họa tĩnh dài > 4,5 s" in m for m in cl.kiem(so_do))
    # có camera hoặc nhip thì không bị coi là tĩnh
    sc_cam = {"scenes": [{"id": "c1", "mau": "minh-hoa", "start": 0, "end": 5.0, "svg": "tien", "may_quay": "punch-in"}]}
    so_do_cam = {**_ok_base(), "do_kho": cl.do_kho(sc_cam)}
    assert not any("cảnh đồ họa tĩnh dài > 4,5 s" in m for m in cl.kiem(so_do_cam))


def test_do_computes_tb_giay_30s_only_for_scenes_starting_before_30s():
    sc = {"scenes": [
        {"id": "c0", "mau": "so-lon", "start": 0.0, "end": 2.0},
        {"id": "c1", "mau": "b-roll", "start": 2.0, "end": 6.0},
        {"id": "c2", "mau": "b-roll", "start": 28.0, "end": 34.0},   # start < 30 → được tính (6.0 s)
        {"id": "c3", "mau": "b-roll", "start": 30.0, "end": 42.0},   # start >= 30 → bỏ qua
    ]}
    m = cl.do(sc, _timing(42, 140))
    assert m["tb_giay_30s"] == pytest.approx((2.0 + 4.0 + 6.0) / 3)
    # không có cảnh nào start < 30 → trả về 0.0
    later = {"scenes": [{"id": "c0", "mau": "so-lon", "start": 30.0, "end": 35.0}]}
    assert cl.do(later, _timing(35, 100))["tb_giay_30s"] == 0.0


def test_kiem_30s_dau_warns_only_above_threshold():
    assert cl.kiem_30s_dau({"tb_giay_30s": 3.5}) == []
    assert cl.kiem_30s_dau({}) == []
    warns = cl.kiem_30s_dau({"tb_giay_30s": 4.2})
    assert len(warns) == 1 and "4.2 s/cảnh" in warns[0] and "3.5 s" in warns[0]
    assert len(cl.kiem_30s_dau({"tb_giay_30s": 3.2}, max_tb=3.0)) == 1
    so_do = {**_ok_base(), "tb_giay_30s": 4.2}
    assert any("30 giây đầu cắt cảnh chậm" in m for m in cl.kiem(so_do))


def test_boi_labels_count_as_layering_events():
    def san(boi):
        dau = [{"id": f"c{i}", "mau": "so-lon", "start": i * 3.0, "end": i * 3.0 + 3.0} for i in range(20)]
        return {"scenes": dau + [{"id": "s", "mau": "minh-hoa", "start": 60, "end": 80, "svg": "x",
                                  "boi": [{"chu": "A", "x": 0.5, "y": 0.5}] * boi}]}
    assert cl.do(san(0), _timing(80, 300))["tren_8"] == 1   # 4 sự kiện / 20 s: tĩnh
    assert cl.do(san(4), _timing(80, 300))["tren_8"] == 0   # 8 sự kiện / 20 s = 24/phút
    assert cl.do(san(4), _timing(80, 300))["sfx_phut"] > cl.do(san(0), _timing(80, 300))["sfx_phut"]
