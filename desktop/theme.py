"""Design system — PeopleRisk AI Desktop (mockup-aligned)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    brand: str = "#0B3A4A"
    brand_deep: str = "#072A36"
    brand_soft: str = "#123F4F"
    accent: str = "#1F8A70"
    accent_hover: str = "#18725C"
    accent_soft: str = "#E6F5F0"
    bg: str = "#F4F7F9"
    surface: str = "#FFFFFF"
    surface_alt: str = "#EEF2F5"
    border: str = "#D5DEE5"
    sidebar_text: str = "#D5E4EA"
    sidebar_muted: str = "#8FA9B4"
    text: str = "#1A2B34"
    text_secondary: str = "#5B6E78"
    text_muted: str = "#84949C"
    danger: str = "#C0392B"
    danger_soft: str = "#FDECEA"
    warning: str = "#B9770E"
    warning_soft: str = "#FEF5E7"
    success: str = "#1E8449"
    success_soft: str = "#E8F8F0"
    info: str = "#2471A3"
    info_soft: str = "#EAF4FB"
    font_family: str = "Noto Sans"
    font_fallback: str = "DejaVu Sans"


THEME = Theme()

NAV_SECTIONS = [
    (
        "OVERVIEW",
        [("dashboard", "Tổng quan", "Bức tranh nhân sự & rủi ro nghỉ việc")],
    ),
    (
        "DATA",
        [
            ("data", "Dữ liệu", "Từ điển cột, kiểu dữ liệu, mẫu bản ghi"),
            ("upload", "Nhập Dataset", "Tải CSV mới và chọn biến mục tiêu"),
            ("quality", "Chất lượng dữ liệu", "Missing, trùng lặp, outlier, làm sạch"),
        ],
    ),
    (
        "ANALYTICS",
        [
            ("eda", "Phân tích EDA", "Thống kê mô tả và mối quan hệ với nghỉ việc"),
            ("viz", "Trực quan hóa", "Thư viện biểu đồ có chú thích"),
        ],
    ),
    (
        "AI / ML",
        [
            ("model", "Mô hình AI", "Phân loại nghỉ việc & hồi quy thu nhập"),
            ("predict", "Dự báo rủi ro", "Chấm điểm nguy cơ nghỉ việc theo hồ sơ"),
        ],
    ),
    (
        "RESULTS",
        [
            ("insights", "Insights", "Phát hiện từ dữ liệu hiện tại"),
            ("recs", "Khuyến nghị", "Hành động đề xuất cho HR"),
        ],
    ),
]

FILTER_ROLE_LABELS = {
    "department": "Phòng ban",
    "location": "Địa điểm",
    "gender": "Giới tính",
    "overtime": "Làm thêm giờ",
    "contract": "Hợp đồng",
    "job_level": "Cấp bậc",
}
