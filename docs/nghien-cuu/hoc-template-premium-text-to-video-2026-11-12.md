# Học từ bộ template premium-text-to-video (12/11/2026)

Nguồn: `/Users/quangtinh/Documents/premium-workflow-create-video/premium-text-to-video` (Remotion/React, 36 template:
creative, commerce, 25 bộ news, media-showcase cho `/tao-tin`, long-explainer 16:9). Ghi lại những cách làm tốt để
mang sang pipeline HyperFrames/GSAP của kênh; **học cách làm, không chép mã hay bố cục nguyên xi**.

**User chốt 12/11/2026: bộ `news/tech-dark` (và bản sáng `tech-light`) khá phù hợp với kênh.** Đó là bộ tham chiếu
chính khi chỉnh nhận diện và hiệu ứng.

Quy đổi đơn vị: Remotion 30 fps → 1 khung = 0,033 s (26 khung ≈ 0,87 s; 12 khung = 0,4 s).

## 1. Bộ tech-dark: vì sao hợp kênh và lấy gì

Màu gần như trùng nhận diện kênh (`brand/theme.json`): tech-dark nền `#0B0C10`, nhấn cyan `#00D4FF` → lam `#4F7FFF`;
kênh nền `#08181C`, nhấn `#22D3EE`. Lấy được gần như nguyên tinh thần mà không phải đổi nhận diện.

Tệp: `src/templates/news/tech-dark/` (tokens, GlowBackground, Layout, ParticleNetwork) + `src/templates/news/shared/`
(Badge, TagRow, Headline, BodyText, StatCard, BarChart, CompareCard, ImageCard, SceneHook/Body/Ending, parseAccent).

| Thành phần | Cách làm | Mang sang kênh |
|---|---|---|
| Nền "không gian sâu" | 5 đốm sáng radial ở 4 góc + giữa trên, mỗi đốm "thở" `scale` 0,7→1 theo `sin(frame·0,008 + pha)`, màu nhấn độ mờ 6–12% | Thay/kèm gradient tĩnh của `nen-toi`: thêm 3–5 đốm thở chậm (GSAP yoyo hữu hạn) |
| Mạng hạt | 14 hạt cyan/lam trong 15% trên khung, vị trí từ seed cố định (render lại không đổi), nối dây khi gần < 300px, độ mờ dây giảm theo khoảng cách | Lớp trang trí mép trên cho cảnh chương/mở đầu; phải tất định (seed), không `Math.random` |
| Thanh nhấn mép trên | 6px gradient cyan→lam, `box-shadow` phát sáng | Hợp với thanh tiến trình chương sẵn có: cho thanh có gradient + glow |
| Chữ nhấn gradient | Từ trong `{ngoặc}` tô gradient cyan→lam bằng `background-clip: text` | Thay màu nhấn phẳng ở `chu-dong`, `so-lon` (nền tối); nền kem giữ màu phẳng |
| Gạch dưới tiêu đề | Gạch 64×5px gradient, dài ra khung 20→45 sau tiêu đề, có glow | Giống `sl-gach` của kênh; thêm gradient + glow |
| Nhãn loại tin (Badge) | Chấm phát sáng + chữ gradient "TIN NÓNG / SỰ KIỆN / PHÂN TÍCH / CẬP NHẬT / TÓM TẮT" · ngày; dòng dưới cờ + quốc gia nối bằng "→" | Nhãn góc trên cảnh mở đầu theo `Loại:` của template kịch bản (`ra-mat` → RA MẮT, `ro-ri` → TIN RÒ RỈ…) |
| Thẻ hashtag | Viên `#AI #Apple`, nảy lần lượt (spring, cách 8 khung); thẻ đầu đậm hơn | Dòng thẻ chủ đề ở cảnh mở đầu/b-roll |
| Thẻ số (StatCard) | Thẻ kính tối, viền trái 4px màu nhấn, nhãn IN HOA mờ + icon, số đếm 0→giá trị (khung 8→50) gradient, đơn vị nhỏ màu mờ, dòng ngữ cảnh | Biến thể nhỏ của `so-lon` đặt cạnh ảnh (số + ngữ cảnh), khi cảnh cần cả ảnh lẫn số |
| Thẻ ảnh (ImageCard) | Bo 16px, viền mảnh, chấm nhãn "ẢNH/VIDEO" góc trái, nhãn địa điểm góc phải, **dải "Nguồn: X · ngày" bắt buộc**, tự chọn cover/contain theo tỉ lệ ảnh, ảnh dọc 9:16 giới hạn cao | Khung ảnh `b-roll`/`minh-hoa`: thêm chấm loại ảnh + nhãn địa điểm |
| Nhịp hiện | Thẻ (0) → nhãn (0) → tiêu đề (10–12) → thân (28–35) → số/biểu đồ (42) → ảnh (55) | Thứ tự so le này hợp lời đọc; ở kênh thay mốc cứng bằng `nhip` |
| Màn kết | Nút "Bấm Theo Dõi" cố định, chuông lắc 18°/-16°/12° mỗi 2 s, nút đập 1,2% | Kênh đã có `ket-thuc`; có thể thêm chuông lắc. Không gắn CTA theo bài báo |

