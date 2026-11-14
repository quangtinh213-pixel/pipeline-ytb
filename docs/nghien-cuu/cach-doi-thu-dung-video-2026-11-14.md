# Nghiên cứu thực chứng cách đối thủ (`@MotCongNghe`) dựng video & đối chiếu 1-1 với kênh `Nhịp Công Nghệ`

- **Ngày thực hiện:** 14/11/2026
- **Đối thủ phân tích:** `@MotCongNghe` (`UC91zSg_iPgJZZL6KB91BewQ`)
- **Mẫu đối chiếu (5 video):**
  1. **Video nổ view của đối thủ (`s7l1zBV10GM`):** *"Bong bóng AI chính thức nổ? Chip Mỹ sập 12% một ngày, giá RAM, laptop có giảm theo?"* (đăng 06/11)
  2. **Cặp đối đầu 1 — Chủ đề CEO Nvidia từ chức (13/11):**
     - Đối thủ: `siGdK7U9ea4` (*"Sốc! Jensen Huang chính thức rời ghế CEO Nvidia: lời hứa với Việt Nam còn không?"*)
     - Kênh mình: `RX21zw1F8S0` (*"SỐC: Ông chủ Nvidia bất ngờ từ chức! Lời hứa biến Việt Nam thành cứ điểm AI có tan thành mây khói?"*)
  3. **Cặp đối đầu 2 — Chủ đề Microsoft 365 / Outlook sập toàn cầu (14/11):**
     - Đối thủ: `0wDK-sZVtj0` (*"Microsoft 365 sập toàn cầu hơn 13 tiếng: vì sao sửa mãi chưa xong, người đi làm Việt Nam mất gì?"*)
     - Kênh mình: `gg4P35JfyXk` / bản dựng local `videos/2026-11-14-microsoft-sap-toan-cau/final.mp4` (*"Sự thật vụ Microsoft nâng cấp mạng: Tự tay làm sập 18 giờ, người dùng Việt Nam chịu trận!"*)
- **Phương pháp & giới hạn đo đạc:** Tải video gốc 720p, metadata `.info.json`, phụ đề `.vi.vtt` qua `yt-dlp`; đo cắt cảnh qua `ffmpeg` (`gt(scene,0.22)` cho chuyển cảnh lớn và `gt(scene,0.10)` cho bồi phần tử/chuyển động nhỏ), đo âm thanh bằng bộ lọc `ebur128`, `volumedetect` và `silencedetect` (sweep `-28 dB` tới `-45 dB`); trích 15 khung 0–30s (`hook30s_*.jpg`), 24 khung toàn bài (`overview_*.jpg`) và 15 khung HD mẫu (`samples_*/`) để kiểm đếm trực tiếp. Lưu ý: các kết luận về âm thanh/nhạc nền dựa trên số đo sóng âm `ffmpeg` và thẻ `[âm nhạc]`/`>>` trong phụ đề chứ không nghe thủ công từng giây bằng tai. Thư mục `docs/nghien-cuu/khung-hinh/` nằm trong `.gitignore`.

---

## Tóm tắt phát hiện cốt lõi (Executive Summary)

1. **Nghịch lý "ảnh thật 45%" so với thực tế đối thủ:** Quy định ngày 10/11 trong `pipeline/tttc/chat_luong.py` đang ép `doi_that_min = 0.45` (`>= 45%` B-roll/ảnh thật) và khóa trần `do_hoa_max = 0.40` (`<= 40%` đồ họa). Trong thực tế, cả 3 video gần nhất của `@MotCongNghe` vẫn dùng **87,5% – 91,7% đồ họa, sa bàn isometric, biểu đồ và sơ đồ kỹ thuật thiết kế riêng**, **0% B-roll stock Pexels chung chung**, **4,2% (1 khung/video) ảnh báo chí đúng sự kiện thực tế**, và **4,2% – 8,3% ảnh bằng chứng cắt phóng đại có viền khoanh + tóm tắt**. Kênh mình khi cố nhồi `>= 45%` B-roll stock đã phải dùng tới cả clip Pexels tối om hoặc lệch ngữ cảnh (như clip kẹt xe ban ngày, bát phở) khiến video trông như tin tổng hợp stock thay vì phong cách phân tích sa bàn đặc trưng.
2. **Bí mật nhịp cắt — 30 giây đầu nhanh như nhau, phần thân "Bồi dần" trên một sân khấu:** Đối thủ có tốc độ cắt cảnh lớn (`scene=0.22`) chậm gấp đôi kênh mình (**10,54–11,46s/đoạn** vs **5,21–5,38s/đoạn**; tỉ lệ đoạn `> 8s` chiếm **45,9%–53,1%** so với trần **3%** trong `chat_luong.py`), nhưng **30 giây đầu họ cắt rất nhanh** (**3,28–4,30s/đoạn**, trong khi bản Microsoft của mình là **6,01s/đoạn** và Nvidia là **4,70s/đoạn**). Sang phần thân, thay vì đổi hẳn sang B-roll mới mỗi 3,5 giây, đối thủ giữ một sân khấu isometric 20–50 giây rồi **bồi dần phần tử/nhãn chữ mới mỗi ~2 giây** (`scenes_010`), giúp mắt vừa có neo không gian để hiểu sâu vừa liên tục có kích thích thị giác mới.
3. **Không phụ đề karaoke đáy màn hình — Giữ đáy màn hình sạch cho bằng chứng & nhãn tóm tắt:** 100% khung hình của `@MotCongNghe` **không có phụ đề chạy chữ ở đáy**. Toàn bộ chữ trên màn hình là **nhãn pill định danh** (nền vàng `#FACC15` chữ đen, nền trắng viền đen, nền đỏ cảnh báo) hoặc **thanh tóm tắt 1 câu** dưới ảnh bằng chứng. Kênh mình bật phụ đề karaoke đáy màn hình khiến nhiều cảnh bị **đè chữ 2 lớp** (nhãn `b-roll` phía dưới đụng phụ đề) hoặc **linh vật Nhịp góc phải dưới chạm/lẫn vào cụm chữ**.
4. **Hố sâu âm thanh lớn nhất nằm ở file nhạc nền & quãng ngắt TTS (`-17,3 LUFS` vs `-14,2 LUFS`):** Đối thủ giữ chuẩn YouTube **`-14,2 LUFS`** đồng đều trên cả 3 video và gần như **không có khoảng lặng chết tiếng** (`0,6–1,9` lần/phút dưới `-35 dB` ở `d=0.15s`; chỉ **0,1%** thời lượng xuống dưới `-45 dB`) vì luôn duy trì lớp nhạc nền quanh mức `-30..-33 dB`. Ngược lại, hai video kênh mình nhỏ hơn **3,0–3,1 LUFS** (`-17,2` đến `-17,3 LUFS`) và có tới **23,5 / 20,5 khoảng lặng/phút ngay cả dưới `-45 dB`** (**12,3% và 11,0% thời lượng rơi xuống gần như tắt tiếng**). Nguyên nhân trực tiếp từ mã nguồn: tệp `pipeline/am-thanh/nhac/ambient-tech.mp3` chỉ dài **10,00 giây** và vốn đã có **`mean_volume = -44,4 dB`** (`-45,7 LUFS`), sau đó `pipeline/tttc/tron_am.py` lại giảm thêm **`-12 dB`** (`ha_db + 8` khi `ha_db = -20.0`) đẩy nhạc xuống **`~ -56,4 dB`** rồi sidechain duck với `release = 600ms` (dài hơn cả quãng nghỉ `0,25s`/`0,5s` của `giong_vieneu.py`), làm nhạc nền biến mất hoàn toàn.
5. **Bất lợi kép về độ sâu phân tích & giờ đăng ("Đẻ chậm hơn 2–4,5 tiếng nhưng bài lại ngắn hơn 2–4,5 lần"):** Cặp Nvidia mình đăng chậm hơn **2 giờ 15 phút** (`19:15` vs `17:00`) với thời lượng **9p14s** so với **18p43s** của đối thủ (`70.476` vs `27` view). Cặp Microsoft mình đăng chậm hơn **4 giờ 30 phút** (`15:30` vs `11:00`) với thời lượng **2p21s (556 từ)** so với **10p43s (2.566 từ)** của đối thủ — tức vừa chậm tin hơn vừa thiếu toàn bộ phần giải thích cơ chế cốt lõi (*Load Balancer*, *Health Check*, *Retry Storm*, *Azure Front Door*, *SLA 99,9%*, số liệu *Downdetector* VN vs Mỹ).

