# Nhận diện mới cho kênh

Ngày: 09/11/2026 · Trạng thái: chờ bạn duyệt spec
Spec đi cùng: `2026-11-09-dinh-vi-doi-dau-van-hanh-design.md` (định vị và vận hành) và `2026-11-09-chat-luong-hinh-anh-design.md` (chất lượng hình ảnh; phông và hình mới của spec đó dùng màu từ theme ở mục 4 dưới đây, và bước đạo diễn chọn dáng nhân vật từ `nhan-vat/kit.json`).

## 1. Mục tiêu và phạm vi

Làm lại nhận diện cho khác hẳn @MotCongNghe ngay ở trang chủ YouTube (tên, avatar, thumbnail), vẫn đọc rõ ở cỡ 168 px, và để lần đổi sau rẻ.

**Làm lại (bạn chọn 09/11/2026):** bảng màu + khung thumbnail; nhân vật dẫn chuyện + giọng đọc; tên kênh, logo, avatar, banner.
**Giữ nguyên:** phong cách hình isometric trong video; công thức nội dung.

Hiện trạng trùng với kênh mẫu: nền đen + vàng `#FFC800`; thumbnail chia đôi bằng đường răng cưa, hai hộp chữ vàng, vòng "VS" (`thumb.chia_doi` được viết theo khuôn 3 thumbnail top của họ); nhân vật dẫn chuyện cùng vai trò với "Mọt".

## 2. Thứ tự và phụ thuộc

```
Quyết định (bạn) → A. Lớp màu → B. Bộ nhân vật → C. Tài sản kênh → D. Áp lên kênh
```

- Palette phải chốt trước B, vì ảnh raster của nhân vật không đổi màu theo theme được như SVG.
- A, B và khung thumbnail (một phần của C) phải xong trước khi chạy khô (spec 1, mục 7), vì chạy khô dựng cả thumbnail đến duyệt 2. Logo, avatar, banner (phần còn lại của C) và D phải xong trước ngày chạy thật G; không cần cho chạy khô vì chạy khô không đăng.
- Việc làm chắc pipeline (spec 1, mục 6) chạy song song với A–C.

## 3. Quyết định cần bạn

| Mục | Yêu cầu | Cách chọn |
|---|---|---|
| Tên + handle | Nói được "tin nóng công nghệ–kinh tế, góc Việt Nam"; không chứa "Mọt"; không còn mã hóa góc túi tiền; handle còn trống | Tôi đưa danh sách ứng viên và kiểm handle; bạn chọn |
| Palette | Gồm nền, màu nhấn (kèm 2 sắc đậm hơn), mực, giấy kem, 4 màu phụ theo nghĩa (tiết kiệm, rủi ro, AI/dữ liệu, cao cấp). Màu nhấn **không** là cặp đen–vàng và không trùng 4 màu phụ | Đặt thumbnail thử cạnh thumbnail của 8–10 kênh công nghệ/kinh tế tiếng Việt (lấy bằng vidIQ) và 3 thumbnail top của @MotCongNghe; bạn chọn |
| Tính cách nhân vật | Vai trò: người dẫn chuyện nhỏ ở góc màn hình, chớp mắt, phản ứng theo lời. Tính cách, hình dạng, khác "Mọt" ở những điểm cụ thể | Bạn cho tôi ảnh/mô tả "Mọt" để ghi vào brief điểm khác; bạn chọn 1 trong 4–6 concept |
| Giọng | Chọn trong các giọng VieNeu có sẵn | `giong_vieneu nghe-thu`; bạn nghe cả giọng của họ và giọng ứng viên rồi chọn giọng khác rõ. Tôi chưa nghe giọng của họ nên không đảm bảo khác. Ghi vào `config.json:vieneu.voice`; chỉnh `toc_do` theo H4 của spec 1; nghe thử danh sách từ đệm và câu lửng của spec 4 (`2026-11-09-giong-van-kich-ban-design.md`) với giọng này |

## 4. A. Lớp màu một nguồn

**Hiện trạng (đã đo):** màu nằm rải ở khoảng 9 nơi.
- `svg/ve.py`: 6 hằng số (`INK, WHITE, LIGHT, MID, DARK, Y`) và bộ ba sắc vàng `#E0B000`/`#C79C00` viết thẳng ở nhiều dòng; khoảng 65 tệp SVG sinh ra từ đây.
- `tttc/dung.py`: bảng `SAC` (4 màu phụ) và `VANG`; hai thứ này đổi màu SVG theo chương bằng cách thay chuỗi hex nên hex trong SVG phải khớp tuyệt đối. Còn hex trong CSS nhúng (dòng ~351–352).
- `templates/canh/base.css`: biến CSS nhưng ba lớp nền `nen-toi/nen-kem/nen-vang` lặp hex.
- `templates/canh/trich-bao.html`, `b-roll.html`, `trang-nguon.html`, `nhan-vat.html`, `templates/duyet.html`, `tttc/thumb.py`, `brand/make_brand.py`.

