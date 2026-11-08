"""Kiểm kịch bản: mọi con số phải có nguồn [#id] trỏ tới nguon.json và khớp giá trị."""
import json
import re
import sys
import unicodedata
from pathlib import Path

TAG = re.compile(r"\[#([\w-]+)\]")
NUM = re.compile(r"\d[\d.,]*\d|\d")
DATE_TIME = re.compile(r"\b\d{1,2}/\d{1,2}/\d{4}\b|\b\d{1,2}:\d{2}\b")
PLACEHOLDER = re.compile(r"\[[^\]]*(?:\.\.\.|…|ĐIỀN|ĐỔI|TODO|TBD)[^\]]*\]")
LIST_MARK = re.compile(r"^\s*(?:\d+[.)]|[-*>])\s+")
URL = re.compile(r"https?://\S+")
SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?!\[#)")
WARN = ("sơ bộ", "chưa chính thức")


def _digits(s: str) -> str:
    return re.sub(r"\D", "", s)


def _numbers(text: str) -> list[str]:
    text = URL.sub(" ", TAG.sub(" ", DATE_TIME.sub(" ", PLACEHOLDER.sub(" ", text))))
    # shortcut: số nguyên < 13 không dấu phân cách coi là đếm/tháng, bỏ qua; nếu lọt sai số liệu thì hạ ngưỡng
    return [n for n in NUM.findall(text) if not (n.isdigit() and int(n) < 13)]


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
                errs.append(f"Số {', '.join(nums)} không có nguồn: {sent.strip()}")
                continue
            allowed = {_digits(v) for s in srcs
                       for v in NUM.findall(unicodedata.normalize("NFC", s["gia_tri"]))}
            for n in nums:
                if srcs and _digits(n) not in allowed:
                    errs.append(f"Số {n} không khớp giá trị nguồn {[s['id'] for s in srcs]}: {sent.strip()}")
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
