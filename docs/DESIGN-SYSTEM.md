# Tìm Mua Smart City — Design System V2

## Theme toàn site 2026-09-02

`assets/css/site-theme.css` là lớp giao diện cuối cùng, phát triển từ ngôn ngữ thiết kế
của trang `/dang-tin-smart-city/`: font sans đậm, xanh đậm `#0e211c`, xanh thương hiệu
`#0b6b57`, điểm nhấn xanh dương `#1588df`, nền `#f5f8f6`, card bo tròn và CTA gradient.
Lớp này tải sau các stylesheet cũ để toàn bộ route dùng chung một diện mạo mà không đổi
markup, dữ liệu, JavaScript hay SEO.

`tools/apply_site_theme.py` gắn stylesheet vào public HTML và source template một cách
idempotent. `tools/prepare_portal_v2.py` lặp lại bảo đảm này trên artifact triển khai;
`tools/build_seo_portal.py` gắn theme cho các trang chi tiết tin được sinh sau staging.

## 1. Mục tiêu và audit V1

Design System V2 là lớp giao diện chung, tải sau `v3.css` hoặc `portal.css`. Cách này giữ nguyên pipeline, URL, dữ liệu và JavaScript inventory trong khi đưa các route cũ về cùng một ngôn ngữ thiết kế.

Audit trước khi triển khai ghi nhận:

- `v3.css` dùng bộ token tiếng Việt/legacy (`--navy`, `--gray`, `--r`, `--sh`), trong khi `portal.css` định nghĩa lại `--ink`, `--brand`, `--radius` với giá trị khác.
- Có ba biến thể header (`.topbar`, `.top`, `.top .nav`), menu desktop không cùng danh mục và nhiều trang không có mobile navigation.
- Footer thiếu trên một số landing page; các footer còn lại khác cấu trúc, link và disclaimer.
- Button tồn tại dưới `.btn`, `.pill-btn`, `.nav-cta`, `.cta a` và style attribute; radius, màu và chiều cao không đồng nhất.
- Card tồn tại dưới `.card`, `.apt`, `.profile-card`, `.story-grid article`, `.card-le`; shadow/radius/hover khác nhau.
- Hero tồn tại dưới `.hero`, `.sub-hero`, `.profile-hero`, `.hero-le`, `.listing-hero`; riêng LUMIÈRE có một stylesheet nội tuyến.
- Article lặp cùng khối inline style trên các bài: width, heading, lead, figure, note và CTA. Breadcrumb dùng thẻ `nav` nhưng không có pattern chung.
- Container dùng `.shell`, `.khung`, `.wrap`, `.le` với width/padding khác nhau. Breakpoint cũ tập trung ở 620/640/760/800/980px và thiếu quy tắc thống nhất.
- Màu đỏ, nền xám, spacing 14–28px, radius và shadow bị hard-code tại nhiều nơi. Một số gradient tối tạo cảm giác landing page thay vì portal editorial.
- Mobile V1 có cả bottom tab bar và desktop nav bị ẩn; hành vi không thống nhất, thiếu focus management và trạng thái `aria-expanded` hoàn chỉnh.

## 2. Tokens

Nguồn chuẩn nằm trong `assets/design-system.css`:

- **Color:** `--color-primary`, `--color-primary-dark`, `--color-accent`, `--color-text`, `--color-text-muted`, `--color-bg`, `--color-surface`, `--color-border`, `--color-dark`.
- **Typography:** `--font-display`, `--font-body`.
- **Spacing:** `--space-xs`, `--space-sm`, `--space-md`, `--space-lg`, `--space-xl`.
- **Shape:** `--radius-sm`, `--radius-md`, `--radius-lg`.
- **Elevation:** `--shadow-sm`, `--shadow-md`, `--shadow-lg`.
- **Layout:** `--container-width`, `--reading-width`, `--header-height`.

Các alias V1 chỉ là cầu tương thích. Code mới phải dùng token V2, không thêm literal màu/spacing lặp lại vào template.

## 3. Typography

