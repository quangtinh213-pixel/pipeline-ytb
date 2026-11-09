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
    m = cl.do(_canh(PROFILE, [3.5] * 20), _timing(70, 170))
    assert cl.kiem(m) == []
    assert m["su_kien_phut"] >= 30 and m["sfx_phut"] >= 15 and 130 <= m["toc_do"] <= 160


def test_main_exit_code_follows_errors(tmp_path):
    import json
    (tmp_path / "canh.json").write_text(json.dumps(_canh(PROFILE, [3.5] * 19 + [1.0])), encoding="utf-8")
    (tmp_path / "giong-timing.json").write_text(json.dumps(_timing(68.5, 166)), encoding="utf-8")
    assert cl.main(str(tmp_path)) == 1
    (tmp_path / "canh.json").write_text(json.dumps(_canh(PROFILE, [3.5] * 20)), encoding="utf-8")
    (tmp_path / "giong-timing.json").write_text(json.dumps(_timing(70, 170)), encoding="utf-8")
    assert cl.main(str(tmp_path)) == 0
