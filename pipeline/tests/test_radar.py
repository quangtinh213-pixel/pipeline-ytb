import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from tttc import radar

VN = timezone(timedelta(hours=7))
FIX = Path(__file__).resolve().parent / "fixtures"


class Resp:
    def __init__(self, text, code=200, json_data=None):
        self.text, self.status_code, self._json_data = text, code, json_data

    def raise_for_status(self):
        if self.status_code != 200:
            raise RuntimeError(self.status_code)

    def json(self):
        if self._json_data is not None:
            return self._json_data
        return json.loads(self.text)


@pytest.fixture
def fixture_rss():
    return (FIX / "rss-doi-thu.xml").read_text(encoding="utf-8")


def test_doc_rss_parses_entries_in_vietnam_time_and_skips_broken(fixture_rss):
    items = radar.doc_rss("UCx", get=lambda url, **kw: Resp(fixture_rss))
    assert [i["id"] for i in items] == ["aaa111", "bbb222"] and items[0]["view"] == 11180
    assert items[0]["tieu_de"] == 'Video thử một "trích"' and items[0]["dang_luc"].utcoffset() == timedelta(hours=7)
    assert items[0]["dang_luc"].hour == 17


def test_doc_rss_raises_on_http_error_or_bad_xml():
    with pytest.raises(RuntimeError, match="RSS đối thủ"):
        radar.doc_rss("UCx", get=lambda url, **kw: Resp("", 500))
    with pytest.raises(RuntimeError, match="RSS đối thủ"):
        radar.doc_rss("UCx", get=lambda url, **kw: Resp("<not-xml"))


def test_cham_diem_weights_vietnam_angle_double_and_validates():
    assert radar.cham_diem(2, 2, 2) == 8 and radar.cham_diem(2, 2, 0) == 4 and radar.cham_diem(0, 0, 2) == 4
    with pytest.raises(ValueError):
        radar.cham_diem(3, 0, 0)


def _de(t, soc, sl, vn, moi=10):
    return {"tieu_de": t, "soc": soc, "so_lon": sl, "goc_vn": vn, "link": "u", "moi_luc": datetime(2026, 11, 9, moi, tzinfo=VN)}


def test_xep_hang_drops_below_threshold_and_orders_ties_by_vietnam_angle_then_recency():
    top = radar.xep_hang([_de("thấp", 1, 1, 0), _de("A không VN", 2, 2, 0, moi=12),
                          _de("B có VN", 1, 1, 1, moi=8), _de("C có VN mới", 1, 1, 1, moi=9)])
    assert [d["tieu_de"] for d in top] == ["C có VN mới", "B có VN", "A không VN"] and top[0]["diem"] == 4


def test_ghi_chu_de_writes_three_ranked_ideas(tmp_path):
    top = radar.xep_hang([_de(f"Đề {i}", 2, 2, 1, moi=i + 1) for i in range(5)])
    p = radar.ghi_chu_de(tmp_path, top, {"Đề 4": True})
    txt = p.read_text(encoding="utf-8")
    assert p == tmp_path / "chu-de.md" and txt.count("## Đề ") == 3
    assert "Họ đã đăng cùng sự kiện: có" in txt and "góc Việt Nam 1×2" in txt and "Họ đã đăng cùng sự kiện: chưa rõ" in txt
    assert "Từ khóa tìm kiếm gợi ý" not in txt and "bão hòa" not in txt


def test_kiem_bao_hoa_counts_recent_videos_and_respects_window(tmp_path):
    for i in range(1, 9):
        d = tmp_path / f"2026-11-{i:02d}-video"
        d.mkdir()
        if i == 1:
            # Quá cũ (ngoài 8 thư mục mới nhất khi so_ngay=4), phải bị bỏ qua
            (d / "chu-de.md").write_text("Apple và Google liên tiếp", encoding="utf-8")
        elif i in (2, 3):
            (d / "chu-de.md").write_text("Nvidia ra chip mới. Nvidia tăng mạnh.", encoding="utf-8")
        elif i == 4:
            (d / "chu-de.md").write_text("Phân tích giải pháp email văn phòng", encoding="utf-8")
        elif i == 5:
            (d / "chu-de.md").write_text("OpenAI dùng AI mới", encoding="utf-8")
        elif i == 6:
            (d / "chu-de.md").write_text("Google cạnh tranh AI", encoding="utf-8")
    (tmp_path / "2026-11-09-nvidia-apple").mkdir()  # không có chu-de.md, đếm theo tên thư mục

    res = radar.kiem_bao_hoa(tmp_path, so_ngay=4)
    assert res["nvidia"] == 3  # 2, 3, 9 (mỗi video tối đa 1 lần)
    assert res["ai"] == 2      # 5, 6 (không đếm nhầm "giai"/"email" ở video 4)
    assert "apple" not in res  # video 1 quá cũ nên apple chỉ xuất hiện ở video 9 (count=1)
    assert "google" not in res
    assert radar.kiem_bao_hoa(tmp_path / "khong-ton-tai") == {}


