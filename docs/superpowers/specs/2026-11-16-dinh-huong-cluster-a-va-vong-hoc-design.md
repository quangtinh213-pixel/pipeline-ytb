# Thiết kế Hệ thống Đột phá Kênh (Cluster A + Sắc hóa Bao bì + Vòng học Tự động)

- **Ngày:** 2026-11-16
- **Trạng thái:** Đang kiểm tra (Builder Check)
- **Phạm vi:** Dự án cấp kênh (Project-level) — nâng cấp `pipeline/tttc/`, kỹ năng `.claude/skills/`, dữ liệu gốc và 2 video chờ phát sóng (`2026-11-16-meta-phat-anh-facebook`, `2026-11-16-starship-starlink-vn`).

---

## 1. Mục đích & Lý do (Intent & Why)

Kênh *Nhịp Công Nghệ* hiện có 7 người đăng ký sau 6 video dài đã công khai, với lượt xem giảm dần (`3.208 → 93 → 123 → 187 → 31 → 4`). Phân tích dữ liệu thực tế từ YouTube Data API, YouTube Analytics API và YouTube Reporting API (CSV ngày 11–13/11/2026) chỉ ra 3 nguyên nhân gốc rễ:

1. **Tắc nghẽn ở CTR (Bao bì):** Thuật toán vẫn cấp hàng nghìn lượt hiển thị cho các video sau (*Grab*: 3.713 hiển thị, *Lá thư Nvidia*: 3.187 hiển thị, *Jensen từ chức*: 801 hiển thị), nhưng CTR rơi xuống **1,48% – 2,79%**. Video duy nhất có CTR cao (**8,26%**, 7.855 hiển thị, 3.208 view) là `E17SceQLG9I` (*CEO Nvidia xin lỗi*) với mặt thật của Jensen Huang, độ tương phản mạnh và chủ đề sát luồng đề xuất lớn. Trong khi đó, giữ chân 30 giây đầu của video thứ 4 (`d1jh3GyOdrU` - *Một lá thư Nvidia*) đã đạt **83,7%** — chứng minh nội dung kịch bản đã giữ được người xem, nhưng bao bì chặn đứng phễu.
2. **Phân tán tệp người xem (Audience Cluster):** Kênh nhảy liên tục qua các chủ đề không cùng tệp khán giả (Nvidia → iPhone cũ → Grab → Microsoft → 7-Zip → Meta → Starlink), khiến thuật toán không gom được cụm người xem cố định trên trang chủ và cột Đề xuất (Suggested).
3. **Thiếu công cụ đo lường tự động sau khi đăng:** Chưa ghi lượt hiển thị (`hien_thi_7d`), khuôn thắng Test & Compare, chưa tự động khớp điểm rơi giữ chân với câu thoại trong phụ đề (`tttc.kham`), chưa quản lý chuỗi (`chuoi.json`), chưa theo dõi lịch sử thị trường đối thủ (`doi-thu.csv`) và chưa tự tổng hợp báo cáo tuần (`tttc.bao_cao`).

**Quyết định của người dùng (16/11/2026):**
- Thu hẹp hẳn phạm vi chủ đề vào **Cluster A ("Bàn cờ Đế chế AI & Bán dẫn × Túi tiền/Vị thế Việt Nam")** và sắc hóa bao bì để ép thuật toán nổ (breakout) 1–2 video lấy 1.000 sub đầu tiên.
- Xuất cả **Khuôn 2 (`ho-so` sắc hóa)** và **Khuôn 3 (`ban-co-toi` tràn viền)** (kèm `zoom` cận cảnh mặt nhân vật) trong mỗi bộ 3 ảnh của từng video để đưa vào **Test & Compare** trên YouTube Studio.
- Áp dụng ngay lập tức bộ 3 thumbnail mới cho cả 2 video đã dựng xong (`2026-11-16-meta-phat-anh-facebook` hẹn 15:30 ngày 16/11 và `2026-11-16-starship-starlink-vn`).
- Triển khai **Phương án B (Hệ thống Toàn diện)**: bao gồm cả nâng cấp bao bì, radar Cluster A + chuỗi, mở rộng sổ theo dõi, module khám nghiệm tự động (`tttc.kham`), báo cáo tuần (`tttc.bao_cao`) và sổ đối thủ (`doi-thu.csv`).

