"""Chạy bằng python của VieNeu-TTS (môi trường riêng, không phải của pipeline): tạo wav cho từng job.
Dùng: ~/Documents/VieNeu-TTS/.venv/bin/python scripts/vieneu_worker.py --jobs jobs.json
jobs.json = [{"text", "out", "voice"}]; job đã có tệp `out` thì bỏ qua (chạy lại sau lỗi là tiếp tục tiếp).
"""
import json
import sys
from pathlib import Path


def main(jobs_path: str) -> None:
    jobs = [j for j in json.loads(Path(jobs_path).read_text(encoding="utf-8")) if not Path(j["out"]).exists()]
    if not jobs:
        return
    from vieneu import Vieneu
    v = Vieneu()
    for i, j in enumerate(jobs, 1):
        out = Path(j["out"])
        tmp = out.with_name(out.stem + ".tmp.wav")  # ghi xong mới đổi tên: tệp dở dang không bị coi là đã làm
        v.save(v.infer(j["text"], voice=j["voice"]), str(tmp))
        tmp.replace(out)
        print(f"[{i}/{len(jobs)}] {out.name}", flush=True)


if __name__ == "__main__":
    main(sys.argv[sys.argv.index("--jobs") + 1])