Luật viết tiêu đề của tech-light đáng giữ: hook ≤ 10 từ, thân ≤ 12 từ; 1–3 cụm nhấn, không hơn; dùng "—" để đối
("Apple ra mắt {chip M5} — mạnh hơn {40%}"); tiêu đề video ≤ 8 từ, tò mò trước.

## 2. Hiệu ứng tốt ở các bộ khác

| # | Hiệu ứng | Bộ | Công thức | Chỗ dùng ở kênh |
|---|---|---|---|---|
| 1 | **Bằng chứng zoom + dạ quang** | long-explainer `Beats.tsx` (Evidence) | Ảnh chụp bài báo phóng tới khi câu trích chiếm ~70% thẻ (tối đa 2,4×), điểm nét kéo về giữa (0→22 khung, `inOut cubic`); rồi vệt vàng `#FACC15` `multiply` 85% quét từng dòng, 10 khung/dòng; thẻ nghiêng nhẹ, nhãn "Nguồn: báo · ngày" | Nâng `trang-nguon` (toạ độ dòng lấy từ `tttc.chup`) |
| 2 | **Mở ảnh không méo** | real-estate-civic `CivicScene.tsx` | Khung `scaleX(r)`, ảnh bên trong `scaleX(1/r)`; mở từ giữa (cảnh mở/số/kết) hoặc từ trái; ảnh zoom 1,12→1,03; lớp màu nhấn `screen` 50% | `b-roll`, `minh-hoa`, `trich-bao` |
| 3 | Mở ảnh bằng `clip-path` | business, sports, auto, entertainment | `clip-path: inset(0 X% 0 0 round R)` X: 100→0, 32 khung | Cách mở thứ hai, xen kẽ với #2 |
| 4 | **Nền mờ từ chính ảnh** | modern-news-canvas, commerce | Ảnh dọc/nhỏ: phía sau là chính ảnh phủ kín, blur 34–50px, độ mờ 22% hoặc sáng 22%, scale 1,08–1,15 | Ảnh dọc, logo, ảnh chân dung trong khung ngang |
| 5 | **Một ảnh nhiều cảnh** | media-showcase | Cắt vùng khác mỗi 2,5 s, xoay 4 tâm (50/45, 28/35, 72/60, 40/70), mỗi vùng zoom 1,06→1,16; ≥ 2 ảnh thì luân phiên ≤ 3 s | Đề chỉ có 1–2 ảnh thật |
| 6 | Ghép ảnh dán | long-explainer (Collage) | 1–3 ảnh viền trắng 5px, bóng đổ đậm, nghiêng ±2,5° tất định, trôi 15px + scale 1→1,03, dải ghi công dưới mỗi ảnh | Cảnh nhân vật/địa điểm nhiều ảnh |
| 7 | **Biểu đồ đường tự vẽ** | business-terminal (LineChart) | SVG `path` `pathLength=1`, `stroke-dashoffset` 1→0 trong 45 khung; điểm sáng dần theo tiến độ; màu theo xu hướng (tăng xanh/giảm đỏ/cảnh báo hổ phách) | Mẫu mới cho giá vàng, tỷ giá, cổ phiếu |
| 8 | Dải mã giá chạy | business-terminal (TickerStrip) | Danh sách nhân đôi, `translateX` chạy vòng, font mono, thay đổi tô màu xu hướng | Mở đầu tin thị trường |
| 9 | Đồng hồ cung + kim | auto-showroom (Gauge) | Cung SVG tự vẽ tới 72%, kim quay theo `cos/sin` cùng tiến độ, tâm chấm màu | Biến thể `phan-tram` cho tốc độ, hiệu năng |
| 10 | **Vệt sáng lướt tiêu đề** | auto-showroom (Headline) | Dải 130px gradient trong suốt→nhấn 33%→trong suốt, blur 10px, `skewX(-18deg)` trượt ngang qua chữ | Tiêu đề `mo-dau`, số `so-lon` lúc chốt |
| 11 | Thẻ văn bản đóng dấu | long-explainer (DocumentCard) | Các dòng hiện cách 10 khung; con dấu nghiêng -10° rơi từ scale 2,2→1 (spring nảy) | Tin luật, nghị định, quyết định phạt |
| 12 | Thẻ lịch, thẻ phép tính | long-explainer (Calendar, Equation) | Lịch rơi xuống (spring); phép tính hiện từng vế cách 24 khung rồi ra kết quả | Hạn chót, "tính ra" của kênh |
| 13 | Thẻ chương | long-explainer (ChapterCard) | Số "01" 300px chỉ viền chữ màu nhấn trượt trái, tiêu đề trượt phải, gạch giữa dài ra | Làm mới `chuong` |
| 14 | Chớp khung màu nhấn | sports-arena | Lớp màu nhấn phủ cả khung, `screen`, tối đa 18% theo nhịp | Lúc số lớn chốt (thay cho `dip` đen) |
| 15 | Thẻ số đè hook (A/B) | media-showcase (HookCard) | Một số có nguồn hiện 2–5 s đầu; script kiểm câu trích chứa đủ chữ số; chia nhóm có thẻ/không thẻ theo slug rồi so giữ chân | Thử nghiệm ở `theo_doi.py` |
| 16 | Bảng tỷ số, nhãn mức cảnh báo | sports, health-public-alert | Lưới 3 cột đội–tỷ số–đội; nhãn mức màu theo nguy hiểm + dòng meta | Tin bảo mật (`bao-mat`): nhãn mức độ nguy hiểm |
| 17 | Chữ dọc trang trí, con dấu bưu điện, ảnh bưu thiếp nghiêng | sports, travel, education | Chữ xoay -90° mờ 22% ở góc; dấu nghiêng -3°; ảnh nghiêng -1,2° | Gia vị, dùng ít |

