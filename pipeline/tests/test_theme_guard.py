"""Chặn quay lại viết cứng màu thương hiệu: mọi hex #RRGGBB trong mã nguồn phải là màu vật thể/trung tính đã khai báo."""
import json
import re
from pathlib import Path

PIPE = Path(__file__).resolve().parents[1]
ROOT = PIPE.parent
FIX = Path(__file__).resolve().parent / "fixtures"
HEX = re.compile(r"#[0-9A-Fa-f]{6}\b")


def _sources():
    files = [*sorted((PIPE / "tttc").glob("*.py")), PIPE / "svg" / "ve.py", ROOT / "brand" / "make_brand.py"]
    for ext in ("html", "css", "js"):
        files += [p for p in sorted((PIPE / "templates").rglob(f"*.{ext}")) if "canh-demo" not in p.parts]
    return files


def test_no_brand_hex_hardcoded_outside_theme():
    allow = json.loads((FIX / "mau-vat-the.json").read_text(encoding="utf-8"))  # {"đường dẫn": ["#RRGGBB", ...]}
    bad = {}
    for p in _sources():
        rel = p.relative_to(ROOT).as_posix()
        ok = {a.upper() for a in allow.get(rel, [])}
        for hx in sorted(set(HEX.findall(p.read_text(encoding="utf-8")))):
            if hx.upper() not in ok:
                bad.setdefault(rel, []).append(hx)
    assert bad == {}, "hex chưa phân loại (đổi sang khóa theme hoặc thêm vào mau-vat-the.json kèm lý do): " + json.dumps(bad)
