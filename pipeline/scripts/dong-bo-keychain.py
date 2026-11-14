"""Chuyển khoá của kênh (service `tui-tien-cong-nghe`) giữa Keychain macOS và Credential Manager Windows.

Máy có khoá:   uv run python scripts/dong-bo-keychain.py xuat
               -> ghi pipeline/keychain-chuyen.json (Syncthing đưa sang máy kia, git bỏ qua)
Máy cần khoá:  uv run python scripts/dong-bo-keychain.py nhap
               -> nạp vào kho khoá của máy đó rồi XOÁ file.
"""
import json
import sys
from pathlib import Path

import keyring

KR = "tui-tien-cong-nghe"
TEN = ["youtube-client", "youtube-token", "analytics-token", "elevenlabs", "pexels"]
FILE = Path(__file__).resolve().parent.parent / "keychain-chuyen.json"


def xuat() -> None:
    data = {n: v for n in TEN if (v := keyring.get_password(KR, n))}
    FILE.write_text(json.dumps(data), encoding="utf-8")
    print(f"Đã xuất {', '.join(data)} -> {FILE}")


def nhap() -> None:
    data = json.loads(FILE.read_text(encoding="utf-8"))
    for n, v in data.items():
        keyring.set_password(KR, n, v)
        assert keyring.get_password(KR, n) == v, n
    FILE.unlink()
    # Syncthing giữ bản đã xoá trong .stversions (vẫn là token chữ thường): xoá luôn ở máy này
    for cu in (FILE.parents[1] / ".stversions" / FILE.parent.name).glob(f"{FILE.stem}*"):
        cu.unlink()
    print("Ở máy đã xuất khoá: xoá tay .stversions/pipeline/keychain-chuyen* (Syncthing lưu bản cũ ở đó)")
    print(f"Đã nạp {', '.join(data)} vào {type(keyring.get_keyring()).__name__}; đã xoá {FILE.name}")


if __name__ == "__main__":
    {"xuat": xuat, "nhap": nhap}[sys.argv[1]]()
