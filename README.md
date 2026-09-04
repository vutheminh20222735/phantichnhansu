# PeopleRisk AI — HR Analytics Desktop

Ứng dụng desktop hỗ trợ HR phân tích nhân sự, phát hiện yếu tố liên quan nghỉ việc, dự báo rủi ro và đưa khuyến nghị hành động — dựa trên dữ liệu thật đang nạp vào hệ thống.

## Chạy ứng dụng

```bash
cd hr_analytics
pip install -r requirements.txt
./run_desktop.sh
```

## Chức năng chính

| Nhóm | Màn hình | Việc làm được |
|------|----------|----------------|
| Tổng quan | Dashboard | KPI headcount, tỷ lệ nghỉ việc, tín hiệu rủi ro |
| Dữ liệu | Dữ liệu / Nhập Dataset / Chất lượng | Xem dictionary, upload CSV, kiểm tra & làm sạch |
| Phân tích | EDA / Trực quan hóa | Thống kê, quan hệ biến, thư viện biểu đồ có chú thích |
| AI | Mô hình / Dự báo | Train classification + hồi quy thu nhập; chấm điểm hồ sơ |
| Kết quả | Insights / Khuyến nghị | Phát hiện từ dữ liệu + đề xuất cho HR |

## Dataset

- Mặc định: `data/raw/dataset_nhan_su.csv`
- Có thể upload CSV khác và chọn cột target (ví dụ `NghiViec`)
- Đổi dataset → KPI, chart, insight tính lại; model cũ được clear

## Gợi ý dùng thực tế

1. Nạp dữ liệu nhân sự (CSV) và xác nhận cột nghỉ việc.
2. Kiểm tra chất lượng → làm sạch nếu cần.
3. Lọc theo phòng ban / địa điểm trên Dashboard & EDA.
4. Train mô hình → dùng **Dự báo rủi ro** cho từng nhân sự.
5. Xem **Insights** và **Khuyến nghị** để lên kế hoạch giữ chân.