**Thiết kế**
- `brand/theme.json` là nguồn duy nhất: nền, mực, nhấn (+ sắc đậm), muted, đường kẻ, thanh, giấy kem (+ sắc), 4 màu phụ (nhấn, bóng, bóng tối, màu chữ trên nhấn), font hiển thị.
- `tttc/theme.py` đọc theme và cung cấp hằng số Python cho `ve.py`, `dung.py`, `thumb.py`, `make_brand.py`, cùng một khối `:root{--...}` để compose nhúng vào CSS. Mẫu cảnh và `duyet.html` dùng biến CSS, không viết hex.
- Lệnh `uv run python -m tttc.theme ap-dung`: sinh lại toàn bộ SVG thư viện và logo, rồi kiểm tương phản (mực/nền, chữ-trên-nhấn/nhấn, muted/nền ≥ 4,5:1) và in bảng soi thư viện (`svg/sheet.py`).
- Màu **vật thể** không nằm trong theme và được phép viết thẳng (cờ đỏ `#DA251D`, gỗ, xám trung tâm dữ liệu trong `ve.py`).

**Nghiệm thu**
1. Test 1: không còn hex thương hiệu cũ viết cứng ngoài `theme.json` và danh sách ngoại lệ vật thể.
2. Test 2: SVG trong repo bằng kết quả sinh lại từ theme hiện tại.
3. Test 3: đổi một giá trị trong `theme.json`, chạy `ap-dung`, dựng thử 10 cảnh: hình, chữ, nền chương và màu phụ theo chương đổi theo, không sót màu cũ.
4. Bảng soi thư viện: bạn xem một lần.

## 5. B. Bộ nhân vật bằng workflow TobyFlow

**Quy mô:** 6 biểu cảm × 4 góc = 24 dáng, thêm 6 bản nhắm mắt cho góc thẳng (chớp mắt) = 30 ảnh PNG nền trong suốt.
- Biểu cảm đề xuất: chào, ngạc nhiên, nghi ngờ, lo lắng, tự tin, suy nghĩ (bạn đổi được).
- Góc: thẳng, nghiêng trái, nghiêng phải, nghiêng ngang.

**Workflow** (tạo bằng công cụ TobyFlow sau khi spec này được duyệt):
1. Concept: 4–6 prompt chữ, ảnh 1:1, mỗi prompt 4 phương án; bạn chọn 1 concept.
2. Bản xoay 4 góc từ concept (ảnh tham chiếu).
3. Mỗi dáng: Flow "Nano Banana 2.1" (tối đa 10 ảnh tham chiếu, 4 phương án/lượt) với concept + bản xoay làm tham chiếu; prompt ghép tự động từ bảng biểu cảm × góc. Brief cố định: nét viền đậm cùng độ dày với thư viện SVG, màu phẳng đúng palette, nền phẳng một màu, **không chữ, không logo, không mặt người thật**.
4. Bảng soi 30 dáng để bạn duyệt một lần. Dáng lệch nhân vật thì bỏ hoặc tạo lại; thiếu thì giảm số dáng thay vì giữ dáng lỗi.

**Hậu xử lý cục bộ:** tách nền phẳng bằng PIL (đã cài), cắt sát, đổi cỡ (đích hiển thị 280×280 px ở khung 1920×1080, lưu gấp đôi), ghi `nhan-vat/<the>-<huong>.png` và `-nham.png`. Viền xấu thì mới cân nhắc dịch vụ xóa nền trả phí, và hỏi bạn trước.

**Nối vào pipeline**
- `canh.json`: `dan.the` mở rộng từ 3 giá trị (`chao, ngac-nhien, nghi`) sang 6 biểu cảm; thêm `dan.huong` (`truoc, nghieng-trai, nghieng-phai, ngang`); `dan.goc` (`phai|trai`, vị trí trên màn hình) giữ nguyên. `huong` mặc định tự chọn quay vào giữa màn hình theo `goc`.
- `nhan-vat/kit.json` liệt kê các cặp (`the`, `huong`) có sẵn; `tttc/canh.py` kiểm hợp lệ theo tệp này, nên thêm dáng không phải sửa code.
- Sửa `tttc/canh.py` (hằng số `DAN_THE`, `DAN_GOC`, `_check_dan`), `tttc/dung.py` (chỗ ghép `<img src="assets/svg/tui-{the}.svg">` và bản `-nham` quanh dòng 302–320; chỗ bỏ qua `tui-` khi đổi màu theo chương ở dòng ~240 và ~271) và test tương ứng.
- Shorts dọc vẫn không dùng nhân vật (như hiện nay).
- 6 tệp `svg/tui-*.svg` của nhân vật cũ gỡ khỏi `pipeline/svg` khi bộ mới được duyệt, không trước.