---

## 2. Mục tiêu, Phi mục tiêu & Chống mục tiêu (Goals, Non-Goals, Anti-Goals)

### 2.1 Mục tiêu (Goals)
- **G1 (Bao bì & A/B Testing):** Đạt CTR 7 ngày trung vị ≥ 5% (ngưỡng an toàn ≥ 4%) thông qua việc xuất bộ 3 thumbnail chuẩn Test & Compare (`ban-co-toi` tràn viền vs `ho-so` nền kem sắc hóa) có cắt phóng to (`zoom`) cận cảnh gương mặt nhân vật/chủ thể chính.
- **G2 (Khẩn cấp hôm nay):** Cập nhật xong bộ 3 thumbnail mới cho `2026-11-16-meta-phat-anh-facebook` (đẩy ảnh mặc định mới lên YouTube qua API trước 15:30 ngày 16/11) và `2026-11-16-starship-starlink-vn` (cập nhật trang duyệt 2 + biên nhận).
- **G3 (Khóa Cluster A & Chuỗi trong Radar):** Mọi đề video dài được chấm ưu tiên theo Cluster A, tự động gắn khuyến nghị định dạng (`dai-tang-1`, `dai-tang-2`, `shorts`, `bo`) và nối chuỗi qua `chuoi.json`.
- **G4 (Vòng học tự động):** Mở rộng `theo-doi.csv`, tự động tạo bản khám nghiệm giữ chân `videos/<slug>/kham-nghiem.md` (`tttc.kham`), theo dõi lịch sử view đối thủ trong `doi-thu.csv` và xuất báo cáo tuần `docs/bao-cao/<yyyy-ww>.md` (`tttc.bao_cao`).

### 2.2 Phi mục tiêu (Non-Goals)
- Không thay đổi engine dựng video (`tttc/dung.py`, `tttc/dao_dien.py`, `tttc/canh.py`), giọng đọc (`tttc/giong_vieneu.py`), hay cấu trúc Shorts dọc gốc vừa hoàn thành ngày 15/11.
- Không dựng lại tệp `final.mp4` hoặc `phu-de.srt` của 2 video `2026-11-16-meta-phat-anh-facebook` và `2026-11-16-starship-starlink-vn`.

### 2.3 Chống mục tiêu (Anti-Goals — điều làm dự án thất bại dù code chạy đúng)
- **Không quay lại giật tít kiểu kênh rác AI:** Không dùng "SỐC!", "CHẤN ĐỘNG!", chữ in hoa cả từ hay mặt người do AI vẽ giả ảnh thật. Sắc hóa bao bì bằng **con số thật có nguồn + gương mặt thật cận cảnh + câu hỏi xung đột quyền lực/túi tiền**.
- **Không để lệnh đồng bộ hằng ngày bị sập vì thiếu dữ liệu API:** Khi Analytics trễ 2–3 ngày hoặc Reporting API chưa đủ 7 ngày, `dong-bo-view.py`, `kham.py` và `bao_cao.py` phải ghi nhận nhẹ nhàng hoặc dùng dữ liệu hiện có, không tung ngoại lệ làm đứt tiến trình.

---

## 3. Ràng buộc (Constraints)

- **Môi trường:** Windows, Python chạy qua `uv run` trong thư mục `pipeline/`, bắt buộc `PYTHONUTF8=1` và `PYTHONIOENCODING=utf-8`.
- **Bản quyền & Nguồn:** Mọi con số trên thumbnail và tiêu đề phải khớp `nguon.json`. Ảnh nhân vật dùng cho thumbnail phải từ nguồn hợp lệ (Wikimedia Commons, ảnh cơ quan/hãng trong bài nguồn, hoặc khung hình từ video nguồn) và ghi công rõ ràng.
- **Tương thích ngược:** Toàn bộ bộ test hiện tại trong `pipeline/tests/` phải tiếp tục xanh (cập nhật các test bị đổi quy ước như `test_thumb.py`, `test_duyet.py`, `test_radar.py`, `test_theo_doi.py` và bổ sung test cho các hàm/module mới).
- **Quyền hạn YouTube API:** Không tự thao tác trình duyệt vào YouTube Studio (việc bật Test & Compare với 3 tệp `thumbnails/1.png, 2.png, 3.png`, ghim bình luận, gắn video liên quan trên Studio do người dùng bấm). API chỉ cập nhật thumbnail chính (`thumbnails().set`) và tiêu đề/mô tả/playlist.

