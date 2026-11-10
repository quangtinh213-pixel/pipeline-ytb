"""Bộ nhân vật dẫn chuyện (pipeline/nhan-vat/kit.json + các PNG nền trong suốt): biểu cảm × hướng nhìn.

kit.json: {"the": [biểu cảm], "huong": [truoc|nghieng-trai|nghieng-phai|ngang...], "dang": [[the, huong], ...],
           "nham": [[the, huong], ...]}  ("nham" = cặp có thêm ảnh nhắm mắt để chớp). Tệp ảnh: tep(the, huong[, nham]).
Cảnh có `dan` bắt buộc có kit.json (nhân vật SVG "Túi" cũ đã gỡ 10/11/2026).
"""
import json
from pathlib import Path

PIPE = Path(__file__).resolve().parent.parent
KIT = PIPE / "nhan-vat" / "kit.json"


def doc_kit(path: Path | None = None) -> dict | None:
    p = KIT if path is None else Path(path)  # đọc KIT lúc gọi để test đổi được đường dẫn
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def hop_le(the: str, huong: str, kit: dict) -> bool:
    return [the, huong] in kit["dang"]


def huong_mac_dinh(goc: str) -> str:
    """Nhân vật đứng ở góc nào thì nghiêng về phía giữa màn hình."""
    return {"phai": "nghieng-trai", "trai": "nghieng-phai"}[goc]


def tep(the: str, huong: str, nham: bool = False) -> str:
    return f"{the}-{huong}{'-nham' if nham else ''}.png"


# ---- Lời nhắc tạo bộ nhân vật bằng mô hình ảnh (TobyFlow/Flow). Nhân vật "Nhịp": brief đã được người dùng duyệt 10/11/2026
# (docs/nghien-cuu/nhan-dien-ung-vien.md mục 3). Biểu cảm × góc → kit.json; mô tả bằng tiếng Anh vì mô hình ảnh hiểu tốt hơn.
BIEU_CAM = {
    "chao": "friendly greeting: eyes are two bright accent-colour arcs, small smile line, antenna dot bright",
    "ngac-nhien": "surprised: eyes are two wide bright circles, mouth a small open oval, antenna dot slightly bigger",
    "nghi": "sceptical: one eye a flat bar and the other a small circle, mouth a flat line, antenna bent sideways",
    "xac-nhan": "confirming: eyes are happy curved lines, mouth a gentle smile, a small check mark drawn inside the screen corner",
    "bo-ngo": "uncertain: eyes are two small dots at different heights, mouth a wavy line, a small question mark drawn inside the screen only",
    "tinh-toan": "calculating: eyes are two thin horizontal scanning lines, mouth a short dash, antenna dot normal size",
}
GOC = {
    "truoc": "front view, facing the camera directly",
    "nghieng-trai": "three-quarter view turned to the left of the frame",
    "nghieng-phai": "three-quarter view turned to the right of the frame",
    "ngang": "side profile view",
}
BRIEF = (
    "A small friendly robot mascot named Nhip in clean isometric flat illustration style. Rounded-cube white-grey body and head, "
    "the face is a dark LED screen showing the eyes and mouth as glowing lines in the accent colour {acc}, a short antenna with a glowing dot "
    "{acc}, soft shading using {acc2} and {acc3}, thin dark outlines {ink}. Not a human: no hair, no glasses, no clothes, no hands waving. "
    "Plain solid flat background of one single uniform bright chroma-key green colour, nothing else in the background, character centred and fully visible. "
    "no text, no logo, no real person, no watermark, flat vector look."
)


NGAN = ("The same small cube-robot mascot Nhip as in the reference images (keep the exact design, proportions, colours and outlines), "
        "isometric flat vector look, plain solid uniform bright chroma-key green background, character centred and fully visible, "
        "no text, no logo, no real person, no watermark, no glow, no halo, no rays, no extra effects outside the body.")


def tao_prompt(the: str, huong: str, nham: bool = False, ngan: bool = False) -> str:
    """Lời nhắc tạo một dáng: nhân vật + biểu cảm + góc + màu của theme; nham=True thêm 'eyes closed' (ảnh chớp mắt)."""
    from tttc import theme  # nhập trễ: theme đọc brand/theme.json lúc import
    acc, acc2, acc3 = theme.TH["nhan"]
    brief = NGAN if ngan else BRIEF.format(acc=acc, acc2=acc2, acc3=acc3, ink=theme.TH["nen"])  # ngan: thiết kế đã nằm trong ảnh tham chiếu
    p = f"{brief} Expression: {BIEU_CAM[the]}. Camera angle: {GOC[huong]}."
    return p + (" The character has eyes closed (the LED eyes are switched off, as in a blink)." if nham else "")