**Nghiệm thu**
1. 30 PNG nền trong suốt, cùng một nhân vật nhận ra được qua cả 24 dáng (bạn duyệt).
2. Dựng thử một cảnh cho mỗi biểu cảm × góc: nhân vật hiện đúng lúc nói `tu`, nhấp nhô, chớp mắt ở góc thẳng.
3. `tttc.canh` từ chối `the`/`huong` không có trong `kit.json`; test mới đi kèm.

**Giới hạn đã biết**
- TobyFlow hiện **offline**: extension chưa mở. Bạn mở sidebar và đăng nhập trước khi tạo.
- Khối lượng khoảng 150 lượt tạo ảnh (concept, bản xoay, 30 dáng × 4 phương án). Cấu hình ước ~45 giây/ảnh nên cỡ 1,5 giờ nếu tuần tự; hạn mức ngày của gói bạn chưa biết. Giới hạn tạo workflow 20/ngày, đủ dùng.
- Lệch nhân vật giữa các dáng và phong cách ảnh AI lệch với SVG phẳng: giảm bằng ảnh tham chiếu, brief cố định và bước duyệt.

## 6. C. Tài sản kênh

| Tài sản | Yêu cầu | Công cụ |
|---|---|---|
| Logo + avatar | Đọc rõ ở 98 px; dùng palette mới | CoDesign (IMG.LY) hoặc TobyFlow |
| Banner | Khung an toàn của YouTube; có tên kênh và câu định vị | CoDesign hoặc TobyFlow |
| Khung thumbnail | Bố cục **khác hẳn** khuôn của họ: không chia đôi răng cưa, không hai hộp chữ vàng, không vòng "VS". Đọc ra chữ ở 168 px | Viết lại `thumb.chia_doi` (và `thumb.make`) đọc màu từ theme |

Giữ cơ chế ba phương án thumbnail của `/video-dung` mục 6 (khung mới, CoDesign, nền TobyFlow), chỉ đổi màu và khung theo theme mới.

**Nghiệm thu:** bảng so thumbnail mới đặt cạnh 3 thumbnail top của @MotCongNghe và thumbnail của 8–10 kênh khác ở 168 px; bạn xác nhận nhìn là phân biệt được ngay.

## 7. D. Áp lên kênh

- **Bạn làm trong YouTube Studio:** đổi tên, handle, avatar, banner; đổi thumbnail video nvidia đã đăng. YouTube giới hạn số lần đổi tên/handle trong một khoảng thời gian; tôi chưa kiểm giới hạn hiện hành.
- **Tôi làm trong repo:** thay chuỗi tên ở `pyproject.toml`, ba tệp SKILL, chuỗi User-Agent trong `tttc/anh.py` và test của nó. Giữ nguyên tên dịch vụ Keychain `tui-tien-cong-nghe` (đổi sẽ làm mất token OAuth đã cấp).
- Video `goi-ai-dang-tien` render lại sau A–C nếu bạn muốn đăng (spec 1, mục 8).

## 8. Rủi ro

1. **Nhận diện mới vẫn gần kênh mẫu:** vì phong cách hình isometric được giữ nguyên theo lựa chọn của bạn, khác biệt dồn vào màu, nhân vật, thumbnail, tên và giọng. Nghiệm thu ở mục 6 là chốt chặn.
2. **Đổi tên kênh khi đã có một video:** người xem và liên kết cũ thấy tên mới; ảnh hưởng nhỏ vì kênh mới có một video.
3. **Raster không đổi màu theo theme:** đổi palette sau khi có bộ nhân vật thì phải tạo lại bộ nhân vật.
4. **Công cụ ngoài:** TobyFlow phụ thuộc extension và tài khoản; CoDesign phụ thuộc đăng nhập IMG.LY. Hỏng thì dùng `thumb.make` và SVG như hiện nay.

## 9. Ngoài phạm vi

- Đổi phong cách hình isometric, font, nhạc nền hay hiệu ứng âm thanh.
- Nhân vật hoạt hình đầy đủ (chỉ ảnh tĩnh nhấp nhô và chớp mắt).
- Đổi công thức nội dung và định vị (spec 1).
