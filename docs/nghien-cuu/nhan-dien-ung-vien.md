# Ứng viên nhận diện kênh – 10/11/2026 (Task 7 của kế hoạch nhận diện mới)

## 1. Tên và handle
Điều kiện (spec nhận diện mới, mục 3): nói được "tin nóng công nghệ–kinh tế, góc Việt Nam"; không chứa "Mọt"; không còn mã hóa góc túi tiền; handle còn trống.
Kiểm bằng `curl -A 'Mozilla/5.0' https://www.youtube.com/@<handle>` ngày 10/11/2026: 404 = chưa ai dùng, 200 = đã có kênh. **Phải kiểm lại trong YouTube Studio khi đổi** (404 từ ngoài chưa chắc chắn handle còn đăng ký được).

| Tên | Handle | Trạng thái | Ý nghĩa và điểm yếu |
|---|---|---|---|
| Công Nghệ Có Nguồn | @congngheconguon | trống | Nói thẳng nguyên tắc kênh (mọi số đều dẫn nguồn gốc); khác hẳn kênh mẫu. Hơi dài, chưa nói "tin nóng" |
| Nhịp Công Nghệ | @nhipcongnghe | trống | Ngắn, dễ nhớ, gợi nhịp tin hằng ngày. Chung chung, chưa nói kinh tế |
| Số Liệu Công Nghệ | @solieucongnghe | trống | Khớp công thức "số lớn, cặp số"; nghe khô |
| Tin Nóng Công Nghệ | @tinnongcongnghe | trống | Nói đúng "tin nóng", dễ tìm kiếm. Quá phổ thông, khó nhớ riêng |
| Bản Tin Công Nghệ | @bantincongnghe | trống | Trang trọng, rõ là tin. Giống tên báo, ít cá tính |
| Công Nghệ Kinh Tế VN | @congnghekinhtevn | trống | Nói đủ mảng và góc Việt Nam. Dài, như nhãn danh mục hơn là tên |
| Tin Công Nghệ Hôm Nay | @tincongnghehomnay | trống | Rõ tính thời sự. Dài, dễ trùng ý với nhiều kênh |
| Đọc Gốc Công Nghệ | @docgoccongnghe | trống | Gợi "đọc tài liệu gốc"; lạ tai |
| Góc Nhìn Công Nghệ | @gocnhincongnghe | **đã có** | loại |
| Điểm Tin Công Nghệ | @diemtincongnghe | **đã có** | loại |

Chưa kiểm: nhãn hiệu/tên trùng ngoài YouTube (Facebook, TikTok, tên miền), giới hạn số lần YouTube cho đổi tên và handle.

## Đã chọn (10/11/2026)
Tên: **Nhịp Công Nghệ**, handle dự kiến @nhipcongnghe (bạn chọn trong phiên; cần kiểm lại và đăng ký trong YouTube Studio).

## 2. Bảng màu (chọn 10/11/2026): B – ngọc lam trên xanh đen
Ba ứng viên: A cam #FF7A1A trên #0B1626, **B ngọc lam #22D3EE trên #08181C**, C hồng #FF3D8B trên #150A20; cả ba qua bộ kiểm tương phản `tttc.theme` (mực/nền ≥ 18:1, chữ/nhấn 5,7–10:1, muted/nền ≥ 9,9:1).
Bạn chọn A trước, rồi **đổi sang B** sau khi xem avatar kênh mẫu: avatar @MotCongNghe là nhân vật nền tròn **cam**, áo cam; thumbnail đen–vàng. Cam trùng màu nhận diện avatar của họ nên bị loại.
Chưa làm: so với thumbnail 8–10 kênh công nghệ Việt khác (công cụ `vidiq_similar_channels` hết credit); chỉ so với kênh mẫu và quy tắc tương phản. Lưu ý B gần màu phụ "lam" (#2979FF, AI/dữ liệu) hơn A và C; sẽ chỉnh màu phụ khi áp.

## 3. Brief nhân vật (đề xuất, chờ bạn xác nhận)
**Mọt (kênh mẫu), xem trực tiếp avatar:** cậu bé hoạt hình, tóc đen xù, kính tròn, áo polo cam, miệng mở cười, tay vẫy; nền avatar tròn cam.
**Nhân vật mới tên "Nhịp"** (gắn với tên kênh):
- Hình dạng: robot nhỏ phong cách isometric, thân và đầu là khối vuông bo góc màu trắng xám, **mặt là một màn hình LED tối** hiện hai mắt và miệng bằng nét sáng ngọc lam; một ăng-ten ngắn có chấm sáng nhấp nháy theo nhịp (nhịp tim/xung).
- Khác Mọt cụ thể: không phải người (không tóc, kính, áo, tay vẫy); thân trắng xám với điểm nhấn ngọc lam, không có cam hay vàng; biểu cảm đọc bằng nét sáng trên màn hình, không phải gương mặt người; tư thế không có động tác vẫy.
- Tính cách: điềm tĩnh, hay hoài nghi có lý lẽ; "chớp xung" khi gặp con số lạ, gật nhẹ khi nguồn khớp; không ba hoa.
- Bộ biểu cảm (kit): `chao`, `ngac-nhien`, `nghi` (giữ tên cũ để cảnh cũ vẫn chạy) cộng `xac-nhan` (số khớp nguồn) và `bo-ngo` (chưa kiểm được); các hướng nhìn `truoc`, `nghieng-trai`, `nghieng-phai`, `ngang`; mỗi cặp biểu cảm × hướng có ảnh nhắm mắt (mắt LED tắt một nhịp) để chớp.
- "Túi" hiện tại (khối vàng xếp tầng, gần giống phong cách Mọt về màu) sẽ được thay khi bộ nhân vật mới tạo xong; đến lúc đó `kit.json` chưa có thì mẫu cảnh vẫn dùng Túi.

## 4. Giọng (chọn 10/11/2026)
Nghe thử Mai Anh, Thùy Dung, Minh Triết, Quang Sơn và Quốc Tuấn; bạn **giữ Quốc Tuấn** (giữ `vieneu.voice`, không cần đo lại tốc độ). Chưa so với giọng kênh mẫu.
