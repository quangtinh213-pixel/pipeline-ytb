import json

from tttc import ban_do

QUAD = {"type": "Feature", "properties": {"ADM0_A3": "AAA", "NAME_VI": "Nước A"},
        "geometry": {"type": "Polygon", "coordinates": [[[0, 0], [10, 0.01], [20, 0], [20, 10], [0, 10], [0, 0]]]}}
ISLAND = {"type": "Feature", "properties": {"ADM0_A3": "BBB", "NAME_VI": ""},
          "geometry": {"type": "MultiPolygon", "coordinates": [[[[50, 50], [60, 50], [60, 60], [50, 60], [50, 50]]],
                                                             [[[70, 70], [70.01, 70], [70.01, 70.01], [70, 70]]]]}}


def test_simplify_drops_nearly_collinear_points_but_keeps_corners():
    ring = [[0, 0], [10, 0.01], [20, 0], [20, 10], [0, 10], [0, 0]]
    out = ban_do.don_gian(ring, 0.15)
    assert [10, 0.01] not in out and [20, 10] in out and out[0] == out[-1]


def test_tao_writes_codes_names_and_drops_tiny_rings(tmp_path):
    src, dst = tmp_path / "ne.geojson", tmp_path / "nuoc.json"
    src.write_text(json.dumps({"type": "FeatureCollection", "features": [QUAD, ISLAND]}), encoding="utf-8")
    ban_do.tao(src, dst)
    d = json.loads(dst.read_text(encoding="utf-8"))
    assert set(d["nuoc"]) == {"AAA", "BBB"} and d["nuoc"]["AAA"]["ten"] == "Nước A"
    assert len(d["nuoc"]["BBB"]["vong"]) == 1  # vòng 0,01° bị bỏ, vòng lớn giữ lại
    assert "Natural Earth" in d["nguon"]


def test_chon_keeps_only_countries_touching_the_view(tmp_path):
    nuoc = {"AAA": {"ten": "A", "vong": [[[0, 0], [20, 0], [20, 10], [0, 0]]]}, "BBB": {"ten": "B", "vong": [[[50, 50], [60, 50], [60, 60], [50, 50]]]}}
    assert set(ban_do.chon(nuoc, -5, 25, -5, 15)) == {"AAA"}
    assert set(ban_do.chon(nuoc, -5, 100, -5, 100)) == {"AAA", "BBB"}


def test_shipped_data_covers_the_countries_of_our_stories():
    d = ban_do.doc()
    assert d is not None and {"VNM", "MYS", "THA", "USA", "CHN", "SGP"} <= set(d["nuoc"])