## 3. Nhịp, âm thanh, chuyển cảnh

- **Luật nhịp** (long-explainer, có máy kiểm): mỗi beat 3–6 s (số liệu ≤ 10 s, còn lại ≤ 8 s); không 3 beat cùng
  loại liền nhau; bằng chứng ≥ 20% số beat; 30 s đầu đổi hình mỗi 1,5–2,5 s; chọn hình theo **đối tượng chịu tác
  động** trong câu, không theo cơ quan chỉ được nhắc tên. → Đưa vào `canh.py validate` dạng cảnh báo.
- **Âm hiệu ứng nhỏ**: 0,10–0,16 (long-explainer), trần 0,25 (template -sfx); kênh đang 0,2–0,35 → hạ.
  Âm suy ra từ loại cảnh; **bỏ âm rơi vào lúc thẻ chương che màn hình**; template -sfx bắt mỗi cảnh ghi lý do chọn âm.
- **Chuyển cảnh theo ý nghĩa** (free-style): mờ dần = tiếp nối; trượt = bước mới; quét = trước/sau; lật = đổi góc
  nhìn; 12–24 khung; không lặp một kiểu ở mọi đường nối. `addTransitionHandles` cộng bù khung để chuyển cảnh chồng
  lên nhau không làm lệch giọng (kênh dùng lớp phủ nên không bị vấn đề này).
- **Phụ đề**: chia câu ở khoảng lặng ≥ 0,45 s, dòng cố định 6–10 từ; video dài tắt phụ đề cháy, giao `.srt`.
  Phụ đề của kênh đã tốt hơn (nhấn số, nảy, hộp nền) — giữ.

## 4. Không học

- Icon emoji (⚡💰🔔) trong thẻ: dùng icon SVG của kênh.
- Font Arial mặc định ở source-led/article-demo.
- Nhạc nền bắt buộc ở mọi video tech (kênh chưa chốt nhạc, D5).
- Tiêu đề cảnh dạng "tờ báo" chiếm nửa khung Shorts kèm phụ đề: quá nhiều chữ cho video ngang 8–14 phút.
- Chọn tin giật gân của `/tao-tin` (vụ án, tai nạn): khác định vị kênh công nghệ–kinh tế.

## 5. Kênh đã hơn, giữ nguyên

Chuyển cảnh mống mắt và ba lớp; nhân vật Nhịp; phụ đề nhấn số; nền theo vai trò (tối/kem/vàng); chữ hiện đúng từ
đang đọc (`nhip`, `moc_tu`); số khung cuối đúng chuỗi nguồn; máy kiểm số có nguồn trong từng cảnh.

## 6. Thứ tự đề xuất nếu mang sang

1. Bộ nhận diện tech-dark cho nền tối: đốm sáng thở, chữ nhấn gradient, gạch/thanh có glow (sửa `base.css`, `dong.js`).
2. Bốn hiệu ứng nhỏ: mở ảnh không méo (#2), nền mờ từ ảnh (#4), vệt sáng lướt (#10), hạ âm hiệu ứng.
3. Bằng chứng zoom + dạ quang (#1) cho `trang-nguon`.
4. Luật nhịp vào `canh.py validate` (cảnh báo).
5. Mẫu mới: biểu đồ đường (#7), thẻ văn bản đóng dấu (#11), thẻ lịch (#12).