---

## 4. Các phương án đã cân nhắc (Approaches)

1. **Phương án A ("Phẫu thuật Gọn & Đánh nhanh"):** Chỉ sửa `thumb.py`, `duyet.py`, `radar.py`, `theo_doi.py` và nâng cấp ngay 2 video hiện tại; bỏ qua việc viết các module hậu kiểm tự động (`kham`, `bao_cao`, `chuoi.json`, `doi-thu.csv`).
   - *Đánh đổi:* Nhanh nhưng thiếu hệ thống vòng học tự động về lâu dài.
2. **Phương án B ("Hệ thống Toàn diện" — Người dùng đã chọn):** Thực hiện toàn bộ phần cốt lõi của Phương án A (bao bì đôi `ban-co-toi` + `ho-so` sắc hóa, nâng cấp 2 video hôm nay, khóa Radar Cluster A) VÀ xây dựng đầy đủ hệ thống vòng học tự động (`theo-doi.csv` mở rộng, `tttc.kham`, `tttc.bao_cao`, `chuoi.json`, `doi-thu.csv`).
   - *Đánh đổi:* Khối lượng code lớn hơn (~6 module sửa/mới), cần chia thứ tự thực thi rõ ràng để xử lý xong 2 video trong ngày trước rồi mới lắp các module hậu kiểm.
3. **Phương án C ("Tối giản Thủ công"):** Không sửa code pipeline, chỉ chạy script rời bên ngoài để đè ảnh thumbnail.
   - *Đánh đổi:* Bị `duyet.py` chặn lỗi khuôn và phải làm tay lặp lại mỗi ngày.

---

## 5. Thiết kế chi tiết (Detailed Design)

### 5.1 Nâng cấp Thumbnail (`tttc/thumb.py`, `tttc/duyet.py`, skill `video-dung`)

#### A. Hằng số & Kiểm duyệt khuôn
- Trong `tttc/thumb.py`:
  - Giữ `KHUON = "ho-so"` làm hằng mặc định cho tương thích ngược, và thêm tập hợp `KHUON_HOP_LE = {"ho-so", "ban-co-toi"}`.
- Trong `tttc/duyet.py`:
  - Sửa kiểm tra ở `render_review_2`: một phương án hợp lệ khi `o.get("khuon") in thumb.KHUON_HOP_LE`. Nếu không thuộc tập này thì báo lỗi yêu cầu dựng bằng `thumb.ho_so` hoặc `thumb.ban_co_toi`.
  - Cảnh báo (không chặn lỗi) nếu cả 3 phương án trong `dong-goi.json` chỉ dùng 1 khuôn duy nhất mà thiếu sự kết hợp giữa `"ban-co-toi"` và `"ho-so"` để nhắc người dựng tận dụng Test & Compare (**đề xuất của builder**).

#### B. Cắt phóng to cận cảnh (`_crop_zoom`) trong `tttc/thumb.py`
- Thêm hàm nội bộ `_crop_zoom(img: Image.Image, tam: tuple[float, float], zoom: float = 1.0) -> Image.Image`:
  - Khi `zoom > 1.0`: cắt khung chữ nhật tỉ lệ gốc có kích thước `(w / zoom, h / zoom)` xoay quanh tâm `(w * tam[0], h * tam[1])` (kẹp trong biên `0..w, 0..h`) trước khi `ImageOps.fit`.
  - Giúp ảnh chụp toàn cảnh sự kiện (như ảnh Jensen Huang giữa đám đông sinh viên hoặc Elon Musk/Mark Zuckerberg ở hội nghị) phóng thẳng vào gương mặt nhân vật.

