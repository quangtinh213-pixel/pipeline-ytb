# Shorts dọc gốc: mỗi Short là một video riêng

- **Ngày:** 15/11/2026
- **Trạng thái:** bản thiết kế, chờ duyệt. Chưa sửa mã.
- **Căn cứ:** `docs/nghien-cuu/de-xuat-phat-trien-2026-11-15.md` mục 8.2, `theo-doi.csv`, số Studio người dùng dán ngày 15/11, rà `pipeline/tttc/dung.py` ngày 15/11.

Ghi chú đọc: câu nào ghi **(mình chọn)** là quyết định của người viết thiết kế, người dùng chưa xác nhận riêng. Phần còn lại là điều người dùng đã chọn hoặc số đo được.

## 1. Vì sao làm

Shorts của kênh được YouTube đưa lên feed (940 và 888 view) nhưng chỉ 9,6–18,9% người lướt tới ở lại xem. Các mốc người làm kênh hay dùng là 70% trở lên (số bên thứ ba, YouTube không công bố ngưỡng). Đăng thêm Shorts kiểu cũ chỉ nhân thêm số lần bị lướt qua.

Ba nguyên nhân tìm thấy trong mã và khung hình:

1. **Hình nhỏ.** Mọi mẫu cảnh vẽ cho 1920×1080; Short là sân khấu đó thu nhỏ 0,5625 đặt giữa khung dọc (`dung.py`, biến `stage_open`). Hình chỉ chiếm khoảng 1/3 chiều cao, còn lại là nền tối.
2. **Cắt giữa bài.** Short lấy nguyên một đoạn giọng và cảnh của video dài qua `scene_range`, nên câu đầu là câu giữa bài ("Thứ nhất,…").
3. **Hook không phải câu nói đầu.** `short_hook` chỉ là một băng chữ phía trên.

Người dùng đã chọn **cách A**: mỗi Short có kịch bản riêng, giọng đọc mới, và hình dựng bằng bộ mẫu cảnh dọc. Hai cách bị loại: chỉ dựng lại hình dọc trên giọng cũ (không sửa được câu đầu), và ghép hook mới với thân bài cũ (chỗ ghép lệch tông, không làm được Short độc lập).

## 2. Mục tiêu, ngoài phạm vi, điều phải tránh

**Mục tiêu**

- Tỉ lệ "ở lại xem" trung vị ≥ 40% sau 10 Shorts dựng kiểu mới. Ngưỡng này là giả định, chỉnh khi có số. Mốc so sánh: 9,6–18,9% của lứa cũ.
- Khung 0 của mọi Short đã đủ chữ lớn và con số, không cần chờ hiệu ứng.
- Câu nói đầu tiên là câu hook.
- Hình phủ kín khung 1080×1920.

**Ngoài phạm vi (không làm trong đợt này)**

- Nhân vật Nhịp và thanh chương trong Shorts.
- Radar tự đề xuất Short độc lập (mục 3.3 của bản đề xuất). Cấu trúc thư mục dưới đây không chặn việc đó, nhưng đợt này Short vẫn đi kèm một thư mục video.
- Lấy tỉ lệ "ở lại xem" bằng API. Trước mắt nhập tay từ Studio.
- Cầu nối Short → video dài (video liên quan, màn hình kết thúc). Làm sau khi tỉ lệ ở lại đã lên.
- Mọi thay đổi với cách dựng video ngang.

**Điều phải tránh**

- Short trông như bản tin tự động: tiêu đề và chữ hook không dùng từ giật gân, không "!" (theo luật `tieu_de` đã sửa 15/11).
- Số liệu không nguồn. Mọi số trong lời và trên hình của Short phải có `[#id]` trong `nguon.json` của thư mục video, như video dài.
- Tự duyệt. Luồng `duyet-short` giữ nguyên: người dùng xem từng Short rồi mới đăng.

## 3. Các cách đã cân nhắc

| Cách | Sửa hình nhỏ | Sửa câu đầu | Short độc lập | Chi phí |
|---|---|---|---|---|
| **A. Short là video riêng** (đã chọn) | có | có | có | 5 mẫu cảnh mới, thêm một lượt giọng 130–190 từ mỗi Short |
| B. Giữ giọng cũ, dựng lại hình dọc | có | không | không | 5 mẫu cảnh mới |
| C. Hook đọc mới ghép thân cũ | có | có | không | 5 mẫu cảnh mới, xử lý chỗ ghép giọng |
| Phóng to sân khấu ngang | một phần (cắt mất hai bên) | không | không | gần như không |

