# Tốc độ đọc VieNeu theo `toc_do` – 09/11/2026

Cách đo: chép `kich-ban.md` của video nvidia (bản V3 đã đăng, 2.032 từ) và các wav theo câu sang `videos/thu-nghiem/toc-do-<giá trị>/`, chạy `giong_vieneu.synthesize` với `vieneu.toc_do` thay đổi (wav gốc dùng lại, chỉ áp `atempo` và ghép), rồi tính `số từ / (thời lượng / 60)` từ `giong-timing.json`. Giọng "Quốc Tuấn", `pause_cau` 0,25 s, `pause_doan` 0,5 s.

| `toc_do` | Thời lượng | Tốc độ đọc |
|---|---|---|
| 1,0 (cấu hình cũ) | 489,7 s (8,2 phút) | 249,0 từ/phút (vượt 230) |
| 0,92 | 528,3 s (8,8 phút) | 230,8 từ/phút (vượt nhẹ) |
| **0,9** | 539,2 s (9,0 phút) | **226,1 từ/phút** (trong 180–230) |
| 0,88 | 550,7 s (9,2 phút) | 221,4 từ/phút |

**Chọn `toc_do` 0,9**: giá trị lớn nhất cho tốc độ nằm trong 180–230 từ/phút. Ghi `vieneu.wpm_du_kien` = 226 trong `config.json` để `python -m tttc.phong_cach` in ước tính phút đọc. Khoảng nghỉ giữa câu không co theo `atempo` nên tốc độ không tỉ lệ đúng với `toc_do`; số đo trên là của kịch bản này, kịch bản khác lệch vài từ/phút.

Hạn chế: chưa nghe lại chất lượng giọng ở 0,9 (`atempo` giữ cao độ, nhưng nghe có tự nhiên không là việc của tai bạn). Bản thử: `videos/thu-nghiem/toc-do-0.9/giong.mp3`.