#### C. Sắc hóa hàm `thumb.ho_so(...)` (Khuôn 2 — Nền kem sắc hóa)
- Chữ ký hàm:
  ```python
  def ho_so(anh: Path, nhan: str, so: str, hoi: str, out: Path, ghi_cong: str = "",
            tam: tuple[float, float] = (0.5, 0.4), zoom: float = 1.0) -> tuple[Path, Path]:
  ```
  *(Tương thích ngược hoàn toàn với mọi lời gọi cũ không truyền `zoom`).*
- Cải tiến thị giác:
  - Giữ nền giấy kem kẻ dòng (`theme.TH["kem"]`), ảnh dán viền trắng xoay nhẹ `-3°` có băng keo và bóng đổ, nhân vật Nhịp ở góc dưới trái ảnh.
  - Thêm **thanh nhấn dọc màu đỏ (`sac.do[0]`) rộng 18 px** sát mép trái (`x = 0..18`).
  - Áp dụng `_crop_zoom` và tăng tương phản nhẹ (`ImageEnhance.Contrast(1.15)`) cho ảnh trong khung dán.
  - Thay vì chỉ kẻ gạch đỏ mảnh dưới chân con số `so`, vẽ **hộp tem đỏ bo góc (`radius=12`, màu `sac.do[0]`) bao trọn tầng `so` với chữ màu trắng (`#FFFFFF`)** để nổi bật ở kích thước `168×94 px`.

#### D. Thêm hàm `thumb.ban_co_toi(...)` (Khuôn 3 — Bàn cờ tối tràn viền)
- Chữ ký hàm:
  ```python
  def ban_co_toi(anh: Path, nhan: str, so: str, hoi: str, out: Path, ghi_cong: str = "",
                 tam: tuple[float, float] = (0.5, 0.35), zoom: float = 1.0) -> tuple[Path, Path]:
  ```
- Bố cục & Màu sắc:
  - Nền tối sâu `#08181C` (`theme.TH["nen"]`) kèm lưới tọa độ mảnh mờ (`rgba(34, 211, 238, 18)`, ô 48 px) ở nửa trái và quầng sáng đỏ mờ (`GaussianBlur(80)`) sau con số.
  - Thanh nhấn dọc màu đỏ (`#FF3B3B`, rộng 16 px) sát mép trái.
  - **Bên phải (rộng 720 px, từ `x=560` đến `1280`, cao `720 px`):** Ảnh nhân vật/sự kiện tràn viền (full-bleed), đã qua `_crop_zoom(tam, zoom)`, tăng tương phản `1.20×` và độ nét `1.25×`, hòa trộn sang nền tối bên trái bằng mặt nạ gradient ngang rộng 220 px (kèm làm tối nhẹ 90 px đáy ảnh để không chói badge thời lượng).
  - **Bên trái (3 tầng chữ):**
    1. `nhan` (nếu có): Chữ màu `#08181C` nằm trong nhãn pill bo góc màu xanh ngọc lam `#22D3EE` (`theme.TH["nhan"][0]`).
    2. `so` (bắt buộc): Chữ trắng `#FFFFFF` viền đen dày (`stroke_width=6`), đặt trên dải băng chéo nhẹ màu đỏ `#DC2626`.
    3. `hoi` (bắt buộc): Chữ vàng sáng `#FACC15` (`theme.TH["pill"]["vang"][0]`) viền đen dày (`stroke_width=8`).
  - `ghi_cong`: Đặt ở góc dưới trái `(x=54, y=H-34)`, chữ xám sáng `#B4C8CE` viền đen mảnh để luôn đọc được mà không đụng badge thời lượng góc dưới phải.
  - Lưu cả bản gốc `out` (`1280×720`) và bản thu nhỏ `-168px` (`168×94`).

---

### 5.2 Nâng cấp ngay 2 video hiện tại (`meta-phat-anh-facebook` & `starship-starlink-vn`)

