# Kiến trúc kỹ thuật — Tìm Mua Smart City

_Cập nhật: 2026-08-12. Phạm vi: refactor build/SEO, không redesign và không thay đổi domain._

## 1. Kết luận audit

Website là static site triển khai trên GitHub Pages, domain duy nhất là
`https://timmuasmartcity.com` (được khóa bởi `CNAME`). `data.json` là quỹ căn nguồn và
được giữ nguyên. Trước refactor có hai họ URL cùng phục vụ toàn bộ nội dung:

| Nhóm | Nguồn cũ | Bản sinh cũ | URL canonical được giữ |
|---|---|---|---|
| Cẩm nang | `blog/**/index.html` | các bài `.html` ở root | `/<slug>.html`; hub là `/cam-nang.html` |
| Quỹ căn | `can-ho-dang-ban/index.html` | `can-ho-dang-ban.html` | `/can-ho-dang-ban.html` |
| Phân khu | `phan-khu/**/index.html` | các trang `phan-khu*.html`, `gateway-tower.html` | URL `.html` tương ứng |
| Landing theo inventory | `data.json` + `tools/build_static_sale_landings.py` | `ban-*.html` | URL `.html` của chính trang |
| Trang độc lập | HTML ở root | không qua copy | URL `.html` của chính trang; homepage là `/` |

Sitemap và phần lớn internal link đã dùng URL phẳng `.html`; vì vậy đây là chuẩn duy
nhất, tránh thay URL đang index và tránh vòng lặp trailing slash của GitHub Pages.
Các directory URL cũ vẫn tồn tại để không làm gãy backlink, nhưng nay chỉ là trang
chuyển tiếp `noindex,follow`, canonical tới `.html` và meta refresh tới cùng đích.
Chúng không có trong sitemap và không được tính là nội dung trùng lặp.

Audit workflow cũ cho thấy `big-update.yml` và `build-flat-routes.yml` đều chạy khi
push `main`, cùng sửa/push `index.html` và các HTML. Commit do bot lại kích hoạt cả hai,
tạo race, vòng chạy bổ sung và khả năng ghi đè. Workflow ảnh cũng tự commit; workflow
asset khóa cứng một branch cũ. Cả bốn đã được thay bằng một pipeline chỉ đọc, không
workflow nào tự ý commit production output nữa.

## 2. Phân loại repository

- **Source:** `_source/` chứa template HTML gốc cho cẩm nang, quỹ căn và phân khu.
  GitHub Pages/Jekyll không publish thư mục bắt đầu bằng `_`. Các HTML root độc lập
  (`index.html`, trang pháp lý, ký gửi và profile dự án độc lập) hiện là source trực tiếp.
- **Generated:** HTML phẳng được liệt kê trong `ROUTES` của
  `tools/build_flat_public_routes.py`, bốn landing `ban-*.html`, `data/public-stats.json`,
  và các compatibility page `blog/**`, `can-ho-dang-ban/`, `phan-khu/**`.
- **Data:** `data.json` (inventory nguồn, tuyệt đối không xóa), `data/official/**` và
  `data/public-stats.json` (derived).
- **Assets:** `assets/**`, `images/**`, favicon, manifest và các ảnh icon.
- **Scripts:** `tools/**`; `build_site.py` là entrypoint production duy nhất.
- **Documentation/content planning:** `docs/**` và `seo/**`.
- **Legacy:** các công cụ normalize/crawl/sync còn lưu trong `tools/` để tham khảo hoặc
  chạy thủ công. Chúng không nằm trong production pipeline; các directory URL công
  khai cũ chỉ là compatibility output.

## 3. Build graph deterministic

```text
_source/**/*.html + root source HTML + data.json
                         |
                 python3 tools/build_site.py
                         |
       flat pages + sale landings + stats + legacy redirects
                         |
              python3 tools/validate_site.py
                         |
              GitHub Pages artifact / deploy
```