def test_goi_y_tu_khoa_extracts_top_5_and_handles_errors():
    calls = []

    def ok_get(url, **kw):
        calls.append((url, kw))
        payload = ["nvidia", [f"nvidia {i}" for i in range(1, 8)]]
        return Resp(json.dumps(payload), json_data=payload)

    res = radar.goi_y_tu_khoa("nvidia", get=ok_get)
    assert res == ["nvidia 1", "nvidia 2", "nvidia 3", "nvidia 4", "nvidia 5"]
    assert calls[0][0] == "https://suggestqueries.google.com/complete/search"
    assert calls[0][1]["params"] == {"client": "firefox", "ds": "yt", "hl": "vi", "q": "nvidia"}
    assert calls[0][1]["timeout"] == 5

    assert radar.goi_y_tu_khoa("nvidia", get=lambda *a, **kw: (_ for _ in ()).throw(OSError("timeout"))) == []
    assert radar.goi_y_tu_khoa("nvidia", get=lambda *a, **kw: Resp("", code=503)) == []
    assert radar.goi_y_tu_khoa("nvidia", get=lambda *a, **kw: Resp("not-json")) == []
    assert radar.goi_y_tu_khoa("nvidia", get=lambda *a, **kw: Resp("{}", json_data={})) == []


def test_ghi_chu_de_renders_suggestions_and_saturation_warning(tmp_path):
    top = radar.xep_hang([_de("Nvidia siết chip", 2, 2, 1, moi=5), _de("Tin khác", 2, 1, 1, moi=4)])
    p = radar.ghi_chu_de(
        tmp_path,
        top,
        {"Nvidia siết chip": False},
        goi_y={"Nvidia siết chip": ["nvidia trung quốc", "chip ai việt nam"]},
        bao_hoa={"nvidia": 3, "ai": 2},
    )
    txt = p.read_text(encoding="utf-8")
    assert "bão hòa" in txt.lower() and "nvidia (3 video)" in txt and "ai (2 video)" in txt
    assert "- Từ khóa tìm kiếm gợi ý: nvidia trung quốc, chip ai việt nam" in txt
    assert txt.count("Từ khóa tìm kiếm gợi ý:") == 1


def test_kiem_bao_hoa_ignores_de2_3_and_warnings_and_lowercase_ai_pronoun(tmp_path):
    d1 = tmp_path / "2026-11-12-su-co-mang"
    d1.mkdir()
    (d1 / "chu-de.md").write_text(
        "> ⚠️ Cảnh báo bão hòa chủ đề gần đây: nvidia (4 video), ai (4 video)\n\n"
        "## Đề 1: Sự cố mạng toàn cầu\nTiền về túi ai?\n\n"
        "## Đề 2: Nvidia tung chip mới\nNvidia rất mạnh.\n",
        encoding="utf-8",
    )
    d2 = tmp_path / "2026-11-13-giam-phi"
    d2.mkdir()
    (d2 / "dong-goi.json").write_text(json.dumps({
        "phuong_an": [{"tieu_de": "Giảm phí: tiền về túi ai?"}],
        "tags": ["giam phi", "xe om"],
    }, ensure_ascii=False), encoding="utf-8")
    d3 = tmp_path / "2026-11-14-chip-moi"
    d3.mkdir()
    (d3 / "dong-goi.json").write_text(json.dumps({
        "phuong_an": [{"tieu_de": "Nvidia công bố chip mới"}],
        "tags": ["nvidia"],
    }, ensure_ascii=False), encoding="utf-8")

    res = radar.kiem_bao_hoa(tmp_path, so_ngay=4)
    assert "ai" not in res
    assert "nvidia" not in res  # chỉ đếm d3 (d1 nhắc Nvidia ở warning & Đề 2 bị bỏ qua)