1. **`videos/2026-11-16-meta-phat-anh-facebook` (đã upload hẹn giờ 15:30 ngày 16/11, video_id `Gsvyy5eGh70`):**
   - Tìm & tải 1 ảnh chân dung thật của Mark Zuckerberg từ Wikimedia Commons (ghi công chuẩn vào `anh/ghi-cong.json` và tham số `ghi_cong`).
   - Dựng lại 3 thumbnail:
     - `thumbnails/1.png`: Khuôn `ban-co-toi` (ảnh Mark Zuckerberg zoom cận mặt, chữ `["META BỊ PHẠT", "805 TRIỆU EURO", "CẦN TẮT GÌ?"]`).
     - `thumbnails/2.png`: Khuôn `ho-so` sắc hóa (cùng ảnh Mark Zuckerberg zoom cận mặt, chữ `["META BỊ PHẠT", "805 TRIỆU EURO", "VIỆT NAM PHẠT?"]`).
     - `thumbnails/3.png`: Khuôn `ban-co-toi` (ảnh Mark Zuckerberg + chữ `["79 TRIỆU NGƯỜI", "805 TRIỆU EURO", "TẮT NÚT NÀO?"]`).
   - Cập nhật `dong-goi.json` (khớp `"khuon"` và `"chu_thumb"`), tạo lại `duyet-2.html`, cập nhật `ban_duyet` trong `trang-thai.json` và dùng `tttc.dang` / `tttc.giam_sat.doi_bao_bi` đẩy thumbnail mới lên YouTube cho video `Gsvyy5eGh70` ngay lập tức (trước 15:30).
2. **`videos/2026-11-16-starship-starlink-vn` (đã qua duyệt 2, chưa upload):**
   - Dựng lại 3 thumbnail bằng bộ khuôn mới:
     - `thumbnails/1.png`: Khuôn `ban-co-toi` (ảnh `thumbnails/khung-bat-tau.png` phóng vào khoảnh khắc tháp bắt tàu Starship, chữ `["STARLINK CHÀO", "566 NGHÌN", "RẺ CHƯA?"]`).
     - `thumbnails/2.png`: Khuôn `ho-so` sắc hóa (cùng chữ `["STARLINK CHÀO", "566 NGHÌN", "RẺ CHƯA?"]`, ảnh lễ bàn giao thiết bị Starlink của Bộ KH&CN).
     - `thumbnails/3.png`: Khuôn `ban-co-toi` (ảnh ông Nguyễn Thành Chung / lễ bàn giao zoom cận cảnh, chữ `["CÁP QUANG 195K", "STARLINK 566K", "AI NÊN MUA?"]`).
   - Cập nhật `dong-goi.json`, render lại `duyet-2.html` và cập nhật biên nhận `duyet-2` trong `trang-thai.json` (giữ `chon = 1`) để sẵn sàng chạy `/video-dang`.

---

### 5.3 Khóa Radar vào Cluster A & Quản lý Chuỗi (`tttc/radar.py`, `chuoi.json`, `tttc/dang.py`)

#### A. Bộ lọc & Chấm điểm Cluster A trong `tttc/radar.py`
- Định nghĩa danh sách thực thể cốt lõi Cluster A (`THUC_THE_CLUSTER_A`):
  `["nvidia", "jensen huang", "tsmc", "apple", "openai", "sam altman", "microsoft", "google", "meta", "elon musk", "spacex", "starlink", "starship", "deepseek", "huawei", "byd", "intel", "amd", "qualcomm", "asml", "bán dẫn", "chip", "ai", "trung tâm dữ liệu", "thuế quan", "trừng phạt"]`.
- Bổ sung hàm `khuyen_nghi_dinh_dang(de: dict) -> str`:
  - Đầu vào `de` có thể chứa: `soc` (0–2), `so_lon` (0–2), `goc_vn` (0–2), `cluster_a` (bool, tự nhận diện qua tiêu đề hoặc truyền vào), `tre_gio` (số giờ kể từ tin gốc, mặc định 0), `tran_nhu_cau` (view cao nhất trên thị trường nếu có, mặc định None), `ho_da_dang` (bool), `chenh_gio_ho` (số giờ mình trễ hơn họ, mặc định 0).
  - Quy tắc trả về:
    - Nếu `diem < 4`: trả `"bo"`.
    - Nếu `tre_gio > 48` hoặc (`tran_nhu_cau is not None and tran_nhu_cau < 10000`) hoặc `not cluster_a`: trả `"shorts"` (tin tiêu dùng nội địa lẻ hoặc tin nhỏ chuyển hết sang Shorts).
    - Nếu `ho_da_dang` và `chenh_gio_ho >= 2.0`: trả `"dai-tang-2"` (bắt buộc làm góc tầng thứ hai: số liệu ngày 2, hồ sơ gốc, bảng tính Việt Nam).
    - Còn lại: trả `"dai-tang-1"`.
