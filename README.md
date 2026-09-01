# smartcity-sale

Website mua bán căn hộ tại Vinhomes Smart City.

## Big update 12/08/2026

- Chuẩn hóa dữ liệu theo mảng **mua bán**.
- Loại bỏ cách gọi nhầm trường giá bán là `Giá thuê` trong nguồn dữ liệu.
- Tự kiểm tra các giá/m² bất thường và các giá bao phí không hợp lý.
- Loại bỏ nội dung/form dành cho khách thuê khỏi trang bán.
- Cập nhật thông tin địa chỉ theo đơn vị hành chính hiện hành của Hà Nội.

## Marketplace / Supabase

Marketplace dùng project Supabase `smartcity-marketplace` và các bảng chính:

- `listings`: tin mua bán / cho thuê.
- `listing_images`: metadata ảnh theo từng tin.
- `listing_reports`: báo cáo tin sai / đã giao dịch.
- `admin_users`: danh sách Supabase Auth user được quyền quản trị.
- Storage bucket: `listing-images`.

### Luồng đăng tin

1. Người dùng gửi form tại `/dang-tin-smart-city/`.
2. Trình duyệt tạo bản ghi `pending` qua Supabase Data API.
3. Ảnh được tải lên `listing-images/pending/<listing-id>/...`.
4. Tin chỉ xuất hiện công khai khi admin chuyển trạng thái sang `approved`.
5. Tin hết hạn / đã bán / đã thuê sẽ không còn nằm trong danh sách public.

RLS giới hạn anonymous user chỉ được:

- tạo tin ở trạng thái `pending`;
- đọc tin `approved`, còn hạn và cho phép công khai liên hệ;
- tải ảnh vào đúng thư mục `pending/<listing-id>/`;
- báo cáo một tin đang hiển thị.

Không có secret/service-role key nào được đưa vào frontend.

### Trang admin

Trang quản trị: `/admin/`

Chức năng hiện có:

- đăng nhập Supabase Auth;
- xem KPI chờ duyệt / đang hiển thị / đã giao dịch / báo cáo;
- tìm kiếm và lọc tin;
- xem, sửa nội dung;
- duyệt / từ chối;
- ghim / bỏ ghim;
- đánh dấu đã bán / đã thuê;
- gia hạn 45 ngày;
- xóa vĩnh viễn tin và ảnh đính kèm.

### Cấp admin đầu tiên

1. Tạo user trong **Supabase → Authentication → Users**.
2. Chạy SQL:

```sql
insert into public.admin_users (user_id)
select id
from auth.users
where email = 'ADMIN_EMAIL'
on conflict (user_id) do nothing;
```

Sau đó user đó có thể đăng nhập tại `/admin/`.

### Patch quyền Data API

Patch đang dùng được lưu tại:

`supabase/marketplace-access-20260901.sql`

Patch này cũng mở rộng `unit_type` cho các loại căn Smart City mới như `1PN+1`, `2PN+1`, `2PN+1 (1WC)`, `2PN+1 (2WC)`, `3PN+1`.
