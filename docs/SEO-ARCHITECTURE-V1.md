# Tìm Mua Smart City — SEO Architecture V1

Ngày lập: 2026-08-25

## Mục tiêu

Biến timmuasmartcity.com từ một trang quỹ căn thành buyer portal cho toàn bộ Vinhomes Smart City. Mỗi nhóm URL phải phục vụ một ý định tìm kiếm rõ ràng và dẫn người dùng về quỹ căn thực tế.

## Cấu trúc nội dung chuẩn

### 1. Hub cấp đô thị

- `/` — tổng quan buyer portal, điểm vào cho dự án, thị trường và quỹ căn.
- `/phan-khu.html` — hub toàn bộ phân khu/dự án.
- `/gia-ban-vinhomes-smart-city.html` — hub dữ liệu giá.
- `/can-ho-dang-ban.html` — quỹ căn giao dịch thực tế.
- `/cam-nang.html` — hub kiến thức mua/chuyển nhượng.
- `/ky-gui-ban-can.html` — ý định chủ nhà muốn bán.

### 2. Cluster dự án / phân khu

Mỗi trang dự án phải trả lời tối thiểu: vị trí trong đại đô thị, nhóm tòa, sản phẩm, diện tích phổ biến, tiêu chuẩn bàn giao, tiện ích gần, khoảng giá từ dữ liệu quỹ căn, điểm mạnh/yếu, link tới căn đang bán.

Các URL lõi hiện có:

- `/phan-khu-sapphire.html`
- `/phan-khu-the-sakura.html`
- `/masteri-west-heights-smart-city.html`
- `/lumiere-evergreen-smart-city.html`
- `/the-canopy-residences-smart-city.html`
- `/the-miami-smart-city.html`
- `/the-tonkin-smart-city.html`
- `/imperia-smart-city.html`
- `/the-sola-park-smart-city.html`
- `/the-victoria-smart-city.html`
- `/gateway-tower.html`

### 3. Cluster từng tòa — ưu tiên V2/V3

Mẫu URL đề xuất:

- `/toa-s401-vinhomes-smart-city/`
- `/toa-s203-vinhomes-smart-city/`
- `/toa-g1-sola-park-smart-city/`
- `/toa-v1-the-victoria-smart-city/`
- `/toa-masteri-a-west-heights/`
- `/toa-masteri-b-west-heights/`
- `/toa-masteri-c-west-heights/`
- `/toa-masteri-d-west-heights/`

Không tạo hàng loạt trang mỏng. Chỉ publish khi có đủ dữ liệu: mô tả tòa, mặt bằng/tầng điển hình hoặc layout, ảnh local, quỹ căn liên quan và internal link.

### 4. Cluster mặt bằng / layout

Đây là nhóm truy vấn evergreen giống chiến lược đang dùng ở Lumi Hanoi.

Mẫu:

- `/mat-bang-vinhomes-smart-city/` — hub.
- `/mat-bang-masteri-west-heights/`
- `/mat-bang-the-sakura-smart-city/`
- `/mat-bang-sapphire-smart-city/`
- `/mat-bang-toa-s401-vinhomes-smart-city/`

Mỗi trang cần ảnh mặt bằng thật, chú giải căn, hướng, diện tích và link quỹ căn đúng tòa/loại.

### 5. Cluster loại căn

Ý định tìm kiếm theo công năng:

- Studio
- 1PN
- 1PN+
- 2PN
- 2PN+
- 3PN

Các landing hiện có cần được hợp nhất tránh trùng intent giữa `mua-can-ho-*` và `ban-can-ho-*`. Chọn một URL canonical chính cho từng intent.

### 6. Cluster ngân sách

Tạo từ dữ liệu thực tế, không viết giá ảo:

- căn dưới 3 tỷ
- căn 3–4 tỷ
- căn 4–5 tỷ
- căn 5–7 tỷ
- căn trên 7 tỷ

Landing phải có thống kê build-time và danh sách căn thực, không chỉ text SEO.

### 7. Cluster quyết định mua

Ưu tiên các bài có khả năng tạo lead và internal link mạnh:

- nên mua phân khu nào tại Smart City
- so sánh Sapphire / Sakura / Masteri / Lumiere / Canopy
- mua để ở hay đầu tư cho thuê
- chọn tầng thấp / trung / cao
- chọn hướng ban công và view
- căn có sổ và HĐMB khác nhau thế nào khi chuyển nhượng
- thuế phí, công chứng, quy trình cọc
- checklist kiểm tra căn trước đặt cọc
- vay ngân hàng mua căn chuyển nhượng

## Chuẩn trang dự án V2

Mỗi trang dự án mới hoặc nâng cấp cần có:

1. Hero ảnh local WebP + H1 đúng intent.
2. Quick facts có nguồn hoặc ghi rõ dữ liệu tham khảo.
3. Bản đồ vị trí trong đại đô thị hoặc mô tả vị trí rõ ràng.
4. Danh sách tòa.
5. Mặt bằng / loại căn.
6. Gallery ảnh thực hoặc ảnh tài liệu có nguồn.
7. Market snapshot lấy từ `data.json` theo phân khu.
8. Quỹ căn đang bán lọc sẵn.
9. Ưu / nhược điểm cho người mua.
10. FAQ + schema phù hợp.
11. Breadcrumb + canonical + OG image.
12. Internal links tới hub, trang tòa, mặt bằng, giá và quỹ căn.

## Ảnh

Quy tắc V2:

- Ưu tiên ảnh chính thức/tài liệu chủ đầu tư, ảnh thực tế tự có hoặc nguồn được phép sử dụng.
- Không hotlink ảnh môi giới bên thứ ba.
- Lưu local WebP, tên file mô tả đúng đối tượng.
- Mỗi dự án có thư mục riêng trong `images/projects/<slug>/`.
- Mỗi ảnh có alt theo nội dung thật, không nhồi từ khóa.
- `IMAGE_SOURCES.md` hoặc file nguồn riêng theo dự án phải ghi URL nguồn và ngày truy cập.

## Internal linking

Mọi trang phải dẫn theo luồng:

`Đô thị -> Dự án/phân khu -> Tòa/mặt bằng/loại căn -> Quỹ căn -> Liên hệ`

Và đường ngược lại từ quỹ căn phải cho người mua quay về trang phân khu để hiểu sản phẩm trước khi hỏi căn.

## Ưu tiên triển khai

### V1 — nền móng

- Rebuild UX quỹ căn: lọc, sort, lưu, so sánh.
- Chuẩn hóa navigation và footer internal links.
- Chốt kiến trúc SEO để tránh tạo URL trùng intent.

### V2 — data + project depth

- Nâng 6 trang dự án có quỹ căn lớn nhất.
- Tạo market snapshot build-time theo từng phân khu.
- Chuẩn hóa ảnh local và gallery.
- Hợp nhất landing loại căn/ngân sách bị trùng intent.

### V3 — tower & floorplan moat

- Tạo hub mặt bằng.
- Tạo từng tòa khi đủ dữ liệu.
- Gắn mặt bằng, layout và quỹ căn theo đúng tòa.

### V4 — conversion

- Form yêu cầu tìm căn theo ngân sách.
- Saved shortlist có CTA gửi danh sách qua Zalo.
- Lead source tracking.
- CTA ký gửi theo trang phân khu/tòa.