Thứ tự build cố định: (1) flat routes và stats, (2) landing từ quỹ căn, (3) redirect
compatibility. Build không gọi mạng, không commit và không push. CI build lại rồi dùng
`git diff --exit-code`; thay đổi output chưa commit sẽ làm job fail. Pull request chỉ
build/validate; push `main` pass mới upload và deploy. `concurrency` hủy deploy cũ cùng
ref, nên không có hai writer.

### Quy trình local

```bash
python3 tools/build_site.py
python3 tools/validate_site.py
git diff --exit-code
```

Khi sửa bài được generate, sửa file tương ứng trong `_source/`, không sửa bản root.
Khi sửa dữ liệu bán, chỉ cập nhật `data.json`, build lại và review generated diff.
Không chạy các script legacy trong CI nếu chưa tích hợp rõ input/output vào
`build_site.py`.

## 4. URL, canonical và redirect policy

- Origin bắt buộc: `https://timmuasmartcity.com`; không dùng `www` hoặc domain khác.
- Homepage canonical `/`; các trang còn lại ưu tiên `.html` như sitemap hiện hữu.
- Internal link mới phải trỏ thẳng canonical, không trỏ compatibility URL.
- Directory alias cũ là bridge an toàn cho GitHub Pages: `noindex,follow`, canonical và
  meta refresh. GitHub Pages không hỗ trợ HTTP 301 theo repo, nên không giả định đây là
  server redirect. Chỉ bỏ alias khi có redirect HTTP được xác minh ở lớp CDN/domain.
- `404.html` là trang lỗi đặc biệt, không index/canonical. `robots.txt` cho crawl site và
  khai báo đúng sitemap. Sitemap chỉ chứa canonical indexable URLs.

## 5. Validation contract

`tools/validate_site.py` dùng Python standard library và trả exit code khác 0 nếu có:

1. link/script/stylesheet/ảnh local bị thiếu (hỗ trợ root-relative, relative, query/hash);
2. canonical thiếu, nhiều hơn một, sai HTTPS hoặc sai domain;
3. nhiều trang indexable dùng cùng canonical;
4. sitemap trùng URL, sai domain, URL không có file, hoặc canonical không khớp;
5. `og:image` cùng domain hoặc ảnh HTML local bị thiếu;
6. `robots.txt` thiếu sitemap chuẩn hoặc `CNAME` thay domain.

Validator bỏ qua `_source/` vì đó không phải public output và cho phép canonical trùng
chỉ ở trang `noindex` compatibility. Ảnh remote ngoài domain không thể kiểm tra ổn định
trong build offline; nên ưu tiên lưu asset cần SEO ở `images/`.

### Public data boundary

Audit runtime hiện tại cho thấy frontend chỉ tải `/data.json`; file này đã là public
inventory contract và được stage ở root. Không có HTML/JS nào tải `data/public-stats.json`:
đây là build output để audit số lượng, không phải runtime dependency. Toàn bộ
`data/official/**` là source/crawl metadata và tuyệt đối không được deploy.
`prepare_deploy.py` vì vậy dùng allowlist `PUBLIC_DATA_FILES` rỗng thay vì copy cả
`data/`. Nếu sau này frontend cần một file dưới `/data/`, file đó phải được review field,
thêm riêng vào allowlist, và validator chạy với `--root _site` sẽ fail cho tới khi runtime
reference thực sự tồn tại trong artifact. Validator staged cũng fail nếu thấy
`data/official/**`.

## 6. Nội dung và asset được bảo toàn

Refactor không xóa `data.json`, không lọc/xóa căn bán, không đổi canonical đã có trong
sitemap, không redesign và không thêm/sửa binary asset. Các tham chiếu editorial từng
trỏ tới bốn file ảnh không tồn tại nay dùng lại hero WebP production đã có sẵn, nên
link và OpenGraph không 404 mà không cần đưa binary mới vào thay đổi kiến trúc này.