- Hàm `xep_hang`: giữ nguyên tương thích với các test hiện tại (`soc + so_lon + 2 * goc_vn`), đồng thời nếu mục đề có trường `cluster_a=True` hoặc nối chuỗi đang nóng (`chuoi_nong=True`) thì được ưu tiên xếp trên khi bằng điểm.
- Hàm `ghi_chu_de`: ghi thêm dòng `- Định dạng khuyến nghị: <dạng>` (và `- Chuỗi: <mã chuỗi>` nếu khớp chuỗi trong `chuoi.json`) khi dữ liệu đề có các trường này (giữ tương thích ngược nếu đề truyền vào chỉ có các trường cũ).

#### B. Quản lý chuỗi (`chuoi.json` ở thư mục gốc & `tttc/chuoi.py` hoặc trong `tttc/radar.py`)
- Tạo tệp `c:\Projects\Youtube\chuoi.json` lưu danh sách các chuỗi chủ đề Cluster A đang mở:
  ```json
  {
    "chuoi": [
      {
        "ma": "nvidia-de-che-ai",
        "ten": "Đế chế Nvidia & Cuộc chiến Chip AI",
        "playlist_id": "PLf9v4rPuuCys",
        "tu_khoa": ["nvidia", "jensen huang", "megaspeed", "h100", "blackwell", "chip ai"],
        "tap": [
          {"slug": "2026-11-11-nvidia-ceo-gian-diep", "video_id": "E17SceQLG9I", "ngay": "2026-11-09"},
          {"slug": "2026-11-15-nvidia-siet-chip", "video_id": "d1jh3GyOdrU", "ngay": "2026-11-12"},
          {"slug": "2026-11-13-huang-roi-nvidia", "video_id": "RX21zw1F8S0", "ngay": "2026-11-13"}
        ],
        "goi_y_tap_ke": [
          "Báo cáo tài chính quý Nvidia 17/11: doanh thu thực tế sau khủng hoảng",
          "Phiên điều trần Hạ viện Mỹ 18/11 về đường đi chip AI qua Singapore"
        ]
      },
      {
        "ma": "spacex-starlink-vn",
        "ten": "SpaceX, Starlink & Hạ tầng Viễn thông Việt Nam",
        "playlist_id": "PLf9v4rPuuCys",
        "tu_khoa": ["starlink", "spacex", "starship", "elon musk", "vệ tinh"],
        "tap": [
          {"slug": "2026-11-16-starship-starlink-vn", "video_id": null, "ngay": "2026-11-16"}
        ],
        "goi_y_tap_ke": [
          "Sau mốc 01/12/2026: Giá Starlink tại Việt Nam thay đổi ra sao so với cáp quang?"
        ]
      }
    ]
  }
  ```
- Hàm hỗ trợ trong `tttc/radar.py` (`khop_chuoi(text, chuoi_path)`): kiểm tra xem một chủ đề có thuộc chuỗi nào đang mở (tập cuối ≤ 14 ngày) không để gợi ý nối tập.
- Trong `tttc/dang.py`: khi upload video dài có trường `"chuoi"` trong `dong-goi.json` (hoặc khớp `chuoi.json`), tự động nối link "👉 Xem tập trước trong chuỗi: https://youtu.be/<id>" vào mô tả nếu chưa có, và cập nhật `video_id` vào `chuoi.json`.

---

### 5.4 Mở rộng Sổ theo dõi & Đồng bộ (`tttc/theo_doi.py`, `pipeline/scripts/dong-bo-view.py`)

- Mở rộng `theo_doi.EXTRA` thêm các cột phục vụ vòng học:
  ```python
  EXTRA = [
      "trung_de_ho", "chenh_gio", "radar_hang", "view_ho_24h",
      "avd_pct", "con_50pct", "o_lai_short", "khuon_short",
      "hien_thi_7d", "khuon_thumb", "goc", "chuoi", "roi_lon_nhat"
  ]
  ```
