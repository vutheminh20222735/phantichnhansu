"""Sinh khuyến nghị HR gắn với Insight thực tế."""

from __future__ import annotations

from typing import Any


def _rec_for_insight(insight: dict[str, Any]) -> str | None:
    group = insight.get("group", "")
    metrics = insight.get("metrics", {})

    if group == "Overtime":
        diff = abs(float(metrics.get("diff", 0)))
        if diff < 1:
            return (
                "Chênh lệch OT nhỏ trong mẫu hiện tại — tiếp tục theo dõi khối lượng "
                "làm thêm theo phòng ban trước khi can thiệp lớn."
            )
        return (
            "Khuyến nghị HR theo dõi khối lượng làm thêm giờ, rà soát phân bổ workload "
            "và chính sách OT — đặc biệt với nhóm có tỷ lệ nghỉ việc cao hơn."
        )

    if group == "Job Satisfaction":
        return (
            "Ưu tiên khảo sát và cải thiện trải nghiệm công việc cho nhóm có điểm "
            "hài lòng thấp; gắn KPI giữ chân với kế hoạch cải thiện engagement."
        )

    if group == "Monthly Income":
        return (
            "Rà soát khung lương/thưởng theo vị trí và benchmark thị trường; "
            "kiểm tra nhóm có thu nhập thấp hơn mặt bằng nhưng cùng cấp bậc."
        )

    if group == "Years at Company":
        return (
            "Thiết kế chương trình onboarding và giữ chân giai đoạn đầu "
            "(0–2 năm) nếu nhóm nghỉ việc có thâm niên thấp hơn."
        )

    if group == "Department / Job Role":
        return (
            "Làm sâu phân tích theo phòng ban/vị trí nổi bật: exit interview, "
            "workload, quản lý trực tiếp và cơ hội thăng tiến."
        )

    if group == "Distance From Home":
        return (
            "Xem xét chính sách làm việc linh hoạt/hybrid hoặc hỗ trợ đi lại "
            "cho nhóm có khoảng cách lớn nếu xu hướng nghỉ việc cao hơn."
        )

    if group == "Work-Life Balance":
        return (
            "Đánh giá lại lịch làm việc, kỳ vọng OT và hỗ trợ cân bằng "
            "công việc–cuộc sống cho nhóm điểm thấp."
        )

    if group == "Relationship Satisfaction":
        return (
            "Đầu tư kỹ năng quản lý và quan hệ đồng nghiệp; "
            "theo dõi xung đột/feedback 360 ở các nhóm điểm thấp."
        )

    if group == "Performance Rating":
        return (
            "Đối chiếu đánh giá hiệu suất với kế hoạch phát triển nghề nghiệp "
            "để tránh mất nhân sự có/không đạt kỳ vọng vì lý do khác."
        )

    if group == "Training":
        return (
            "Rà soát tiếp cận đào tạo: đảm bảo nhân viên nhận đủ cơ hội học "
            "và lộ trình phát triển rõ ràng."
        )

    if group == "Overview":
        return (
            "Thiết lập dashboard theo dõi attrition định kỳ và cảnh báo sớm "
            "theo phòng ban/nhóm rủi ro cao."
        )

    return None


def generate_recommendations(insights: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Tạo recommendation gắn trực tiếp với từng insight."""
    recs: list[dict[str, str]] = []
    for ins in insights:
        text = _rec_for_insight(ins)
        if not text:
            continue
        recs.append(
            {
                "based_on": ins.get("title", ins.get("group", "")),
                "group": ins.get("group", ""),
                "recommendation": text,
                "linked_insight": ins.get("insight", ""),
            }
        )
    return recs
