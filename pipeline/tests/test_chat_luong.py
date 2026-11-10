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
    m = cl.do(_canh(PROFILE, [6.0] * 20), _timing(120, 290))
    assert any(e.startswith("Cảnh báo") and "Độ dài trung bình" in e for e in cl.kiem(m))


def test_kiem_passes_channel_like_profile():
    m = cl.do(_canh(PROFILE, [3.5] * 20), _timing(70, 234))
    loi = [e for e in cl.kiem(m) if "độ khô" not in e]  # mẫu cũ chỉ có một phông nên bị báo độ khô, đúng ý đo
    # mẫu kênh cũ (70% đồ họa) nay bị báo hai tỉ lệ: user chốt ưu tiên ảnh thật và b-roll
    assert len(loi) == 2 and "Đồ họa" in loi[0] and "đời thật" in loi[1]
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


def test_kiem_ti_le_uu_tien_doi_that():
    maus = ["b-roll"] * 5 + ["trich-bao", "so-lon", "b-roll", "bieu-do", "minh-hoa"]  # 60% đời thật, b-roll liền nhau
    m = cl.do(_canh(maus * 2, [3.5] * 20), _timing(70, 234))
    assert not [e for e in cl.kiem(m) if "Đồ họa" in e or "đời thật" in e or "liền cùng" in e]