- Trong `pipeline/scripts/dong-bo-view.py`:
  - **`cap_nhat_ctr`**:
    - Hiện tại chỉ ghi `ctr` khi đủ cả 7 ngày báo cáo PST, khiến giai đoạn đầu kênh không nhìn thấy số trong sổ.
    - Cải tiến: Khi đã có từ **1 đến 6 ngày** báo cáo trong cửa sổ 7 ngày đầu, in ra log số hiển thị + CTR tạm tính để người vận hành biết ngay; khi đủ 7 ngày (hoặc khi gọi hàm trợ giúp điền hiển thị) thì ghi chính thức `ctr` và `hien_thi_7d` (tổng lượt hiển thị thumbnail) vào `theo-doi.csv`. Đặc biệt, nếu `hien_thi_7d` còn trống mà đã có báo cáo trong 7 ngày đầu, cập nhật tổng lượt hiển thị đã ghi nhận được (nếu đủ 7 ngày thì khóa số; chưa đủ 7 ngày thì vẫn điền `hien_thi_7d` tạm tính hoặc điền khi đủ 7 ngày — **quyết định kỹ thuật: để nhất quán với `ctr`, `cap_nhat_ctr` điền `hien_thi_7d` cùng lúc với `ctr` khi đủ 7 ngày, VÀ in bảng hiển thị/CTR tạm tính của các video chưa đủ 7 ngày ra màn hình mỗi tối**).
  - Tự động gọi `kham.dong_bo_kham(rows, thoi_luong, an, now)` (mục 5.5) để sinh `kham-nghiem.md` và điền cột `roi_lon_nhat` (ví dụ `"0:19 -11.0pt"`) vào `theo-doi.csv`.
  - Tự động gọi `radar.dong_bo_doi_thu()` (mục 5.6) để cập nhật `doi-thu.csv`.

---

### 5.5 Module Khám nghiệm Tự động (`tttc/kham.py`)

Tự động hóa việc tìm điểm rơi người xem mà trước đây phải làm tay:
- **Dữ liệu đầu vào:**
  - Đường cong 100 điểm `(elapsedVideoTimeRatio, audienceWatchRatio, relativeRetentionPerformance)` từ YouTube Analytics API.
  - Thời lượng video `thoi_luong` (giây).
  - Phụ đề `videos/<slug>/phu-de.srt` (để tìm câu thoại tại giây bị rơi) và `videos/<slug>/canh.json` (để tìm `id` cảnh và `mau` cảnh tại giây đó).
- **Các hàm chính trong `tttc/kham.py`:**
  1. `tim_cu_roi(pts: list[tuple[float, float]], thoi_luong: float, nguong_diem: float = 5.0) -> list[dict]`:
     - Nhận danh sách `(ratio_0_to_1, watch_ratio_0_to_1)`.
     - Bỏ qua vùng `ratio <= 0.02` (2% đầu tiên luôn biến động do bộ đếm).
     - Tìm mọi bước nhảy liên tiếp mà `(w_truoc - w_sau) * 100 >= nguong_diem`.
     - Trả về danh sách sắp xếp từ rơi nặng nhất xuống nhẹ nhất: `[{"giay": float, "mmss": str, "roi_diem": float, "con_lai_pct": float}]`.
  2. `khop_boi_canh(video_dir: Path, giay: float) -> dict`:
     - Đọc `phu-de.srt` (nếu có) lấy câu thoại chứa `giay` (hoặc gần `giay` nhất trong ±5s).
     - Đọc `canh.json` (nếu có) lấy cảnh có `start <= giay <= end` (trả về `id`, `mau`, `loi`).
  3. `tao_kham_nghiem(video_dir: Path, pts: list[tuple[float, float]], thoi_luong: float, ctr: str = "", hien_thi: str = "") -> Path`:
     - Tính tỉ lệ còn xem ở giây 30 (`giu_30s`), ở 50% thời lượng (`con_50`), và danh sách cú rơi.
     - Ghi tệp `videos/<slug>/kham-nghiem.md` gồm:
       - So sánh với mục tiêu (Giây 30 ≥ 75%, 50% thời lượng ≥ 35%, CTR ≥ 5%).
       - Bảng 5 cú rơi mạnh nhất kèm đúng câu đang nói trong `phu-de.srt` và mẫu cảnh đang chiếu trong `canh.json`.
       - Gợi ý tự động: nếu cú rơi nằm trong 40s đầu và câu thoại chứa cụm từ meta/nhiều câu hỏi thì chỉ rõ để thêm vào danh sách rút kinh nghiệm.
  4. CLI: `uv run python -m tttc.kham ../videos/<slug> [--som]`
     - Có cờ `--som`: truy vấn Analytics từ ngày đăng đến hôm nay (không cần chờ đủ 9 ngày) để khám nghiệm ngay các video đã có đường giữ chân trên Analytics (như 4 video đầu của kênh).