---

## Mục 1 — Tổng quan 5 video & Bối cảnh đối đầu

| Tiêu chí | `s7l1zBV10GM` (Đối thủ · AI Bubble) | `siGdK7U9ea4` (Đối thủ · Nvidia) | `RX21zw1F8S0` (Kênh mình · Nvidia) | `0wDK-sZVtj0` (Đối thủ · Microsoft) | `gg4P35JfyXk` (Kênh mình · Microsoft) |
|---|---|---|---|---|---|
| **Kênh** | Mọt Công Nghệ | Mọt Công Nghệ | Nhịp Công Nghệ | Mọt Công Nghệ | Nhịp Công Nghệ |
| **Giờ đăng (VN)** | 06/11 20:05:10 | 13/11 17:00:02 | 13/11 19:15:28 (**+2h15p**) | 14/11 11:00:23 | 14/11 15:30:23 (**+4h30p**) |
| **Thời lượng** | 11p34s (`693,56s`) | 18p43s (`1123,38s`) | 9p14s (`554,35s`) | 10p43s (`643,19s`) | 2p21s (`140,77s`) |
| **Tổng số từ (transcript)** | 2.494 từ | 4.457 từ | 2.166 từ | 2.566 từ | 556 từ |
| **Số chương (Chapters)** | 6 chương | 7 chương (Mở + Phần 1..6) | 6 chương | 6 chương (Mở + Phần 1..5) | 5 chương |
| **Lượt xem / Thích / BL** *(tại lúc thu thập 14/11)* | 276.797 / 1.251 / 135 | 70.476 / 511 / 93 | 27 / — / — | 5.671 / 54 / 8 | 0 *(mới đăng 15:30)* / — / — |
| **Độ phân giải / Bitrate** | 1280×720 / 442,0 kbps | 1280×720 / 412,9 kbps | 1280×720 / 624,6 kbps | 1280×720 / 370,4 kbps | 1920×1080 / 6.252,7 kbps |