Chọn A vì chỉ A sửa trọn cả ba nguyên nhân và cho phép thử từng biến một trên Short.

## 4. Thiết kế

### 4.1 Thư mục của một Short

`.gitignore` đang bỏ qua cả `videos/*/shorts/` và `videos/*/short-[0-9]*/`, nên nguồn của Short đặt ở thư mục mới **(mình chọn)**:

```
videos/<slug>/ngan/<k>/
  kich-ban.md          # Loại: shorts, có [#id] trỏ vào nguon.json của thư mục cha
  canh.json            # "khuon": "doc", cảnh dùng mẫu dọc
  giong.mp3            # bỏ qua khỏi git
  giong-timing.json
  composition/         # bỏ qua khỏi git
  khung-0.png, khung-3.png   # khung giây 0 và giây 3 để người dùng xem khi duyệt
videos/<slug>/shorts/<k>.mp4   # tệp ra, đường dẫn như cũ để dang và dong-goi.json không đổi
```

`nguon.json`, `anh/`, `broll/`, `nguon/` dùng chung của thư mục cha, không chép. Thêm vào `.gitignore`: mp3, `giong-vieneu/`, `composition/`, png khung trong `videos/*/ngan/*/`.

### 4.2 Kịch bản Short

Viết riêng theo mục 7 của `docs/template-kich-ban.md`, 35–50 giây. Mỗi video dài có 2 Shorts, mỗi Short một góc tự đứng được (người chưa xem video dài vẫn hiểu).

Cấu trúc:

| Đoạn | Giây | Nội dung |
|---|---|---|
| Hook | 0–4 | Một câu nêu vấn đề sát sườn kèm con số có nguồn |
| Điểm chính | 4–20 | Con số hoặc thay đổi quan trọng nhất, kèm bằng chứng |
| Thực tế | 20–40 | Người Việt được, mất gì; một so sánh cụ thể |
| Kết | 40–50 | Câu cuối nối lại câu đầu để xem lặp |

Kết mặc định là **vòng lặp**, không có băng "Xem bản đầy đủ ở video liên kết" **(mình chọn)**: tỉ lệ ở lại đang thấp nên chưa có gì để chở sang video dài. Dòng trỏ về video dài trong mô tả (`dang._upload_short`) giữ nguyên.

Máy kiểm mới `phong_cach.kiem_short(script_md, wpm)`:

| Luật | Mức |
|---|---|
| Ước thời lượng ngoài 30–55 giây | lỗi |
| Câu đầu mở bằng từ nối ("Thứ nhất", "Còn", "Vậy", "Và", "Nhưng", "Tiếp theo", "Ngoài ra") | lỗi |
| Câu đầu không có con số gắn `[#id]` | lỗi |
| Câu đầu dài hơn 22 từ | cảnh báo |
| Hai câu đầu có hơn một câu hỏi | cảnh báo |
| Có lời nói về việc kể chuyện hoặc trỏ đi chỗ khác ("mình đọc lại", "video trước", "dưới mô tả"…) | cảnh báo |
| Từ giật gân, "!" | lỗi (dùng lại danh sách của `tieu_de`) |

Kiểm nguồn dùng `tttc.kiem` sẵn có, đọc `nguon.json` của thư mục cha. Tiêu đề Short chấm bằng `tieu_de.kiem` và `kiem_khop_nguon` như video dài.

### 4.3 Giọng

`giong_vieneu.synthesize(ngan/<k>)` với cấu hình ghi đè cho Shorts: `pause_cau = 0.10`, `pause_doan = 0.10` (video dài đang 0,14 và 0,32). Đặt ở `config.json:vieneu.shorts`. Giọng chính giữ nguyên; không dùng giọng phụ trong đợt này **(mình chọn)**, để lứa đầu chỉ đổi hình và kịch bản.

### 4.4 Bộ mẫu cảnh dọc

Thư mục mới `pipeline/templates/canh-doc/`, mỗi mẫu vẽ cho 1080×1920, dùng chung `base.css`, `dong.js` và bảng màu `theme` với mẫu ngang.

