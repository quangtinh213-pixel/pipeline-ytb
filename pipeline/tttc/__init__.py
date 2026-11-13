import sys

for _s in (sys.stdout, sys.stderr):  # cửa sổ lệnh Windows mặc định cp1252: in tiếng Việt là hỏng
    if hasattr(_s, "reconfigure") and (_s.encoding or "").lower().replace("-", "") != "utf8":
        _s.reconfigure(encoding="utf-8")
