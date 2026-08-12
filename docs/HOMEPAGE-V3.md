# Homepage Portal V3

## Mục tiêu và information architecture

Homepage được thiết kế lại thành **buyer portal**, không phải landing page bán hàng. Luồng đọc đi từ bối cảnh rộng đến hành động cụ thể:

1. Hero visual-first và hai lối vào: tìm căn hoặc nghiên cứu dự án.
2. Smart City at a glance (`#tong-quan`).
3. Câu chuyện đô thị phía Tây Hà Nội.
4. Hồ sơ các phân khu (`#phan-khu`).
5. Tiện ích và lifestyle (`#tien-ich`).
6. Loại căn đang có trong quỹ.
7. Market snapshot build-time.
8. Sáu căn đáng xem.
9. Cẩm nang người mua.
10. CTA ký gửi cho chủ nhà và footer dùng chung của Design System V2.

Các section cũ dạng box đều nhau được thay bằng nhịp editorial: ảnh toàn khung, text/visual bất đối xứng, project mosaic, data band và các dải cuộn ngang trên mobile.

## Nguồn dữ liệu

`tools/build_homepage.py` đọc `data.json` và chỉ nhận record có `Hiển thị trên Web = Có`. Homepage được render trước khi deploy, vì vậy count và metrics vẫn tồn tại nếu JavaScript bị tắt hoặc request runtime thất bại.

- **Live count:** số record được phép hiển thị.
- **Loại căn:** `Counter` trên trường `Loại`; chỉ sáu loại đã duyệt (Studio, 1PN, 1PN+, 2PN, 2PN+, 3PN) và thực sự có dữ liệu mới được render.
- **Median giá chào:** median của `Giá bán` dương trên record có `Diện tích` dương, đổi từ đồng sang tỷ đồng.
- **Median đơn giá:** median của `Giá mỗi m2` dương trên cùng tập dữ liệu hợp lệ, đơn vị triệu đồng/m².
- **Phân khu có nhiều nguồn cung:** tần suất cao nhất của `Phân khu` trong quỹ công khai.
- **Ngày cập nhật:** ngày `Ngày xác nhận chủ` mới nhất, chỉ dùng cho trust indicator.

Các con số 280 ha, mật độ 14,7% và trục Đại lộ Thăng Long là thông tin nền đã có trong hồ sơ dự án của repository. Disclaimer được đặt ngay cạnh market metrics vì dữ liệu cần xác nhận lại trước giao dịch.

## Quy tắc chọn featured inventory

Ứng viên phải đồng thời:

- được phép hiển thị;
- có URL hợp lệ trong field public `Ảnh đại diện`;
- có giá bán dương;
- có diện tích dương.

Ứng viên được xếp hạng cố định theo độ đầy đủ của tập trường công khai, rồi `Phân khu`, `Tòa`, `Loại` theo alphabet. Bộ chọn lấy căn xếp hạng cao nhất của từng phân khu; nếu có ít hơn sáu phân khu đủ điều kiện, bộ chọn tiếp tục lấy các căn tốt nhất còn lại thay vì giảm số card hoặc tạo visual giả.

Renderer tạo một dictionary whitelist gồm đúng: `Tòa`, `Phân khu`, `Loại`, `Diện tích`, `Tầng`, `Nội thất`, `Giá bán`, `Giá mỗi m2`. Giá thu về/net, phí, commission, ghi chú, ID và các trường nội bộ không thể đi vào HTML generated. Ảnh được đọc riêng từ field public `Ảnh đại diện`: helper chỉ chấp nhận HTTPS thumbnail của đúng host/path Drive đã duyệt, bỏ toàn bộ query option ngoài ID và tuyệt đối không đọc `Danh sách ảnh`. Mỗi card render ảnh căn thật và rơi về ảnh local nếu endpoint public lỗi. CTA truyền `?q=` cho trang inventory, trang này khởi tạo ô tìm kiếm từ query string.

## Image strategy và fallback

Repository hiện chỉ có một bộ ảnh Smart City thật ở `images/hero/` với desktop/mobile WebP và JPG. V3 dùng:

- WebP desktop/mobile trong `<picture>` cho hero, với `fetchpriority="high"`, kích thước rõ và không lazy-load.
- Mobile WebP cho visual dọc của câu chuyện đô thị.
- Project LUMIÈRE và lifestyle dùng typography/color composition, tương tự các project chưa có ảnh riêng, thay vì tái sử dụng hero làm ảnh giả.
- Featured inventory dùng đúng public representative thumbnail của từng căn, được sanitizer fail-closed như mô tả trên.

Ảnh bên dưới fold có `loading="lazy"`. Không dùng stock và không gắn một ảnh chung thành ảnh giả của từng phân khu/căn. Ảnh nội dung dự án đều là local; riêng ảnh căn là public inventory thumbnail đã được duyệt và có fallback local. Khi repository có pipeline mirror ảnh căn, URL public có thể được thay bằng bản local mà không đổi cấu trúc card.

## Internal linking

Mọi liên kết dùng flat canonical route đã kiểm tra trong repository: `/phan-khu.html`, `/lumiere-evergreen-smart-city.html`, `/phan-khu-sapphire.html`, `/phan-khu-the-sakura.html`, `/gateway-tower.html`, `/masteri-west-heights-smart-city.html`, `/gia-ban-vinhomes-smart-city.html`, `/cam-nang.html`, `/can-ho-dang-ban.html`, các bài buyer guide và `/ky-gui-ban-can.html`. CTA ký gửi chính luôn là page nội bộ; Zalo chỉ là lựa chọn phụ.

## SEO

Homepage có title/description bám search intent mua bán, căn hộ và bảng giá; canonical domain gốc; Open Graph URL/title/description/image local; kích thước OG image; Twitter large card. WebSite schema và SearchAction được giữ lại. Không có review/rating giả hoặc keyword stuffing.

## Performance, accessibility và mobile

- Chỉ HTML/CSS/vanilla JS; không slider library, video hay runtime fetch trên homepage.
- Hero có intrinsic dimensions, responsive source và overlay CSS; dưới fold lazy-load.
- Reuse token, button, focus state, header/footer từ `design-system.css` và shell từ `app-shell.js`.
- Một H1; hierarchy H2/H3 tuần tự; ảnh có alt; CTA là link semantic; focus state và reduced-motion do Design System V2 cung cấp.
- Ở mobile hero được giới hạn theo viewport; project và listing dùng native horizontal scroll + scroll snap; stats/type/market chuyển thành hai cột; CTA đủ vùng chạm.
- Breakpoint desktop/tablet/mobile tránh fixed-width content và horizontal overflow toàn trang; chỉ hai rail có chủ đích được cuộn ngang.

## Determinism và build

`tools/build_site.py` gọi `build_homepage.py` sau khi build flat routes. Template nằm tại `_source/homepage.html`; artifact là `index.html`. Sorting có tie-breaker ổn định, không dùng timestamp build và không random. Hai lần build với cùng `data.json` tạo byte-identical homepage.

`tools/validate_homepage.py` chạy ngay sau generator và fail build nếu còn token, thiếu local asset, không đủ sáu ảnh căn thật, public image sai host/path, thiếu fallback/alt hoặc featured markup chứa tên field nhạy cảm.