| Mẫu | Dùng cho | Trường chính |
|---|---|---|
| `moc` | Khung 0 và các điểm số lớn | `chu` (≤ 8 từ), `so`, `nhan`, `nguon` |
| `bang-chung` | Ảnh chụp văn bản, trang giá | `anh`, `vung` (tọa độ cắt phóng), `tom_tat` (một dòng tiếng Việt), `nguon` |
| `anh` | Ảnh báo chí, b-roll | `anh` hoặc `video`, `diem_giu` (điểm giữ khi cắt dọc), `nhan`, ghi công |
| `doi-chieu` | So sánh hai vế | `tren`, `duoi` (mỗi vế: `nhan`, `so`), `noi_bat` |
| `ket` | Câu kết | `chu`, `so?` |

Luật chung cho cả bộ:

- **Khung 0 đã đủ nội dung.** Trong `moc` ở cảnh đầu, chữ và số hiện đủ độ đậm ngay từ t = 0. Hiệu ứng vào chỉ là phóng nhẹ, không đi từ trong suốt. Feed Shorts hiện khung đầu trước khi phát.
- **Vùng an toàn (mình chọn, kiểm lại trên điện thoại thật):** không đặt chữ trong 220 px trên cùng, 380 px dưới cùng, 140 px mép phải. Đó là chỗ giao diện Shorts che (tên kênh, tiêu đề, nút bấm).
- **Phụ đề:** giữ phụ đề từng từ của nhánh dọc hiện có (`phu_de(..., doc=True)`), đặt trong một dải cố định; các mẫu chừa dải đó ra. Riêng cảnh `moc` đầu tiên, chữ hook là chính, phụ đề nằm dưới.
- **Cỡ chữ tối thiểu 56 px** trên khung 1080 px rộng; nguồn và ghi công 30 px.
- **Bằng chứng** luôn cắt phóng vào đúng dòng hoặc con số, có viền, kèm một dòng tóm tắt tiếng Việt. Không chiếu nguyên trang.

### 4.5 Ghép và render

`dung.compose` nhận biết chế độ dọc gốc qua `canh.json` có `"khuon": "doc"`:

- Đọc mẫu từ `canh-doc/`, mỗi cảnh khai `data-width="1080" data-height="1920"`.
- Không bọc `#san-khau` thu nhỏ, không sinh băng `#short-hook` và `#short-cta`.
- Chuyển cảnh chỉ cắt thẳng kèm tiếng lướt ngắn. Không dùng mống mắt, chớp tối, ba lớp quét (các hiệu ứng này tính theo khung ngang).
- Nhãn bồi (`boi`) vẫn dùng được; tọa độ nhân với 1080 và 1920.
- Tham số mới để đọc `nguon.json`, `anh/`, `broll/`, `nguon/` từ thư mục cha.
- Nhạc nền và chuẩn âm lượng −14 LUFS như video dài.

Nhánh cũ (`scene_range` + thu nhỏ) giữ nguyên trong mã để dựng lại được Shorts cũ, nhưng skill không gọi nữa.

Render: `scripts/render.sh ngan/<k>/composition shorts/<k>.mp4 delivery`, sau đó trích `khung-0.png` (t = 0) và `khung-3.png` (t = 3 s).

### 4.6 Cổng chất lượng

`canh.validate` nhận các mẫu dọc, vẫn kiểm số trên hình khớp nguồn (`_check_values`).

Hàm mới `chat_luong.kiem_short(canh, timing, mp4)`:

| Luật | Mức |
|---|---|
| Cảnh đầu không phải `moc`, hoặc không bắt đầu ở 0, hoặc `chu` quá 8 từ, hoặc thiếu `so` | lỗi |
| Thời lượng tệp ngoài 30–55 giây (ffprobe) | lỗi |
| Có cảnh dài hơn 6 giây | cảnh báo |
| Trung bình mỗi cảnh dài hơn 3,5 giây | cảnh báo |
| Giữa hai từ liền nhau trong `giong-timing.json` nghỉ quá 0,25 giây | cảnh báo |
| Khung không đúng 1080×1920 | lỗi |

### 4.7 Quy trình trong skill `video-dung` (viết lại mục 7)