### Cấu trúc chương & Chiến lược độ sâu nội dung
- **Cấu trúc bất biến của `@MotCongNghe` (luôn 6–7 chương, 10,7–18,7 phút):**
  1. **Chương 1 (0–66s hoặc 0–78s):** Mở móc trực diện + neo góc độ **Việt Nam** ngay từ tiêu đề chương 1 (*"thanh RAM ở Việt Nam"*, *"câu hỏi về lời hứa với Việt Nam"*, *"Outlook quay vòng cả buổi sáng"*).
  2. **Các phần giữa (Phần 1 -> Phần 3/4):** Dựng lại trình tự thời gian + **giải thích cơ chế bản chất bằng ví dụ đời thường hoặc tiền lệ lịch sử**. Ví dụ: với AI bubble là **ví dụ lò gạch** ký hợp đồng trước 1 năm & lịch sử dot-com 2000; với Nvidia là **bàn tròn 60 bếp trưởng**, **cơ chế cổ phiếu loại B của Meta**, **tiền lệ CEO Intel 2018 & nhà máy Foxconn Wisconsin 10 tỷ đô**; với Microsoft là **cơ chế Load Balancer như trạm thu phí không kịp bật đèn xanh**, **khái niệm `Retries are 'selfish'` (AWS Builders' Library)** và **tính nhẩm 99,9% SLA = 43 phút/tháng**.
  3. **Phần áp chót:** Bảng đối chiếu **"Việt Nam & túi tiền người dùng / đã hứa – đã làm – còn trên bàn"** (số liệu xuất khẩu Samsung VN 57,1 tỷ USD, bảng 3 cột lời hứa Nvidia, báo giá khách hàng ở TP HCM & lập trình viên ở Huế trong Dân Việt/VnExpress).
  4. **Chương cuối:** Bài học hành động cụ thể (**checklist 5 việc nhỏ làm ngay hôm nay** ở `0wDK-sZVtj0`) và câu hỏi mở đúng đối tượng để kéo bình luận.
- **Kênh mình:** Cặp Nvidia (`RX21zw1F8S0`) bám khá sát khung chương dài (`554s`, 6 chương), nhưng vẫn thiếu tầng dẫn chứng lịch sử & phản biện báo chí đa chiều (WSJ, NYT, Bloomberg, Elon Musk trên X, tiền lệ Intel/Foxconn). Riêng video Microsoft (`gg4P35JfyXk`) lại rẽ sang cấu trúc **clip ngắn 140s** (do cơ chế `Loại:` ngắn trong `.claude/skills/video-moi/SKILL.md`), khiến video đăng **sau đối thủ 4,5 tiếng** nhưng **lượng thông tin chỉ bằng 1/5 đối thủ**.

### Công thức Thumbnail & Tiêu đề
- **`@MotCongNghe` giữ 100% tính nhất quán thương hiệu (nhận diện trong 0,5 giây trên feed):**
  - Viền cam bo góc bao quanh khung hình.
  - Đường **tia sét vàng gãy khúc** chia đôi màn hình (trái là nhân vật chính / mặt người thật có biểu cảm mạnh; phải là bối cảnh Việt Nam / sản phẩm hỏng / bong bóng nổ), hoặc ảnh cận cảnh điện thoại lỗi Outlook full màn hình (`0wDK-sZVtj0`).
  - **2 khối hộp vàng `#FACC15` chữ in hoa đen đậm** đặt lệch góc dưới trái (`BONG BÓNG AI / CHÍNH THỨC PHÁT NỔ?`, `JENSEN RỜI GHẾ CEO / LỜI HỨA VỚI VIỆT NAM THÌ SAO?`, `OUTLOOK SẬP HƠN 13 TIẾNG / DÂN VĂN PHÒNG ĐỨNG HÌNH`).
  - Góc trên phải luôn ghi nguồn ảnh công khai (`Ảnh: VGP...`, `Ảnh: Bảo Lâm, VnExpress...`).
- **Kênh mình:** Thumbnail `RX21zw1F8S0` mô phỏng rất tốt bố cục chia đôi tia sét + 2 khối hộp vàng (`JENSEN ĐI RỒI / AI CẦM LÁI?`), tuy nhiên nửa phải lại đặt tòa nhà isometric xanh đen kèm pill chữ nhỏ `NGƯỜI CŨ, KHÔNG LẠ` thay vì một hình ảnh gây tò mò cảm xúc (như ảnh Jensen bắt tay Thủ tướng VN ở đối thủ). Sang `gg4P35JfyXk` (`thumbnails/3.png`), thumbnail lại **đổi hẳn sang phong cách tối minimalist chữ trắng/đỏ phát sáng + thẻ trích dẫn nghiêng chữ nhỏ**, đánh mất hoàn toàn chuỗi nhận diện thương hiệu và khó đọc hơn trên màn hình điện thoại nhỏ.

---

## Mục 2 — Giải phẫu 30 giây đầu (Hook) 1-1

### Bảng nhịp 30 giây đầu qua các mốc cắt `hook30s_*.jpg`

1. **Video nổ 277N view (`s7l1zBV10GM` — Bong bóng AI):**
   - `00–05s`: Ảnh tòa nhà Nasdaq + 2 mặt đồng hồ đối chiếu múi giờ **`16:00 NEW YORK 05/11` = `04:00 VIỆT NAM 06/11`**.
   - `06–14s`: Lưới 30 ô chip biến đỏ + nền sọc cam **con số khổng lồ `-12,25%`** + chốt vàng **`30/30 MÃ GIẢM`**.
   - `15–20s`: Sa bàn kim tự tháp tiền xanh lá (`NVIDIA VỐN HOÁ THEO CNBC`) bật số vàng **`~450 TỶ USD`**.
   - `21–29s`: 3 chip `DRAM` (`MICRON -17,46%` riêng thẻ đen + ảnh Seoul `MẤY TIẾNG SAU` + tòa nhà `SEOUL · KOSPI` thẻ đỏ **`TẠM DỪNG GIAO DỊCH`** -> **`KÉO SÀN XUỐNG MẠNH NHẤT`**).
   - **Đặc điểm:** **9 cú cắt (`3,28s/đoạn`)**, cứ 3 giây lại có **một cú nhảy cấp độ thiệt hại** (Mỹ -> Nvidia -> Micron -> Hàn Quốc ngắt cầu dao), rồi giây 31 bất ngờ xen **giọng phụ thứ hai** (`>> Thế thì RAM sắp rẻ rồi`) dẫn thẳng về giá thanh RAM **7,49 triệu** tại CellphoneS ở giây 41!

2. **Đối đầu 1 — Nvidia từ chức (`siGdK7U9ea4` vs `RX21zw1F8S0`):**

| Mốc giây | Đối thủ (`siGdK7U9ea4` — **7 cắt / 3,98s**) | Kênh mình (`RX21zw1F8S0` — **7 cắt / 4,70s**) |
|---|---|---|
| **00–04s** | Chân dung Jensen Huang + lịch **12 THÁNG 11** + pill `BUỔI SÁNG GIỜ MỸ` | Chữ số lớn **`27 năm`** trên nền tối + linh vật Nhịp góc phải -> ảnh Jensen bị đám đông vây |
| **05–12s** | Sa bàn trụ sở Nvidia giữa biển xanh + thẻ `THÔNG BÁO RẤT NGẮN` + avatar Jensen + sa bàn `GHẾ TRỐNG` (`CEO · 33 NĂM`, `RỜI CẢ HĐQT`, `HIỆU LỰC NGAY`) | Ảnh trụ sở Nvidia (`TRỤ SỞ NVIDIA, SANTA CLARA`) -> **nguyên trang web `nvidia.com` chữ li ti không đọc được (`09–12s`)** |
| **13–18s** | Ảnh chụp báo cáo **8-K SEC có vạch đỏ khoanh đúng dòng từ chức** + thanh tóm tắt đen đáy màn hình -> phong bì `LÁ THƯ XIN LỖI 08/11` (`VẪN LÀ JENSEN`) | Ảnh bảng hiệu `NVIDIA 2800 & 2806` + pill cyan `Rời cả hội đồng` -> vòng tròn chữ **`0 ngày`** |
| **19–29s** | Sa bàn **ghế trống** trượt thanh thời gian `1993 — 33 NĂM — 2026` + tem `TẠM QUYỀN` -> đồng hồ `CHƯA TỚI 1 NGÀY` -> tờ `NEW YORK TIMES` bay tới trụ sở + pill **`MỐI QUAN HỆ THỨ HAI`** | Chữ **`5 ngày`** -> ảnh phố Wall có flag xanh (`PHỐ WALL CHỜ BÁO CÁO QUÝ`) -> B-roll Pexels phòng họp trống + pill `Ai nắm quyền?` -> B-roll chip AI Pexels |

- **Khác biệt quyết định:** Ở giây 09–12, kênh mình chiếu nguyên ảnh chụp toàn trang thông cáo `nvidia.com` dày đặc chữ tiếng Anh không phóng to dòng trọng tâm, trong khi đối thủ dùng **1 cảnh chụp 8-K có khung viền đỏ + tóm tắt 1 dòng tiếng Việt lớn bên dưới**. Ngoài ra ngay từ giây 15–29, đối thủ đã gài xong **3 điểm móc tò mò lớn**: *(1)* Mới ngày 08/11 còn ký thư *"vẫn là Jensen"*, *(2)* Ghế CEO là *tạm quyền*, *(3)* *Mối quan hệ thứ hai* là vụ gì mà New York Times khui ngay đêm 11/11?

3. **Đối đầu 2 — Microsoft sập toàn cầu (`0wDK-sZVtj0` vs `gg4P35JfyXk`):**

| Mốc giây | Đối thủ (`0wDK-sZVtj0` — **7 cắt / 4,30s**) | Kênh mình (`gg4P35JfyXk` — **4 cắt / 6,01s**) |
|---|---|---|
| **00–09s** | Đồng hồ kim (`ĐÊM THỨ NĂM · 12/11`) -> đồng hồ điện tử `≈ 01:00 GIỜ VIỆT NAM` -> 2 ô đỏ `OUTLOOK (!)` + `LỊCH TEAMS (!)` -> quả địa cầu `VIỆT NAM / NHẬT / ÚC` (`TRỤC TRẶC TRÊN DIỆN RỘNG`) | Chữ **`gần 18 giờ`** (`Outlook gần như tê liệt, theo Kentik`) -> **B-roll Pexels sợi cáp tối om (`05–07s`)** với pill `Không phải hacker, AI` -> **B-roll Pexels switch tối (`09–11s`)** với pill `Nâng cấp mạng` |
| **10–17s** | **Ảnh thật của Bảo Lâm (VnExpress 13/11)** màn hình điện thoại báo lỗi `outlook.office.com/mail/` + bong bóng `OUTLOOK VẪN CHƯA VÀO ĐƯỢC Ở VIỆT NAM` -> sa bàn laptop đỏ **`HẾT THỜI GIAN CHỜ`** | Vẫn giữ nền switch (`11s`) -> **thẻ trích báo giấy kem `VNEXPRESS` (`13–15s`)** -> **Chen hẳn bumper logo kênh `NHỊP CÔNG NGHỆ` ngay ở giây 17–19!** |
| **18–30s** | Sa bàn **TP HỒ CHÍ MINH (`NHÂN VIÊN KINH DOANH`)** -> thẻ trích `"TÔI CẦN GỬI BÁO GIÁ..."` + đơn `BÁO GIÁ 10:00` quay vòng hóa đỏ -> sa bàn **`LẬP TRÌNH VIÊN · HUẾ` gọi Teams `KHÁCH NƯỚC NGOÀI`** | Giữ bumper kênh tới giây 19 -> **Thẻ chia chương xanh gắt `PHẦN 1: Chuyện gì đã xảy ra?` (`20–21s`)** -> B-roll tủ server Pexels (`23–25s`) -> vòng tròn `71%` đếm lên `85%` (`27–29s`) |

- **Khác biệt quyết định (sai lầm chí mạng ở `gg4P35JfyXk`):** Trong 30 giây đầu quyết định người xem ở lại hay bỏ đi, kênh mình lại **cắt chỉ 4 lần (`6,01s/đoạn`)** và **tự chặn đà câu chuyện bằng 4 giây bumper thương hiệu + thẻ Chương 1 ở ngay giây 17–21**, cộng thêm 6 giây đầu là B-roll cáp mạng tối om không có chứng cứ thị giác! Trong khi đó, đúng 30 giây đầu của đối thủ đã kể xong một **bộ phim ngắn đủ 3 cảnh gần gũi với dân văn phòng Việt Nam**: 1 giờ sáng bùng lỗi -> 11:29 trưa VN vẫn màn hình trắng `outlook.office.com` -> sale ở TP.HCM trễ báo giá, lập trình viên ở Huế rớt cuộc họp Teams với khách Tây.

---

## Mục 3 — Nhịp cắt, Cấu trúc cảnh & Kỹ thuật "Bồi dần" (*Progressive Layering*)

### Bảng số liệu nhịp cắt (`scenes_022` = đổi cảnh lớn; `scenes_010` = bồi thêm chi tiết/nhãn)

| Video | Thời lượng | `cuts@0.22` (`cắt/phút`) | TB đoạn `0.22` (`median`, `max`) | **0–30s `0.22`** (`số cắt` / `TB`) | `>60s` TB (`0.22`) | `% đoạn > 8s` (`0.22`) | `cuts@0.10` (`cắt/phút`) | TB đoạn `0.10` | **0–30s `0.10`** (`số cắt` / `TB`) |
|---|---|---|---|---|---|---|---|---|---|
| **`s7l1zBV10GM`** (Đối thủ · AI Bubble) | 693,56s | 63 (`5,45/p`) | **10,84s** (`7,33s`, `47,2s`) | **9 cuts / 3,28s** | 12,07s | **46,9%** | 97 (`8,39/p`) | 7,08s | 11 cuts / **2,73s** |
| **`siGdK7U9ea4`** (Đối thủ · Nvidia) | 1123,38s | 97 (`5,18/p`) | **11,46s** (`8,52s`, `54,13s`) | **7 cuts / 3,98s** | 12,70s | **53,1%** | 144 (`7,69/p`) | 7,75s | 7 cuts / **3,98s** |
| **`0wDK-sZVtj0`** (Đối thủ · Microsoft) | 643,19s | 60 (`5,60/p`) | **10,54s** (`7,47s`, `62,46s`) | **7 cuts / 4,30s** | 12,83s | **45,9%** | 80 (`7,46/p`) | 7,94s | 9 cuts / **3,28s** |
| **`RX21zw1F8S0`** (Mình · Nvidia) | 554,35s | 102 (`11,04/p`) | **5,38s** (`4,23s`, `18,5s`) | 7 cuts / **4,70s** | 5,55s | 16,5% | 144 (`15,59/p`) | 3,82s | 8 cuts / 4,18s |
| **`gg4P35JfyXk`** (Mình · Microsoft) | 140,77s | 26 (`11,08/p`) | **5,21s** (`3,73s`, `14,54s`) | **4 cuts / 6,01s** | 4,70s | 18,5% | 37 (`15,77/p`) | 3,70s | 7 cuts / 3,76s |
| *Ngưỡng `pipeline/tttc/chat_luong.py` hiện tại* | — | *~13–21/p* | **`2,8 – 4,5s`** | **`max_tb = 3,5s`** | — | **`<= 3%`** | — | — | — |

### Giải mã hai tốc độ trái ngược của `@MotCongNghe`
Nhìn qua bảng số liệu, nếu chỉ nhìn tổng thể dễ tưởng đối thủ dựng "chậm" hơn mình gấp đôi (`10,5–11,5s` vs `5,2–5,4s`). Thực tế cho thấy **hai chế độ nhịp hoàn toàn có chủ đích**:
1. **Chế độ Hook 0–30s (Cắt gắt hơn cả phần thân của mình):** Ở 30s đầu, đối thủ cắt **2,73–3,98s/đoạn** (`scenes_010`), đạt đúng ngưỡng `<= 3,5–4,0s` mà `chat_luong.py:kiem_30s_dau(max_tb=3.5)` nhắm tới. Kênh mình lại vi phạm ngược đúng ngay 30s đầu: `RX21zw1F8S0` là **4,70s** (`0.22`) / **4,18s** (`0.10`), còn `gg4P35JfyXk` chậm tới **6,01s** (`0.22`).
2. **Chế độ Phân tích sau 60s (Sân khấu neo dài + Bồi dần phần tử):** Sau phút thứ 1, đối thủ cố tình kéo trung bình chuyển cảnh lớn lên **12,07–12,83s** (có cảnh giữ tới **47–62 giây**, ví dụ cảnh 3 hộp carton ở `03:28–04:51` trong `s7l1zBV10GM`, cảnh sa bàn bàn tròn 60 bếp trưởng ở `07:06–07:51` và bảng 3 cột Việt Nam ở `13:06` trong `siGdK7U9ea4`, cảnh Load Balancer trạm thu phí `02:47–03:38` trong `0wDK-sZVtj0`).
   - Lý do `cuts@0.10` cao hơn `cuts@0.22` khoảng **+33% đến +54%** (`97 vs 63`, `144 vs 97`, `80 vs 60`) là vì cứ **2–4 giây một lần khi giọng đọc nhắc tới từ khóa mới**, trên cùng sân khấu isometric đó lại có thêm **1 thẻ nhãn / 1 dấu tem đỏ / 1 đường kẻ mũi tên / 1 tờ báo cáo** bay ra.
   - Trong `pipeline/tttc/dung.py`, việc ép dùng hiệu ứng `iris` trên `so-lon`/`phan-tram` và `dip` định kỳ mỗi 3 cảnh kết hợp các nhát cắt đổi cảnh toàn phần mỗi 3–4 giây khiến não người xem kênh mình liên tục phải "giải mã lại không gian mới" (từ phòng máy -> đường phố -> bát phở -> trang web nhỏ -> tòa nhà), làm tăng mệt mỏi nhận thức mà không giúp nhớ luận điểm.

---

## Mục 4 — Ngôn ngữ hình ảnh, Bố cục, Nhân vật & Trình bày bằng chứng

### Thống kê phân loại trên 120 khung `overview_*.jpg` (24 khung/video)

| Nhóm khung hình | `s7l1zBV10GM` (ĐT · AI) | `siGdK7U9ea4` (ĐT · Nvidia) | `0wDK-sZVtj0` (ĐT · MS) | **Trung bình Đối thủ (72 khung)** | `RX21zw1F8S0` (Mình · Nvidia) | `gg4P35JfyXk` (Mình · MS) |
|---|---|---|---|---|---|---|
| **Đồ họa / Sa bàn Isometric / Biểu đồ / Checklist thiết kế riêng** | **21/24 (87,5%)** | **22/24 (91,7%)** | **21/24 (87,5%)** | **64/72 (88,9%)** | 7/24 (29,2%) *(gồm thẻ chương)* | 7/24 (29,2%) *(+1 wipe frame)* |
| **Ảnh báo chí thật đúng sự kiện** *(có nguồn + ngày)* | 1/24 (4,2%) | 1/24 (4,2%) | 1/24 (4,2%) | **3/72 (4,2%)** | 0/24 *(trừ phần hook đầu)* | 0/24 (0%) |
| **Bằng chứng khoanh vùng phóng đại / Quote có dịch** | 2/24 (8,3%) | 1/24 (4,2%) | 2/24 (8,3%) | **5/72 (6,9%)** | 6/24 (25,0%) *(5 full-page nhỏ + 1 quote)* | **6/24 (25,0%)** *(6 thẻ `trich-bao` lặp mẫu)* |
| **B-roll stock (Pexels / chung chung)** | **0/24 (0%)** | **0/24 (0%)** | **0/24 (0%)** | **0/72 (0%)** | **10/24 (41,7%)** | **10/24 (41,7%)** *(thực tế 50% khi tính cả cảnh kẹt giữa)* |

> **Phát hiện mâu thuẫn trực tiếp với `pipeline/tttc/chat_luong.py` và `.claude/skills/video-dung/SKILL.md`:**
> Bộ kiểm chất lượng hiện hành quy định `"do_hoa_max": 0.40` (`<= 40%`), `"doi_that_min": 0.45` (`>= 45%`), `"bang_chung": (0.08, 0.35)`. Tuy nhiên, số liệu đếm trên 72 khung của đối thủ chứng minh **họ hoàn toàn không trộn 45% stock B-roll vào thân bài**. Họ đạt yếu tố "đời thật" bằng **đúng 1–2 tấm ảnh báo chí chuẩn xác về thời điểm/nhân vật/hiện trường tại Việt Nam** (Samsung Thái Nguyên trong `s7l1zBV10GM`, Jensen Huang gặp Thủ tướng Phạm Minh Chính trong `siGdK7U9ea4`, ảnh điện thoại vào Outlook lỗi của VnExpress trong `0wDK-sZVtj0`), cộng thêm vài đoạn bằng chứng khoanh vùng cực nét; phần còn lại (~89%) là **sa bàn isometric kể chuyện trên nền màu chuyển theo chương**.

### 4 điểm khác biệt lớn về thiết kế thị giác & bằng chứng

1. **Quản lý nền & bảng màu theo chương (Color-coded Chapters) thay vì một tông tối duy nhất:**
   - Quan sát 3 bảng `overview` của `@MotCongNghe`: họ **không khóa chết nền xanh đen `#090F13` toàn video**. Họ đổi tông nền mượt mà theo vai trò từng chương để báo hiệu chuyển trục nội dung mà không cần slide "PHẦN 2" cắt ngang:
     - Hook / Sự cố / Thiệt hại: nền tối sâu navy/đen hoặc đỏ sẫm.
     - Giải thích cơ chế / Quỹ / Phân tích: nền **vàng kem ấm**, **xám bạc nhạt** hoặc **xanh rêu sẫm** (trong `0wDK-sZVtj0` toàn bộ phần kỹ thuật Load Balancer/Azure Front Door dùng nền xanh rêu đậm cực dịu mắt, giúp nhân vật/máy chủ nổi khối).
     - Góc Việt Nam / Chuỗi cung ứng / Tương lai: nền **xanh lá ngọc nhạt** hoặc **xanh nước biển isometric**.
     - So sánh chuyên gia / Checklist cuối bài (`10:04` ở `0wDK-sZVtj0`, `10:51` ở `s7l1zBV10GM`): nền **vàng kem sáng**.
   - Kênh mình giữ nền `#0B1115` / ảnh stock tối đồng nhất suốt video (trong `gg4P35JfyXk` các khung `00:08`, `00:53`, `01:49`, `02:01` chữ đặt trên nền stock tối rất chìm), ngoại trừ 1 slide chương xanh cyan chói đột ngột (`00:19`) và các thẻ `trich-bao` giấy kem lặp đi lặp lại **6 lần giống hệt nhau** trong 2 phút.

2. **Quy tắc "0% phụ đề karaoke đáy màn hình" vs Chữ thông tin nổi khối:**
   - `@MotCongNghe`: **Tuyệt đối không chạy phụ đề lời đọc ở dưới.** Thay vào đó, mỗi khái niệm/nhân vật quan trọng được gắn **thẻ pill có viền mỏng, góc bo tròn, tương phản mạnh**:
     - Nhãn nhấn mạnh / cảnh báo: nền vàng `#FACC15` chữ đen (`CHƯA TỚI 1 NGÀY`, `TRỤC TRẶC TRÊN DIỆN RỘNG`), nền đỏ chữ trắng (`TẠM DỪNG GIAO DỊCH`, `HẾT THỜI GIAN CHỜ`, `KHÔNG THỂ TRUY CẬP`).
     - Nhãn định danh thực thể: nền trắng viền đen chữ đậm (`LOAD BALANCER · BỘ CHIA TẢI`, `NHÂN VIÊN KINH DOANH`), đặt **ngay cạnh vật thể kèm đường kẻ chỉ**.
     - Thanh tóm tắt bên dưới ảnh chụp báo/web: nền đen đặc chữ trắng to, rõ nguồn ở góc phải/trái đáy cỡ nhỏ (`Cục Thống kê, 03/11 · tính tới 31/10`).
   - Kênh mình: `dung.py` (dòng 626–631) phủ `phu-de` (`bottom: 36px; font-size: 44px`) chạy liên tục suốt video. Kết quả quan sát trên `samples_RX21zw1F8S0`:
     - Ở `s15_08m52s.jpg`: thanh caption dưới của `b-roll` (`NGHE LỜI HỨA TRƯỚC GIỚI PHÂN TÍCH`) bị dính sát ngay trên phụ đề `hứa ấy ra sao trước giới phân tích`.
     - Ở `s14_08m17s.jpg` và `hook30s_RX21zw1F8S0.jpg` (`27s`): **linh vật Nhịp ở góc phải dưới** đặt chệch đè sát cụm phụ đề hoặc nhãn chữ dưới (`KHÔNG CÓ ÔNG ĐỨNG ĐÓ`).
     - Ở `hook30s_gg4P35JfyXk.jpg` (`15s`): phụ đề che mất một phần chân giấy `trich-bao`.

3. **Cách trình bày bằng chứng: "Cắt zoom vào đúng 1 con số/1 câu + Thanh dịch tóm tắt" vs "Chụp nguyên trang `trang-nguon`":**
   - Trong `s7l1zBV10GM` (`s04_00m41s.jpg`), để chứng minh giá thanh RAM trên CellphoneS tăng lên 7,49 triệu, họ **cắt phóng to vừa khít khu vực giá bán**, đóng khung viền đỏ nền vàng quanh số **`7.490.000đ`**, rồi đặt một thanh giải thích đen to ở dưới: `CellphoneS, 06/11/2026: RAM laptop Kingston DDR5 16 GB ghi giá 7.490.000đ...`.
   - Trong `siGdK7U9ea4` (`hook30s` `13s`, `overview` `06:21`), khi dẫn hồ sơ SEC 8-K hay tweet trả lời của Elon Musk (`"That would be an honor"`), họ **khoanh đỏ câu khóa** hoặc giữ đúng 2 thẻ bình luận lớn rồi **đặt thanh dịch tiếng Việt trực tiếp phía dưới**.
   - Ngược lại, trong `RX21zw1F8S0` (`overview` `00:11`, `02:46`, `03:08`, `06:50`, `07:12`), 5 trên 24 khung mẫu dùng `trang-nguon` chụp gần như nguyên chiều rộng trang web `nvidia.com` với cỡ chữ cực nhỏ — trên màn hình điện thoại gần như không thể đọc được chữ nào bên trong.

4. **Cách sử dụng nhân vật (`Mọt` vs `Nhịp`):**
   - Nhân vật **`Mọt`** của đối thủ **không đóng vai watermark đứng góc vô cảm trong mọi cảnh**. `Mọt` chỉ xuất hiện ở các thời điểm có chức năng dẫn chuyện rõ ràng:
     - **Recap tập trước / ngữ cảnh nền (`01:07` ở `siGdK7U9ea4`, `01:09` ở `s7l1zBV10GM`):** Ngồi sau bàn có logo `MỌT`, tay chỉ lên màn hình tivi chứa thumbnail tập cũ (`"CHUYỆN BÀ ALICE HUANG"` hoặc câu hỏi trước cú sập), biến intro thành không gian studio có chiều sâu.
     - **Các pha đối thoại phản biện với giọng phụ (`02:32`, `05:46` ở `s7l1zBV10GM`; `05:37`, `06:21`, `07:51` ở `siGdK7U9ea4`):** `Mọt` xuất hiện kèm bóng nói (speech bubble) minh họa chính câu hỏi ngơ ngác/phản ứng của người xem (*"Xì hơi với nổ thì khác gì nhau?"*, *"Nghe mà = 3 LẦN"*).
   - Nhân vật **`Nhịp`** của kênh mình hiện chỉ bật sticker nhỏ tĩnh/lắc nhẹ ở góc phải dưới màn hình, không gắn với thoại hay bóng nói nên đôi lúc gây thừa hoặc chạm vào UI ở đáy khung hình.

---

## Mục 5 — Âm thanh, Giọng đọc, Giọng phụ đối thoại & Nhạc nền / SFX

### Bảng đo sóng âm khách quan bằng `ffmpeg` (`ebur128` + sweep `silencedetect`, `d=0.15s`)

| Video | Loudness (`LUFS`) | LRA (`LU`) | True Peak (`dBFS`) | WPM toàn bài / 60s đầu | Khoảng lặng `@-28 dB` | Khoảng lặng `@-32 dB` | Khoảng lặng `@-35 dB` | Khoảng lặng `@-40 dB` | Khoảng lặng **`@-45 dB`** *(chết tiếng)* |
|---|---|---|---|---|---|---|---|---|---|
| **`s7l1zBV10GM`** (ĐT) | **-14,2** | 2,6 | -3,5 | 215,8 / 211 | 12,4/p (`4,7%`) | 2,1/p (`0,8%`) | 0,6/p (`0,3%`) | 0,3/p (`0,2%`) | **0,3/p (`0,1%`, 0,8s)** |
| **`siGdK7U9ea4`** (ĐT) | **-14,2** | 2,1 | -3,2 | 238,0 / 245 | 17,1/p (`6,6%`) | 6,2/p (`2,2%`) | 1,9/p (`0,7%`) | 0,4/p (`0,2%`) | **0,2/p (`0,1%`, 0,8s)** |
| **`0wDK-sZVtj0`** (ĐT) | **-14,2** | 2,0 | -3,4 | 239,4 / 241 | 9,3/p (`3,6%`) | 1,6/p (`0,7%`) | 0,7/p (`0,4%`) | 0,5/p (`0,2%`) | **0,3/p (`0,1%`, 0,8s)** |
| **`RX21zw1F8S0`** (Mình) | **-17,3** | 1,9 | -1,0 | 234,4 / 237 | 28,4/p (`16,8%`) | 27,3/p (`15,8%`) | 27,1/p (`15,4%`) | 26,2/p (`14,4%`) | **23,5/p (`12,3%`, 68,3s)** |
| **`gg4P35JfyXk`** (Mình) | **-17,2** | 2,3 | -1,9 | 237,0 / 224 | 29,0/p (`16,6%`) | 27,7/p (`15,5%`) | 26,4/p (`14,7%`) | 24,7/p (`13,4%`) | **20,5/p (`11,0%`, 15,5s)** |

*(Lưu ý: với tham số mặc định `d=0.18s` trong `metrics.json`, mức `-35 dB` của kênh mình là `24,7/p` = `14,7%` ở `RX21zw1F8S0` và `21,7/p` = `13,4%` ở `gg4P35JfyXk`; của đối thủ chỉ là `0,4–1,1/p` = `0,2–0,5%`.)*

### 4 phát hiện kỹ thuật quan trọng về âm thanh

1. **Lỗi chuỗi trộn nhạc nền (`ambient-tech.mp3` + `tron_am.py`) làm mất hẳn lớp đệm âm thanh:**
   - Số liệu sweep chứng minh: ở ngưỡng `-28 dB`, đối thủ vẫn có `9,3–17,1` khoảng nghỉ ngữ khí/phút (`3,6%–6,6%`), nhưng từ `-32 dB` đến `-35 dB` số khoảng lặng tụt thẳng xuống gần 0. Điều này xác nhận đối thủ giữ **lớp nhạc nền liên tục ổn định quanh `-30..-33 dB`** (thấp hơn giọng đọc ~16–19 dB): đủ nhỏ để không át giọng, nhưng đủ dày để lấp mọi khe hở giữa câu.
   - Ở kênh mình, kiểm tra trực tiếp tệp nhạc nền `pipeline/am-thanh/nhac/ambient-tech.mp3` cho thấy:
     - Thời lượng tệp nhạc gốc chỉ dài **`10,00 giây`** (bị loop lặp đi lặp lại mỗi 10s, cứ đầu-cuối 10s lại hụt biên độ từ `-63 dB` lên `-45 dB`).
     - Âm lượng gốc của `ambient-tech.mp3` vốn đã ở mức **`mean_volume: -44,4 dB`**, `max_volume: -40,5 dB` (`-45,7 LUFS`).
     - Trong `pipeline/tttc/tron_am.py`, code dùng `ha_db: float = -20.0`, đặt `volume={ha_db + 8}dB` (**tức trừ thêm `-12 dB`**, kéo nhạc nền xuống **`~ -56,4 dB`**!), sau đó lại qua `sidechaincompress=threshold=0.003:ratio=6:attack=20:release=600:makeup=1`.
     - Vì `release=600ms` dài hơn cả quãng nghỉ giữa câu (`pause_cau = 0.25s`) và bằng đúng quãng nghỉ giữa đoạn (`pause_doan = 0.50s` trong `pipeline/tttc/giong_vieneu.py`), nhạc vừa không kịp hồi biên độ lúc nghỉ, vừa nằm dưới ngưỡng `-55 dB` (nhỏ hơn tiếng ồn phòng thu). Hệ quả là **20,5–23,5 lần mỗi phút** âm thanh toàn video rơi thẳng xuống dưới `-45 dB` (tổng 12,3% thời lượng tắt ngóm), gây cảm giác giọng TTS bị chặt khúc.

2. **Chênh lệch độ lớn tổng thể `-3,1 LUFS` & thiếu khâu chuẩn hóa đầu ra về `-14 LUFS`:**
   - Toàn bộ 3 video của đối thủ khóa chính xác ở **`-14,2 LUFS`** (`True Peak -3,2` đến `-3,5 dBFS`, giữ headroom an toàn cho codec YouTube).
   - Hai video kênh mình dừng ở **`-17,2 / -17,3 LUFS`** (`True Peak -1,0` đến `-1,9 dBFS` nhưng tích hợp toàn bài thấp hơn **3 dB** vì 13–15% thời lượng bị hẫng im lặng + không có pass `loudnorm` đạt `-14 LUFS` ở cuối `tron_am.py`). Khi người xem lướt từ video đối thủ sang video mình, video mình bị **nhỏ đi thấy rõ**.

3. **Thủ thuật "Giọng phụ phản biện" (`>> ...`) phá sự đơn điệu của TTS:**
   - So sánh tốc độ đọc thực tế: kênh mình (`234,4–237,0 WPM`) đã ngang ngửa đối thủ ở hai bài tin nóng gần đây (`238,0–239,4 WPM`), vượt xa tốc độ bài `s7l1zBV10GM` (`215,8 WPM`). Tức vấn đề không phải đọc chậm, mà là **độ đơn sắc một giọng suốt 9–18 phút**.
   - Trong cả 3 transcript của `@MotCongNghe`, đều đặn cứ **1–3 phút** họ chèn **1 câu đối thoại cực ngắn (4–9 từ) của một giọng đọc thứ hai** (thể hiện qua dấu phân tách đổi giọng `>>` trong auto-caption của YouTube) đứng vai người xem bình dân hỏi xoáy hoặc thốt lên:
     - `s7l1zBV10GM`: `>> Thế thì RAM sắp rẻ rồi.` · `>> Xì hơi với nổ thì khác gì nhau?` · `>> Mỗi nhà một lý do, loạn quá.` · `>> Giảm kiểu này thì cũng như không.` · `>> Vậy là cứ chờ khuyến mãi.`
     - `siGdK7U9ea4`: `>> Lại chuyện ông chủ ấy nữa à?` · `>> Cúp máy luôn, căng thật đấy.` · `>> Rồi sao nữa, kể tiếp đi.` · `>> Chú ấy là người lập công ty cơ mà.` · `>> Nghe mà chóng mặt quá đi.` · `>> Thôi đừng làm mình hồi hộp.`
     - `0wDK-sZVtj0`: `>> Cái đó là hệ thống gì mà nhạy thế?` · `>> Chỗ này nghe hơi rối rồi đấy.` · `>> Thử lại cũng có tội à?` · `>> Nói chuyện đó để làm gì bây giờ?` · `>> Đợi lâu vậy chắc mất hết thư rồi.`
   - Kỹ thuật này mang lại **3 lợi ích cùng lúc**: *(1)* reset lại ngưỡng chú ý thính giác mỗi 90 giây (retention hook); *(2)* hợp thức hóa việc giải thích khái niệm khó (*Load Balancer*, *Retry Storm*, *giá hợp đồng vs giá giao ngay*) mà không bị mang tiếng giảng đạo; *(3)* tạo điểm chốt tự nhiên cho bong bóng chat của nhân vật `Mọt` trên màn hình.

4. **Lệch biên độ trong kho `pipeline/am-thanh/sfx/`:**
   - Đo `volumedetect` trực tiếp các tệp SFX trong kho hiện tại cho thấy sự mất cân bằng rất lớn nếu `dung.py` chỉ nhân hệ số thô `0.18 – 0.35`:
     - `impact-bass-1.mp3`: `mean = -5,0 dB` (`max = -0,4 dB`) — cực lớn.
     - `whoosh-short.mp3` / `whoosh.mp3`: `mean = -19,1 dB` (`max = -2,1 dB`).
     - `pop.mp3`: `mean = -26,2 dB` (`max = -3,2 dB`).
     - `click-soft.mp3`: `mean = -30,7 dB` (`max = -5,4 dB`) — nếu nhân `0.18` (-15 dB) sẽ rơi xuống `-45,7 dB`, gần như không nghe thấy.
     - `chime.mp3`: `mean = -32,4 dB` (`max = -9,3 dB`).
   - Do đó các SFX nhỏ khi gán hệ số `0.18` bị chìm nghỉm, không tạo được cảm giác "tách – cạch – lướt" mỗi khi bồi phần tử trên màn hình.

---

## Mục 6 — Bảng đề xuất nâng cấp `pipeline/` (Theo thứ tự ưu tiên P0 / P1 / P2)

> **Lưu ý phạm vi:** Tài liệu này chỉ trình bày phương án và thông số đề xuất; **chưa chỉnh sửa** bất kỳ mã nguồn nào trong `pipeline/`.

| Ưu tiên | Hạng mục & Tệp tác động | Trạng thái / Thông số hiện tại | Đề xuất thay đổi cụ thể | Tác động kỳ vọng |
|---|---|---|---|---|
| **P0** | **Chuẩn hóa nhạc nền, sidechain & loudness đầu ra** (`pipeline/config.json`, `pipeline/am-thanh/nhac/`, `pipeline/tttc/tron_am.py`) | Nhạc `ambient-tech.mp3` chỉ dài `10s`, `mean = -44,4 dB`; `tron_am.py` giảm tiếp `-12 dB` (`ha_db + 8`, `ha_db=-20`) + `release=600ms`; đầu ra tổng `-17,2..-17,3 LUFS` | 1. Thay `ambient-tech.mp3` bằng 2–3 track **dài >= 120–180s** (YouTube Audio Library), chuẩn hóa trước nhạc nền về `-16 LUFS` trước khi đưa vào mixer (hoặc chạy `loudnorm` nhánh nhạc trong `tron_am.py`).<br>2. Đặt mức nhạc nền dưới giọng quanh **`-30` đến `-32 LUFS`** (giảm ~16–18 dB so với giọng `-14 LUFS`), chỉnh `sidechaincompress` nhẹ hơn (`ratio=3`, `attack=15`, `release=220ms`) để nhạc kịp hồi nhẹ ở quãng nghỉ.<br>3. Thêm pass chuẩn hóa tổng cuối **`loudnorm=I=-14:TP=-2.0:LRA=5`** đạt đúng `-14,2 LUFS` như đối thủ. | Xóa sạch **11–12,3% khoảng chết tiếng** (`<-45 dB`); tăng cảm giác mượt tai, sang và đồng đều âm lượng với feed YouTube (**+3,1 LUFS**). |
| **P0** | **Gỡ bỏ định mức `45% B-roll stock` & đổi quy tắc kiểm định** (`pipeline/tttc/chat_luong.py`, `.claude/skills/video-dung/SKILL.md`) | `chat_luong.py`: `doi_that_min = 0.45`, `do_hoa_max = 0.40`, `tb_giay = (2.8, 4.5)`, `tren_8_max = 0.03` | 1. Đảo tỉ lệ theo đúng thực chứng đối thủ: cho phép **`do_hoa_min >= 0.70`** (sa bàn isometric, sơ đồ, biểu đồ, checklist), giới hạn B-roll Pexels chung chung **`stock_max <= 0.10`**, tách mục **`anh_su_kien` (1–3 ảnh báo chí thật đúng sự kiện/Việt Nam có ghi nguồn + ngày)**. Bỏ bắt buộc lấp stock khi thiếu ảnh sự kiện.<br>2. Tách chuẩn nhịp làm 2 ngưỡng: **30s đầu `max_tb <= 3.5s` (bắt buộc cắt nhanh >= 7 lần)**; **sau 60s cho phép giữ sân khấu nền tới 15–35s miễn mật độ sự kiện/bồi phần tử đạt `>= 20–30 lần/phút` (`scenes_010`)**. | Chấm dứt tình trạng nhồi video Pexels tối om hoặc lạc quẻ (bát phở, kẹt xe) chỉ để qua cổng `chat_luong.py`; giữ nguyên sân khấu cho người xem tập trung hiểu cơ chế sâu. |
| **P0** | **Làm sạch 30 giây đầu — Cấm bumper kênh & thẻ chương quá sớm** (`pipeline/tttc/dung.py`, `.claude/skills/video-moi/SKILL.md`) | `gg4P35JfyXk` chen bumper logo `NHỊP CÔNG NGHỆ` ở giây 17–19 và thẻ `PHẦN 1` ở giây 20–21; `first_30s_avg_s = 6,01s` | 1. Cấm đặt bumper thương hiệu hoặc slide chia chương trong **45–60 giây đầu tiên** (giống đối thủ chuyển chương 1 -> 2 ở mốc `66s–78s`).<br>2. Trong 30s đầu, chỉ dùng: *(a)* số lớn/đồng hồ/bản đồ mở móc -> *(b)* **1 ảnh thật hiện trường/bằng chứng zoom rõ + tóm tắt 1 dòng** -> *(c)* sa bàn minh họa tình huống người Việt -> *(d)* **1 câu hỏi/giọng phụ gài móc** để chuyển sang thân bài.<br>3. Chỉ chọn chế độ **Video dài (8–15 phút / 2.000–3.500 từ)** cho tin sự kiện chính; chỉ dùng clip ngắn 2 phút cho bản tin phụ/Shorts để tránh thua thiệt đối đầu trực diện. | Giữ chân người xem vượt qua mốc rơi rụng 30s đầu và đủ độ sâu cạnh tranh sòng phẳng với video 10–18 phút của đối thủ. |
| **P1** | **Tắt phụ đề karaoke đáy & nâng cấp mẫu bằng chứng zoom + nhãn pill** (`pipeline/tttc/dung.py`, `pipeline/templates/canh/trang-nguon.html`, `trich-bao.html`, `b-roll.html`) | `phu-de` chạy kín đáy (`bottom: 36px`); `trang-nguon` chụp full-page chữ nhỏ; `trich-bao` lặp 1 mẫu giấy kem 6 lần | 1. Thêm tùy chọn/mặc định **tắt `phu-de` chạy đáy** cho video dài phong cách sa bàn; thay bằng **nhãn pill nổi trên cảnh** (vàng `#FACC15` chữ đen cho điểm chốt, đỏ `#DC2626` chữ trắng cho sự cố/cảnh báo, trắng viền đen chỉ tên thực thể kèm mũi tên) và **thanh tóm tắt nguồn 1 dòng** ở đáy.<br>2. Nâng cấp `trang-nguon.html`: hỗ trợ **tọa độ crop/zoom `2.5x–3.5x` vào đúng dòng/con số khóa + viền highlight đỏ/vàng**, kèm thanh dịch tiếng Việt đậm nét bên dưới.<br>3. Nâng cấp `trich-bao.html`: tách biến thể so sánh **2–3 thẻ trích song song** (avatar nguồn + tổ chức + tóm tắt 3–5 chữ) thay cho thẻ giấy kem lặp đơn điệu.<br>4. Giới hạn `Nhịp` ở các vị trí cao hơn hoặc thu gọn vùng an toàn `bottom >= 140px` không bao giờ chạm chữ đáy; chỉ hiện `Nhịp` khi có **bóng nói/tương tác hoặc intro recap**. | Triệt tiêu lỗi đè chữ 2 lớp, đọc rõ bằng chứng ngay trên màn hình điện thoại nhỏ, tăng tính thẩm mỹ và tính đa dạng thị giác. |
| **P1** | **Tối ưu quãng nghỉ TTS & thêm giọng phụ phản biện 2 người** (`pipeline/tttc/giong_vieneu.py`, `.claude/skills/video-moi/SKILL.md`, `pipeline/config.json`) | Chỉ 1 giọng `Quốc Tuấn`; `pause_cau = 0.25s`, `pause_doan = 0.50s` cứng nhắc | 1. Giảm quãng ngắt mặc định xuống **`pause_cau = 0.12–0.16s`**, **`pause_doan = 0.28–0.35s`** để lời đọc liền mạch, giữ nhịp hối thúc.<br>2. Khai báo **1 giọng phụ (`giong_phu` khác sắc thái/cao độ nhẹ, ví dụ giọng nữ hoặc nam trẻ tự nhiên hơn)** chuyên đọc các dòng đánh dấu `>> ...` (mỗi 90–150 giây chèn 1 câu hỏi ngắn 5–9 từ phản ánh tâm lý người xem). | Tạo nhịp đối thoại sống động mỗi ~2 phút, giữ retention vùng giữa video (phút 3–8) và làm điểm neo tự nhiên để bật bóng nói của `Nhịp`. |
| **P2** | **Sân khấu "Bồi dần" theo timestamp từ & cân bằng lại kho SFX + bảng màu theo chương** (`pipeline/templates/canh/`, `pipeline/tttc/dung.py`, `pipeline/am-thanh/sfx/`) | Một màu nền tối `#0B1115`; chuyển cảnh cứng mỗi ~4s dùng `iris`/`dip` đều đặn; SFX lệch biên độ từ `-5 dB` tới `-32 dB` | 1. Thiết kế bộ 4–5 **nền màu dịu theo vai trò chương** (Navy tối cho Hook, Kem ấm `#EFE6CF` cho Khái niệm/Bảng/Checklist, Xanh rêu tối cho Kỹ thuật, Xanh ngọc nhạt cho Việt Nam/Chuỗi cung ứng) áp dụng bằng biến CSS theme theo chương thay vì ép chung một nền đen.<br>2. Hỗ trợ trường `steps: [{at_word, show}]` trong `canh.json` để GSAP bật dần các nhãn/tem/thẻ mới trên cùng một cảnh SVG isometric khớp chính xác timestamp từ `giong-timing.json`, giảm lạm dụng hiệu ứng `iris`/`dip` cắt ngang mạch thị giác.<br>3. Chạy chuẩn hóa peak cho toàn bộ `pipeline/am-thanh/sfx/*.mp3` (ví dụ đồng nhất mức peak `-6 dBFS` trước khi vào mixer) để âm `click-soft` / `pop` không bị chìm ở gain `0.18–0.25`. | Đưa chất lượng hoàn thiện thị giác – thính giác tiệm cận trực tiếp mặt bằng video 70N–277N view của `@MotCongNghe`. |

---

## Phụ lục: Các tệp chứng cứ đã trích xuất (lưu tại `docs/nghien-cuu/khung-hinh/motcongnghe-2026-11-14/`)

- Bảng khung 30s đầu: `hook30s_s7l1zBV10GM.jpg`, `hook30s_siGdK7U9ea4.jpg`, `hook30s_RX21zw1F8S0.jpg`, `hook30s_0wDK-sZVtj0.jpg`, `hook30s_gg4P35JfyXk.jpg`
- Bảng 24 khung toàn bài: `overview_s7l1zBV10GM.jpg`, `overview_siGdK7U9ea4.jpg`, `overview_RX21zw1F8S0.jpg`, `overview_0wDK-sZVtj0.jpg`, `overview_gg4P35JfyXk.jpg`
- Ảnh HD mẫu 1280×720 / 1920×1080: các thư mục `samples_<id>/`
- Số liệu thô & kịch bản chạy đo: `metrics.json`, `cuts_*.json`, `transcript_*.txt`, `analyze_videos.py`
