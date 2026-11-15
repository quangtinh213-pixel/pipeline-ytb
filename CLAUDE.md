# Nhịp Công Nghệ – pipeline video YouTube tự động

Kênh tin công nghệ–kinh tế tiếng Việt. Mỗi ngày một video dài (8–11 phút) và 2–3 Shorts, đi qua ba chặng, mỗi chặng dừng ở một điểm duyệt của người dùng.

## Ba chặng (skill trong `.claude/skills/`)

| Lệnh | Việc | Dừng ở |
|------|------|--------|
| `/video-moi [chủ đề]` | radar chọn đề → đọc nguồn gốc → kịch bản gắn `[#id]` nguồn → tự kiểm + phản biện giọng | duyệt 1 (`duyet-1.html`) |
| `/video-dung [thư mục]` | giọng VieNeu → chia cảnh → hình/b-roll → render HyperFrames → tiêu đề/thumbnail/mô tả; tối đó dựng Shorts | duyệt 2 (`duyet-2.html`) |
| `/video-dang [thư mục]` | upload riêng tư + hẹn giờ (mặc định 15:30), Shorts sáng hôm sau | — |

Mỗi chặng chạy trong một phiên riêng (`/clear` giữa các chặng); kiểm và render gộp bằng `tttc.gop` (`kiem-1`, `kiem-canh`, `render`); việc nhiều trang web/ảnh chụp giao subagent `sonnet`. Lý do: phiên chạy liền các chặng phình tới 558k ngữ cảnh.

Không tự chọn phương án ở điểm duyệt, không tự chạy `duyet-short`. Trạng thái từng video nằm trong `tttc.trang_thai` (`load`, `set_step`, `next_step`).

## Cấu trúc

- `pipeline/tttc/` – mã chính (một module một bước: `radar`, `kiem`, `phong_cach`, `tieu_de`, `phan_bien`, `giong_vieneu`, `chia`, `canh`, `dao_dien`, `dung`, `chat_luong`, `thumb`, `duyet`, `dang`, `giam_sat`, `theo_doi`…).
- `pipeline/tests/` – pytest, mỗi module một tệp `test_<module>.py`.
- `pipeline/scripts/` – việc chạy tay: `dong-bo-view.py` (đồng bộ view + đối thủ vào sổ), `render.sh`, `vieneu_worker.py`.
- `pipeline/config.json` – nguồn tin, giờ đăng mặc định, phiên âm VieNeu (`vieneu.phat_am`), kênh đối thủ.
- `videos/<yyyy-mm-dd-slug>/` – mỗi video một thư mục: `chu-de.md`, `nguon.json`, `kich-ban.md`, `canh.json`, `dong-goi.json`, `thumbnails/`. mp3/mp4/frames/composition bị bỏ qua khỏi git.
- `docs/` – `phong-cach-kich-ban.md` (thẻ phong cách, bắt buộc theo khi viết), `template-kich-ban.md`, `quy-tac-quyet-dinh.md` (luật đọc sổ), `superpowers/specs|plans` (thiết kế), `nghien-cuu/`.
- `theo-doi.csv` – sổ theo dõi mọi video đã đăng (view 24 giờ/7 ngày, CTR, so với đối thủ).

## Lệnh hay dùng (chạy trong `pipeline/`)

```bash
uv run pytest -q
PYTHONUTF8=1 uv run python scripts/dong-bo-view.py
uv run python -m tttc.giam_sat ../videos/<slug> --ctr 3.2
uv run python -m tttc.giam_sat luat   # luật ngưỡng tuyệt đối trên sổ (docs/quy-tac-quyet-dinh.md)
```

`dong-bo-view.py` chạy tự động 21:30 mỗi ngày bằng Task Scheduler (lịch "Nhip Cong Nghe - dong bo view" → `pipeline/scripts/dong-bo-hang-ngay.cmd`, máy tắt thì chạy bù khi bật lại; log ở `pipeline/dong-bo-view.log`). Phải chạy mỗi ngày vì cột `view_24h`/`view_7d` chỉ được điền trong cửa sổ 24–48 giờ và 7–8 ngày, lỡ là để trống. `giu_chan_30s` thì không có cửa sổ (Analytics truy vấn theo khoảng ngày).

## Môi trường (Windows)

- Lệnh `tttc.*` đọc tiếng Việt qua subprocess phải có `PYTHONUTF8=1` và `PYTHONIOENCODING=utf-8`.
- VieNeu chạy trong venv riêng `C:\Users\78\Documents\VieNeu-TTS\.venv`; lỗi DLL onnxruntime thì kiểm VC++ runtime trước. Không dùng `precision="int8"` (CPU không có VNNI).
- Token lưu trong keyring (`tui-tien-cong-nghe`): `youtube-token` (upload + force-ssl, `tttc.dang login`) và `analytics-token` (chỉ đọc Analytics, `tttc.dang login-analytics`). `dong-bo-view.py` dùng token Analytics để tự điền `giu_chan_30s` (7 ngày đầu, điền khi video đủ 9 ngày).
- Analytics API **không có CTR thumbnail** (400 "query is not supported"); CTR lấy từ Reporting API (`tttc.reach`, báo cáo `channel_reach_basic_a1`, cùng `analytics-token`). `dong-bo-view.py` tự tạo job lần đầu, điền `ctr` gộp 7 ngày đầu khi đủ 7 báo cáo ngày (ngày PST); dòng đã có CTR tay thì chỉ in số để đối chiếu. Cần bật "YouTube Reporting API" trong dự án Google Cloud.
- Git trên máy này chưa đặt `user.name`/`user.email`; các commit cũ ghi tác giả "Quang Tình".

## Quy ước

- Mọi số liệu trong kịch bản và tiêu đề phải có nguồn trong `nguon.json`; tiêu đề kiểm bằng `tieu_de.kiem_khop_nguon`.
- Code, comment, commit viết tiếng Việt; commit theo dạng `feat:` / `fix:` / `chore:`.
- Giới hạn đã biết ghi bằng comment `shortcut: <giới hạn>, <khi nào nâng cấp>`.
- Claude không nhập mật khẩu, không bấm xác nhận OAuth; việc trên YouTube Studio (Test & Compare, ghim bình luận, video liên quan) do người dùng làm.