1. Chọn 2 góc từ `kich-ban.md` của video dài, mỗi góc có ít nhất một con số có nguồn.
2. Viết `ngan/<k>/kich-ban.md`; chạy `phong_cach.kiem_short` và `tttc.kiem`; sửa hết lỗi.
3. Đọc giọng; viết `canh.json` bằng mẫu dọc; `canh.validate`.
4. `dung.compose` → render → `chat_luong.kiem_short` → trích hai khung.
5. Thêm vào `dong-goi.json:shorts` (`file`, `tieu_de`, `ngay`, `gio`, thêm `mo_ta` riêng nếu có; không có thì dùng mô tả chung như hiện nay).
6. Gửi người dùng: tệp mp4, hai khung, tiêu đề, giờ đăng. **Dừng.** Người dùng nói "ok" thì mới chạy `duyet-short`; đăng bằng `/video-dang` như cũ.

`trang_thai`, `dang.upload_short` không đổi ngoài việc đọc `mo_ta` riêng của Short.

### 4.8 Đo

- Thêm hai cột vào `theo_doi.EXTRA`: `o_lai_short` (tỉ lệ "ở lại xem", nhập tay từ Studio) và `khuon_short` (`cu` hoặc `doc`, `dang` ghi lúc upload).
- **Mỗi lứa chỉ đổi một biến.** Lứa đầu (6 Shorts): chỉ đổi cách dựng, giữ loại đề tiêu dùng có giá cụ thể như hai Short 940 và 888 view.
- **Điểm dừng sớm (mình chọn):** sau 6 Shorts kiểu mới, nếu trung vị `o_lai_short` dưới 25% thì dừng thêm mẫu cảnh, xem lại câu hook và chọn đề trước.

## 5. Kiểm thử

Theo quy ước mỗi module một tệp trong `pipeline/tests/`:

- `test_dung.py`: `canh.json` có `"khuon": "doc"` thì trang ghép không có `#san-khau`, `#short-hook`, `#short-cta`; cảnh khai 1080×1920; không có chuyển cảnh mống mắt/chớp tối; đọc nguồn từ thư mục cha. Nhánh cũ vẫn cho kết quả như trước.
- `test_phong_cach.py`: từng luật của `kiem_short`, có ca "Thứ nhất," của Short 7-Zip.
- `test_canh.py`: mẫu dọc hợp lệ và không hợp lệ; số trên hình lệch nguồn bị bắt.
- `test_chat_luong.py`: từng luật của `kiem_short`.
- `test_theo_doi.py`: `migrate` thêm hai cột mới, giữ dữ liệu cũ.
- `test_giong_vieneu.py`: cấu hình `vieneu.shorts` ghi đè quãng nghỉ.

Kiểm bằng mắt: dựng lại Short 1 của video 7-Zip theo kiểu mới (máy còn đủ ảnh nguồn và bản cũ của video này; thư mục "cấm nhập máy cũ" không còn tệp media), đặt khung 0 và khung 3 cạnh bản cũ, xem trên điện thoại thật để chỉnh vùng an toàn.

## 6. Phần để người xây quyết

- Bố cục, cỡ chữ, chuyển động cụ thể của từng mẫu dọc (trong các luật ở 4.4).
- Tên tham số mới của `compose` và cách chia hàm.
- Cách trích khung (ffmpeg trong `render.sh` hay hàm Python).
- Có gộp `moc` và `ket` thành một mẫu hai biến thể hay không.

Điểm người xây phải kiểm trong mã trước khi lập kế hoạch (bản này chưa đọc tới):

- `tttc.kiem` và `giong_vieneu.synthesize` nhận đường dẫn thế nào, để trỏ `nguon.json` về thư mục cha mà không chép tệp.
- `dung._scene_file` tra tiền tố id trong bảng `PREFIX` theo tên mẫu; mẫu dọc cần mục riêng, không trùng tiền tố mẫu ngang.
- `trang_thai._short_snapshot` đang băm tệp, tiêu đề, giờ. Nếu Short có `mo_ta` riêng thì đưa `mo_ta` vào bản băm, để đổi mô tả sau khi duyệt cũng phải duyệt lại.

## 7. Việc người dùng cần biết

- Hai Shorts 7-Zip đã duyệt (hẹn 16/11 và 17/11) vẫn là kiểu cũ. Đăng như đã duyệt hay chờ dựng lại là quyết định riêng, nằm ngoài bản này (bản đề xuất mục 7, việc 5).
- Tỉ lệ "ở lại xem" phải nhập tay từ Studio cho mỗi Short sau 48 giờ; không có số này thì không đánh giá được đợt làm.
