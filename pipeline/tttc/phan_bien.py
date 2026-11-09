"""Phản biện giọng văn kịch bản với agy (Google Antigravity CLI), theo vòng. Chỉ gọi, lưu phản hồi thô, không phân tích nội dung.

Chạy: uv run python -m tttc.phan_bien vong 1 ../videos/<slug>
      uv run python -m tttc.phan_bien vong 2 ../videos/<slug> --conversation <id> --triage ../videos/<slug>/phan-bien-giong-1.md
Không dùng --dangerously-skip-permissions và --json-schema (agy không ép được định dạng trả lời).
"""
import json
import subprocess
import sys
from pathlib import Path

from tttc import tts

PIPE = Path(__file__).resolve().parent.parent
PHONG_CACH = PIPE / "phong-cach"


class AgyLoi(RuntimeError):
    """agy không chạy được hoặc không trả SUCCESS."""


def goi(prompt: str, conversation_id: str | None = None, timeout_s: int = 600, luu: Path | None = None,
        run=subprocess.run) -> dict:
    cmd = ["agy", "-p", prompt, "--output-format", "json", "--print-timeout", f"{timeout_s}s"]
    if conversation_id:
        cmd += ["--conversation", conversation_id]
    try:
        r = run(cmd, capture_output=True, text=True, timeout=timeout_s + 30)
    except FileNotFoundError:
        raise AgyLoi("không tìm thấy lệnh agy") from None
    except subprocess.TimeoutExpired:
        raise AgyLoi(f"agy quá thời gian {timeout_s}s") from None
    if luu is not None and r.stdout:
        Path(luu).write_text(r.stdout, encoding="utf-8")
    if r.returncode != 0:
        raise AgyLoi(f"agy thoát mã {r.returncode}: {r.stderr.strip()[:200]}")
    try:
        d = json.loads(r.stdout)
    except ValueError:
        raise AgyLoi("agy không trả JSON") from None
    if d.get("status") != "SUCCESS":
        raise AgyLoi(f"agy trả trạng thái {d.get('status')}")
    return {"status": d["status"], "response": d.get("response", ""), "conversation_id": d.get("conversation_id", "")}


def loi_doc(script_md: str) -> str:
    return "\n\n".join(tts.spoken_paragraphs(script_md))


def dung_prompt(vong: int, loi_doc: str, tu_cam_text: str, phan_tich: str, triage_md: str = "") -> str:
    p = ("Bạn là biên tập viên giọng văn tiếng Việt cho lời đọc video. Tình huống kể: một người theo dõi công nghệ "
         "kể lại cho bạn thân nghe ngoài quán cà phê. "
         f"Dưới đây là lời đọc (bản {vong}), danh sách từ cấm và phân tích mẫu giọng. "
         "Hãy PHÊ BÌNH, không viết lại cả đoạn, không đổi con số, không dùng tool, không sửa file.\n"
         "Nêu tối đa 12 vấn đề, mỗi vấn đề: câu trích nguyên văn | loại (sáo rỗng, văn dịch, nhịp đều, khó đọc to, "
         "bịa trải nghiệm, từ cấm, đao to búa lớn) | mức (nặng/vừa/nhẹ) | gợi ý sửa ngắn.\n"
         "Cuối cùng chấm 1–5 bốn tiêu chí: tự nhiên khi đọc to; đúng tình huống kể; nhịp; chi tiết cụ thể.\n"
         "Ràng buộc của kênh (đừng gợi ý ngược lại): (1) lời đọc đã viết số, tên riêng và thuật ngữ thành chữ để giọng đọc máy "
         "đọc đúng, nên đừng gợi ý đổi sang chữ số hay viết tắt; (2) câu cuối mời người xem bình luận một con số là bắt buộc "
         "theo thẻ phong cách, chỉ góp ý cách nói, đừng bảo bỏ; (3) phần phiên âm tên riêng là có chủ ý.\n\n"
         f"## Danh sách từ cấm\n{tu_cam_text}\n\n## Phân tích mẫu giọng\n{phan_tich}\n\n## Lời đọc\n{loi_doc}\n")
    if vong >= 2:
        p += (f"\n## Bảng triage vòng 1 (nhận/bỏ kèm lý do)\n{triage_md}\n\n"
              "Hãy kiểm lại bản đã sửa: vấn đề nặng nào chưa xử lý? Có vấn đề mới không? Chấm lại bốn điểm.\n")
    return p


def _doc(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.exists() else ""


def main(argv: list[str], run=subprocess.run) -> int:
    if len(argv) < 3 or argv[0] != "vong" or argv[1] not in ("1", "2"):
        print("dùng: python -m tttc.phan_bien vong <1|2> <thư mục video> [--conversation ID] [--triage tep.md]")
        return 2
    vong, d = int(argv[1]), Path(argv[2])
    opts = dict(zip(argv[3::2], argv[4::2]))
    conv, triage = opts.get("--conversation"), opts.get("--triage")
    if vong == 2 and not (conv and triage):
        print("vòng 2 cần --conversation <id> và --triage <tệp bảng triage vòng 1>")
        return 2
    prompt = dung_prompt(vong, loi_doc(_doc(d / "kich-ban.md")), _doc(PHONG_CACH / "tu-cam.json"),
                         _doc(PHONG_CACH / "phan-tich-giong.md"), _doc(Path(triage)) if triage else "")
    try:
        kq = goi(prompt, conv, luu=d / f"phan-bien-giong-{vong}.raw.json", run=run)
    except AgyLoi as e:
        print(f"agy lỗi: {e}")
        return 3
    (d / f"phan-bien-giong-{vong}.md").write_text(
        f"# Phản biện giọng văn, vòng {vong}\n\nconversation_id: {kq['conversation_id']}\n\n"
        f"## Phản hồi của agy\n\n{kq['response']}\n\n## Bảng triage\n\n(chưa điền)\n", encoding="utf-8")
    print(f"conversation_id: {kq['conversation_id']}")
    print(kq["response"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
