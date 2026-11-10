"""Kiểm kịch bản: mọi con số phải có nguồn [#id] trỏ tới nguon.json và khớp giá trị."""
import json
import re
import sys
import unicodedata
from decimal import Decimal
from pathlib import Path

TAG = re.compile(r"\[#([\w-]+)\]")
# Số kiểu Việt: dấu chấm/cách nhóm nghìn, dấu phẩy thập phân; kèm đơn vị quy mô phía sau nếu có.
NUM = re.compile(r"(?<![\d.,])(\d{1,3}(?:[ .]\d{3})+(?:,\d+)?|\d+(?:,\d+)?)(?!\d)"
                 r"(?:\s*(%|nghìn|ngàn|triệu|tỷ)(?!\w))?", re.I)
UNIT_AFTER = re.compile(r"\s*(%|nghìn|ngàn|triệu|tỷ|usd|đô|đồng|đ|\$|gb|tb)(?!\w)", re.I)
NUM_WORDS = re.compile(r"(?<!\w)(trăm|nghìn|ngàn|triệu|tỷ|phần trăm)(?!\w)", re.I)
WORDS = {w: i for i, w in enumerate("không một hai ba bốn năm sáu bảy tám chín".split())}
WORDS.update(mốt=1, tư=4, lăm=5)
DIGIT = "(?:" + "|".join(WORDS) + ")"
TAIL = "(?:" + "|".join(w for w in WORDS if w != "năm") + ")"
PAIR = rf"(?:{DIGIT}\s+mươi(?:\s+{TAIL})?|mười(?:\s+{TAIL})?|{DIGIT})"
TRIAD = rf"(?:{DIGIT}\s+trăm(?:\s+(?:lẻ|linh)\s+{DIGIT}|\s+{PAIR})?|{PAIR})"
THOUSANDS = rf"{TRIAD}\s+(?:nghìn|ngàn)"
MILLIONS = rf"{TRIAD}\s+triệu"
BILLIONS = rf"{TRIAD}\s+(?:(?:nghìn|ngàn)\s+)?tỷ"
SPELLED = re.compile(
    rf"(?<![\w,])(?:{BILLIONS}(?:\s+{MILLIONS})?(?:\s+{THOUSANDS})?(?:\s+{TRIAD})?"
    rf"|{MILLIONS}(?:\s+{THOUSANDS})?(?:\s+{TRIAD})?|{THOUSANDS}(?:\s+{TRIAD})?|{TRIAD})"
    rf"(?:\s+phẩy\s+{DIGIT}(?:\s+{DIGIT})*)?(?!\w)", re.I)
UNITS = re.compile(r"\s*(phần trăm|%|USD|đô la Mỹ|đô la|đô|\$|đồng|VND|đ|₫|GB|TB|gi-ga-bai|tê-ra-bai)(?!\w)", re.I)
UNIT_NAMES = {"đ": "vnd", "₫": "vnd", "đồng": "vnd", "$": "usd", "đô": "usd",
              "đô la": "usd", "đô la mỹ": "usd", "phần trăm": "%", "gi-ga-bai": "gb", "tê-ra-bai": "tb"}