---

### 5.6 Theo dõi Thị trường Đối thủ (`doi-thu.csv` & cập nhật `tttc/radar.py`)

- Trong `pipeline/config.json`: giữ `"doi_thu": {"ten": "@MotCongNghe", "kenh_id": "UC91zSg_iPgJZZL6KB91BewQ"}` và thêm danh sách `" danh_sach_doi_thu"` (mặc định chứa `@MotCongNghe`, có thể thêm kênh khác mà không làm gãy code cũ đọc `config["doi_thu"]["kenh_id"]`).
- Tệp `c:\Projects\Youtube\doi-thu.csv`:
  - Các cột: `kenh,video_id,tieu_de,gio_dang,view_24h,view_7d,view_moi_nhat,nhom_de,breakout`.
  - Hàm `radar.cap_nhat_so_doi_thu(path, rss_items, now)`:
    - Mỗi lần chạy `dong-bo-view.py`, ghi các video mới từ RSS đối thủ vào `doi-thu.csv`, cập nhật `view_moi_nhat`, điền `view_24h` / `view_7d` nếu nằm trong cửa sổ (hoặc dùng `view_moi_nhat` để tính `breakout = view_moi_nhat / trung_vi_kenh`).
    - Tự động gắn nhãn `nhom_de` sơ bộ bằng từ khóa (`"cluster-a"` nếu khớp `THUC_THE_CLUSTER_A`, `"tieu-dung"` nếu khớp giá/mua bán nội địa, `"khac"` cho phần còn lại).

---

### 5.7 Báo cáo Tuần Tự động (`tttc/bao_cao.py`)

- Sinh báo cáo `docs/bao-cao/<yyyy-Www>.md` (chạy bằng `uv run python -m tttc.bao_cao [--tuan 2026-W46]` hoặc gọi cuối `dong-bo-view.py` vào tối Chủ nhật):
  1. **Bảng tổng hợp tách riêng Video dài vs Shorts:** số lượng đăng, trung vị `view_24h`, `view_7d`, `ctr`, `giu_chan_30s`, `con_50pct`, `avd_pct` (ghi rõ `n = ...`).
  2. **So sánh hiệu quả theo Nhóm / Khuôn:**
     - Khuôn thumbnail (`ban-co-toi` vs `ho-so`).
     - Góc tiếp cận (`tang-1` vs `tang-2`, trong chuỗi vs rời rạc).
  3. **Bức tranh Đối thủ tuần qua (từ `doi-thu.csv`):** Top 5 video breakout cao nhất của đối thủ và tỷ lệ nhóm đề `cluster-a`.
  4. **Danh sách Luật quyết định đã kích hoạt** (`giam_sat.luat_so`) và **Danh sách việc thủ công cần làm trên YouTube Studio** (bật Test & Compare cho video mới, gắn Related Video cho Shorts mới, ghim bình luận chuỗi).

---

## 6. Phần để người thực thi quyết định (Left to Builder)

- Chi tiết tọa độ pixel tinh chỉnh, độ mờ bóng đổ trong `thumb.ban_co_toi` và `thumb.ho_so` (miễn khớp đúng thiết kế ảnh mẫu đã được người dùng duyệt).
- Cấu trúc hàm nội bộ trong `tttc/kham.py` và `tttc/bao_cao.py`.
- Lựa chọn bức ảnh Wikimedia Commons cụ thể của Mark Zuckerberg cho bài `2026-11-16-meta-phat-anh-facebook` (miễn là ảnh thật, rõ mặt, giấy phép tự do CC/Public Domain, ghi công đầy đủ).
