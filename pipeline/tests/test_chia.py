import json

from tttc import chia


def _timing(n, per=0.4, ends=(), commas=()):
    words = []
    for i in range(n):
        w = f"từ{i}" + ("." if i in ends else "," if i in commas else "")
        words.append({"w": w, "start": round(i * per, 3), "end": round((i + 1) * per, 3)})
    return {"duration": round(n * per, 3), "words": words}


def _durs(scenes):
    return [round(s["end"] - s["start"], 3) for s in scenes]


def test_chia_covers_whole_duration_without_gaps():
    t = _timing(200, ends=range(10, 200, 11))
    sc = chia.chia(t)
    assert sc[0]["start"] == 0 and sc[-1]["end"] == t["duration"]
    assert all(a["end"] == b["start"] for a, b in zip(sc, sc[1:]))
    assert [s["id"] for s in sc][:2] == ["c001", "c002"]


def test_chia_respects_min_and_max():
    sc = chia.chia(_timing(600, ends=range(10, 600, 11)))
    assert all(2.5 - 1e-9 <= d <= 5.5 + 1e-9 for d in _durs(sc))  # 2,5 s = ngưỡng cảnh báo của canh.validate


def test_chia_prefers_sentence_end():
    sc = chia.chia(_timing(40, ends={7}, commas={8}))
    assert sc[0]["end"] == 3.2  # sau từ 7 (kết câu), không phải sau từ 8 (dấu phẩy)


def test_chia_never_returns_scene_shorter_than_min():
    for n, ends in [(10, set()), (53, {20, 21}), (47, {9, 10, 11, 30}), (31, {25})]:
        sc = chia.chia(_timing(n, ends=ends))
        assert min(_durs(sc)) >= 2.5 - 1e-9, (n, _durs(sc))


def test_chia_text_is_union_of_words():
    t = _timing(120, ends=range(8, 120, 9))
    sc = chia.chia(t)
    assert " ".join(s["loi"] for s in sc) == " ".join(w["w"] for w in t["words"])


def test_main_writes_canh_khung(tmp_path):
    (tmp_path / "giong-timing.json").write_text(json.dumps(_timing(60, ends={9, 19})), encoding="utf-8")
    assert chia.main(str(tmp_path)) == 0
    data = json.loads((tmp_path / "canh-khung.json").read_text(encoding="utf-8"))
    assert data["scenes"][0]["start"] == 0 and "loi" in data["scenes"][0]