SCALE_VALUE = {"": 1, "%": 1, "nghìn": 1000, "triệu": 10**6, "tỷ": 10**9, "nghìn-tỷ": 10**12}
DATE_TIME = re.compile(r"\b\d{1,2}/\d{1,2}/\d{4}\b|\b\d{1,2}:\d{2}\b")
PLACEHOLDER = re.compile(r"\[[^\]]*(?:\.\.\.|…|ĐIỀN|ĐỔI|TODO|TBD)[^\]]*\]")
LIST_MARK = re.compile(r"^\s*(?:\d+[.)]|[-*>])\s+")
URL = re.compile(r"https?://\S+")
SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?!\[#)")
WARN = ("sơ bộ", "chưa chính thức")
WARN_TU_TINH = ("tự tính", "tự ướm", "tính ra", "mình tính", "mình chia", "mình nhân", "ước tính độc lập", "không phải dự báo")
# "2.5 USD": dấu chấm thập phân kiểu Mỹ, NUM không bắt được; chỉ xét khi có đơn vị để không vướng "Gemini 2.5"
EN_DECIMAL = re.compile(r"(?<![\d.,])\d+\.\d{1,2}(?=" + UNIT_AFTER.pattern + ")", re.I)


def vi_value(raw: str) -> float:
    return float(raw.replace(" ", "").replace(".", "").replace(",", "."))


def _scale(word) -> str:
    w = (word or "").lower()
    return "nghìn" if w == "ngàn" else w


def tokens(text: str, keep_small: bool = True) -> list[tuple[str, float, str]]:
    """(chuỗi gốc, giá trị, quy mô) cho mỗi số; keep_small=False bỏ số nguyên < 13 không kèm đơn vị."""
    out = []
    for m in NUM.finditer(text):
        raw, scale = m.group(1), _scale(m.group(2))
        small = raw.isdigit() and int(raw) < 13 and not UNIT_AFTER.match(text, m.end(1))
        # shortcut: số nguyên < 13 không kèm đơn vị coi là đếm/thứ tự; nếu lọt số liệu thì hạ ngưỡng
        if keep_small or not small:
            out.append((raw, vi_value(raw), scale))
    return out


def _spoken_value(match: re.Match) -> str:
    whole, sep, decimal = match.group().lower().partition(" phẩy ")
    whole = re.sub(r"(?:nghìn|ngàn) tỷ", "nghìn-tỷ", whole)
    total = group = last = 0
    for w in whole.split():
        if w in WORDS:
            last = WORDS[w]
            group += last
        elif w == "trăm":
            group += last * 99
        elif w == "mươi":
            group += last * 9
        elif w == "mười":
            group += 10
        elif w in ("tỷ", "triệu", "nghìn", "ngàn", "nghìn-tỷ"):
            total += group * SCALE_VALUE[_scale(w)]
            group = last = 0
    return str(total + group) + ("," + "".join(str(WORDS[w]) for w in decimal.split()) if sep else "")


def _claims(text: str, keep_small: bool = False) -> list[tuple[str, Decimal, str]]:
    # Số bằng chữ dùng đúng phần kịch bản đưa vào TTS, kể cả số đọc có phần thập phân.
    text = SPELLED.sub(_spoken_value, re.sub(r"\s+", " ", text))
    out = []
    for m in NUM.finditer(text):
        raw, scale = m.group(1), _scale(m.group(2))
        end = m.end()
        if scale == "nghìn" and (ty := re.match(r"\s+tỷ\b", text[end:], re.I)):
            scale, end = "nghìn-tỷ", end + ty.end()
        unit_match = UNITS.match(text, end)
        unit = unit_match.group(1).lower() if unit_match else scale if scale == "%" else ""
        unit = UNIT_NAMES.get(unit, unit)
        if not keep_small and not scale and not unit and raw.isdigit() and int(raw) < 13:
            continue
        # shortcut: dấu âm viết dạng "âm" hoặc dấu trừ liền với số.
        sign = -1 if re.search(r"(?:[-−]|\bâm )$", text[:m.start()], re.I) else 1
        value = Decimal(raw.replace(" ", "").replace(".", "").replace(",", "."))
        out.append((text[m.start():end].strip(), sign * value * SCALE_VALUE[scale], unit))
    return out


def check(script_md: str, nguon: list[dict]) -> list[str]:
    script_md = unicodedata.normalize("NFC", script_md)
    by_id = {n["id"]: n for n in nguon}
    errs = []
    for n in nguon:  # số tự suy ra từ số khác: phải ghi công thức và trỏ về các số gốc
        if n.get("trang_thai") != "tu-tinh":
            continue
        if not str(n.get("cong_thuc", "")).strip():
            errs.append(f"Nguồn [#{n['id']}] tự tính thiếu cong_thuc")
        if not n.get("dau_vao"):
            errs.append(f"Nguồn [#{n['id']}] tự tính thiếu dau_vao (các nguồn gốc của phép tính)")
        errs += [f"Nguồn [#{n['id']}] tự tính trỏ tới dau_vao [#{i}] không có trong nguon.json"
                 for i in n.get("dau_vao") or [] if i not in by_id]
    for line in script_md.splitlines():
        if line.lstrip().startswith("#"):
            continue
        for ph in PLACEHOLDER.findall(line):
            errs.append(f"Còn chỗ giữ chỗ chưa điền: {ph}")
        declared = False  # lời khai "mình tính ra" đã xuất hiện ở câu nào đó trước trong cùng đoạn
        # Thẻ đặt sau dấu chấm vẫn thuộc câu vừa kết thúc.
        line = re.sub(r"([.!?])((?:\s*\[#[\w-]+\])+)", r"\2\1", LIST_MARK.sub("", line))
        for sent in SENT_SPLIT.split(line):
            before, declared = declared, declared or any(w in sent.lower() for w in WARN_TU_TINH)
            ids = TAG.findall(sent)
            for x in (m.group(0) for m in EN_DECIMAL.finditer(URL.sub(" ", sent))):
                errs.append(f"Số {x} dùng dấu chấm thập phân, phải viết dấu phẩy ({x.replace('.', ',')}): {sent.strip()}")
            clean = URL.sub(" ", TAG.sub(" ", DATE_TIME.sub(" ", PLACEHOLDER.sub(" ", sent))))
            nums = _claims(clean)
            srcs = []
            for i in ids:
                if i not in by_id:
                    errs.append(f"Nguồn [#{i}] không có trong nguon.json: {sent.strip()}")
                else:
                    srcs.append(by_id[i])
            if nums and not ids:
                errs.append(f"Số {', '.join(n[0] for n in nums)} không có nguồn: {sent.strip()}")
                continue
            if not ids and NUM_WORDS.search(sent):
                errs.append(f"Số viết bằng chữ không có nguồn: {sent.strip()}")
                continue
            allowed = {(v, unit) for s in srcs for _, v, unit in _claims(unicodedata.normalize("NFC", s["gia_tri"]), True)}
            for raw, v, unit in nums:
                if srcs and (v, unit) not in allowed:
                    errs.append(f"Số {raw} không khớp giá trị hoặc đơn vị nguồn "
                                f"{[s['id'] for s in srcs]}: {sent.strip()}")
            low = sent.lower()
            for s in srcs:
                if s["trang_thai"] == "chua-xac-minh":
                    errs.append(f"Nguồn [#{s['id']}] chưa xác minh, không được dùng: {sent.strip()}")
                elif s["trang_thai"] == "so-bo" and not any(w in low for w in WARN):
                    errs.append(f"Nguồn [#{s['id']}] là số sơ bộ, câu cần ghi 'sơ bộ': {sent.strip()}")
                elif s["trang_thai"] == "tu-tinh" and not (before or any(w in low for w in WARN_TU_TINH)):
                    errs.append(f"Nguồn [#{s['id']}] là số tự tính, câu cần nói rõ 'tính ra' hoặc 'tự tính': {sent.strip()}")
    return errs


def main(video_dir: str) -> int:
    d = Path(video_dir)
    errs = check((d / "kich-ban.md").read_text(encoding="utf-8"),
                 json.loads((d / "nguon.json").read_text(encoding="utf-8")))
    for e in errs:
        print("-", e)
    print(f"{len(errs)} lỗi")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
