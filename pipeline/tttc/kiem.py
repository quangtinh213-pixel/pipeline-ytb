"""Kiểm kịch bản: mọi con số phải có nguồn [#id] trỏ tới nguon.json và khớp giá trị."""
import json
import re
import sys
import unicodedata
from pathlib import Path

TAG = re.compile(r"\[#([\w-]+)\]")
# Số kiểu Việt: dấu chấm/cách nhóm nghìn, dấu phẩy thập phân; kèm đơn vị quy mô phía sau nếu có.
NUM = re.compile(r"(?<![\d.,])(\d{1,3}(?:[ .]\d{3})+(?:,\d+)?|\d+(?:,\d+)?)(?!\d)"
                 r"(?:\s*(%|nghìn|ngàn|triệu|tỷ)(?!\w))?", re.I)
UNIT_AFTER = re.compile(r"\s*(%|nghìn|ngàn|triệu|tỷ|usd|đô|đồng|đ|\$|gb|tb)(?!\w)", re.I)
NUM_WORDS = re.compile(r"(?<!\w)(trăm|nghìn|ngàn|triệu|tỷ|phần trăm)(?!\w)", re.I)
DATE_TIME = re.compile(r"\b\d{1,2}/\d{1,2}/\d{4}\b|\b\d{1,2}:\d{2}\b")
PLACEHOLDER = re.compile(r"\[[^\]]*(?:\.\.\.|…|ĐIỀN|ĐỔI|TODO|TBD)[^\]]*\]")
LIST_MARK = re.compile(r"^\s*(?:\d+[.)]|[-*>])\s+")
URL = re.compile(r"https?://\S+")
SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?!\[#)")
WARN = ("sơ bộ", "chưa chính thức")


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


def _numbers(text: str) -> list[tuple[str, float, str]]:
    text = URL.sub(" ", TAG.sub(" ", DATE_TIME.sub(" ", PLACEHOLDER.sub(" ", text))))
    return tokens(text, keep_small=False)


def check(script_md: str, nguon: list[dict]) -> list[str]:
    script_md = unicodedata.normalize("NFC", script_md)
    by_id = {n["id"]: n for n in nguon}
    errs = []
    for line in script_md.splitlines():
        if line.lstrip().startswith("#"):
            continue
        for ph in PLACEHOLDER.findall(line):
            errs.append(f"Còn chỗ giữ chỗ chưa điền: {ph}")
        for sent in SENT_SPLIT.split(LIST_MARK.sub("", line)):
            ids = TAG.findall(sent)
            nums = _numbers(sent)
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
            allowed = {(v, sc) for s in srcs for _, v, sc in tokens(unicodedata.normalize("NFC", s["gia_tri"]))}
            for raw, v, sc in nums:
                if srcs and (v, sc) not in allowed:
                    errs.append(f"Số {raw}{' ' + sc if sc else ''} không khớp giá trị nguồn "
                                f"{[s['id'] for s in srcs]}: {sent.strip()}")
            low = sent.lower()
            for s in srcs:
                if s["trang_thai"] == "chua-xac-minh":
                    errs.append(f"Nguồn [#{s['id']}] chưa xác minh, không được dùng: {sent.strip()}")
                elif s["trang_thai"] == "so-bo" and not any(w in low for w in WARN):
                    errs.append(f"Nguồn [#{s['id']}] là số sơ bộ, câu cần ghi 'sơ bộ': {sent.strip()}")
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