- Display và body dùng Be Vietnam Pro với system fallback để không làm chậm render khi webfont lỗi.
- `h1`, `h2`, `h3` dùng `clamp()` và line-height gọn; H1 tối đa 4rem.
- Body mặc định 1rem/1.65. Nội dung bài viết dùng tối đa 760px, paragraph/list 1.85 line-height và không quá 72 ký tự tương đối (`72ch`).
- Caption/figcaption dùng 0.8125rem và màu muted. Không dùng chữ nhỏ hơn cho nội dung quan trọng.

## 4. Components và cách dùng

| Pattern | Class chuẩn | Quy tắc |
| --- | --- | --- |
| Layout | `.container`, `.section`, `.section-heading` | Một container mỗi section; không lồng fixed width. |
| Button | `.button .button-primary`, `.button .button-secondary` | Link khi điều hướng, `button` khi thực hiện action. |
| Card | `.card`, `.property-card`, `.article-card`, `.project-card` | Media có `aspect-ratio` và `object-fit: cover`; cả card chỉ click được khi có một đích duy nhất. |
| Breadcrumb | `.breadcrumb` | Đặt trước title; dùng `nav aria-label="Breadcrumb"`. |
| Hero | `.page-hero`, `.project-hero`, `.article-hero` | Một H1, một lead; project có thể dùng visual full-bleed. |
| Facts | `.stats`, `.stat-item` | Tối đa bốn chỉ số; mobile hai cột. |
| Media | `.gallery`, `figure` + `figcaption` | Alt mô tả nội dung; caption ghi nguồn khi cần. |
| CTA | `.cta-panel` | Một primary action, secondary action tùy chọn; không giả button bằng `div`. |
| Meta | `.badge` | Nội dung ngắn, không dùng cho đoạn văn. |
| Data | `.table-wrapper > table` | Wrapper cho phép cuộn cục bộ trên mobile, không làm body overflow. |
| Editorial | `.article-content`, `.related-content`, `.callout` | Giữ đúng hierarchy H1 → H2 → H3. |

Các class legacy được map trong CSS để trang có thể chuyển dần mà không phá inventory logic.

## 5. Page composition

### Article

`header → breadcrumb → article-hero (title + lead) → hero figure slot → article-content → table/callout → cta-panel → related-content → footer`.

Hero figure là slot sẵn sàng cho media task; không chèn ảnh trang trí không có giá trị nội dung.

### Project profile

`project-hero (visual) → stats/quick facts → overview → location → gallery → amenities → apartment types → buyer notes → inventory CTA → FAQ → related-content`.

Các section có thể chưa có nội dung trên từng profile, nhưng dùng chính các primitive chung thay vì stylesheet riêng.

## 6. Breakpoints và responsive

- **Base/mobile:** 390px và 430px; container gutter 14px mỗi bên, một cột, tap target tối thiểu 44px.
- **560px:** card/project grids chuyển từ một lên nhiều cột khi đủ chỗ.
- **820px:** desktop navigation đổi sang drawer; drawer tối đa 360px, có backdrop, Escape, close-on-link và `aria-expanded`.
- **1050px:** footer/card grids thay đổi mật độ trước desktop.
- QA viewport bắt buộc: 390, 430, 768, 1024, 1366 và 1440px. `html/body` không được scroll ngang; chỉ `.table-wrapper` được scroll cục bộ.

## 7. Accessibility và motion

- Luôn có focus ring tương phản; không xóa outline nếu không có thay thế.
- Header dùng landmark `header/nav`, footer thống nhất, logo có accessible name và về `/`.
- Mobile menu dùng button thật, `aria-controls`, `aria-expanded`, đóng bằng backdrop/Escape/link và khóa body scroll khi mở.
- Màu text/body và primary trên white đạt độ tương phản tốt; muted chỉ dành cho secondary copy.
- Mọi transition/scroll animation bị rút ngắn khi `prefers-reduced-motion: reduce`.

## 8. Migration và inline CSS

`tools/apply_design_system.py` chạy cuối build để gắn stylesheet/script chung và loại các block `<style>` cũ khỏi public output. `404.html` còn một block inline page-specific vì đây là error document độc lập với composition bài viết/project. Các source template V1 vẫn có thể chứa style cũ, nhưng chúng không xuất hiện trong artifact sau build; nên xóa khi template đó được chỉnh nội dung lần tiếp theo.

Không thay đổi `data.json`, canonical, sitemap hay inventory behavior trong Design System V2.
