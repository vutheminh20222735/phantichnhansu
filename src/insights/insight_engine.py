"""Sinh Insight tự động từ dataset thực tế."""

from __future__ import annotations

from typing import Any

import pandas as pd

from src.analysis.eda import attrition_rate_by_group
from src.utils import TARGET_COL, attrition_mask, attrition_rate, format_pct, format_vnd


def _income_insight(df: pd.DataFrame) -> dict[str, Any] | None:
    if "ThuNhapHangThang_VND" not in df.columns:
        return None
    leave = df.loc[attrition_mask(df[TARGET_COL]), "ThuNhapHangThang_VND"]
    stay = df.loc[~attrition_mask(df[TARGET_COL]), "ThuNhapHangThang_VND"]
    if leave.empty or stay.empty:
        return None
    leave_mean, stay_mean = float(leave.mean()), float(stay.mean())
    diff = stay_mean - leave_mean
    direction = "thấp hơn" if leave_mean < stay_mean else "cao hơn"
    return {
        "group": "Monthly Income",
        "title": "Thu nhập và tình trạng nghỉ việc",
        "insight": (
            f"Thu nhập trung bình nhóm nghỉ việc là {format_vnd(leave_mean)}, "
            f"{direction} nhóm ở lại ({format_vnd(stay_mean)}). "
            f"Chênh lệch tuyệt đối khoảng {format_vnd(abs(diff))}."
        ),
        "metrics": {
            "leave_mean": leave_mean,
            "stay_mean": stay_mean,
            "diff": diff,
        },
        "supported": True,
    }


def _overtime_insight(df: pd.DataFrame) -> dict[str, Any] | None:
    table = attrition_rate_by_group(df, "LamThemGio")
    if table.empty or not set(table["LamThemGio"]).issuperset({"Có", "Không"}):
        return None
    rate_yes = float(table.loc[table["LamThemGio"] == "Có", "attrition_rate"].iloc[0])
    rate_no = float(table.loc[table["LamThemGio"] == "Không", "attrition_rate"].iloc[0])
    diff = rate_yes - rate_no
    return {
        "group": "Overtime",
        "title": "Làm thêm giờ và tỷ lệ nghỉ việc",
        "insight": (
            f"Nhóm nhân viên làm thêm giờ có tỷ lệ nghỉ việc {format_pct(rate_yes)}, "
            f"trong khi nhóm không làm thêm giờ là {format_pct(rate_no)}. "
            f"Chênh lệch là {diff:+.2f} điểm phần trăm."
        ),
        "metrics": {"rate_yes": rate_yes, "rate_no": rate_no, "diff": diff},
        "supported": abs(diff) >= 0,  # luôn có số liệu; recommendation sẽ xét ngưỡng
    }


def _satisfaction_insight(df: pd.DataFrame) -> dict[str, Any] | None:
    if "HaiLong_CongViec" not in df.columns:
        return None
    table = attrition_rate_by_group(df, "HaiLong_CongViec").sort_values("HaiLong_CongViec")
    if len(table) < 2:
        return None
    low = table.iloc[0]
    high = table.iloc[-1]
    return {
        "group": "Job Satisfaction",
        "title": "Hài lòng công việc và nghỉ việc",
        "insight": (
            f"Ở mức hài lòng công việc {low['HaiLong_CongViec']}, "
            f"tỷ lệ nghỉ việc là {format_pct(low['attrition_rate'])}; "
            f"ở mức {high['HaiLong_CongViec']} là {format_pct(high['attrition_rate'])}. "
            f"Chênh lệch {float(low['attrition_rate']) - float(high['attrition_rate']):+.2f} điểm phần trăm."
        ),
        "metrics": {
            "low_level": float(low["HaiLong_CongViec"]),
            "low_rate": float(low["attrition_rate"]),
            "high_level": float(high["HaiLong_CongViec"]),
            "high_rate": float(high["attrition_rate"]),
        },
        "supported": True,
    }


def _tenure_insight(df: pd.DataFrame) -> dict[str, Any] | None:
    if "SoNamTaiCongTy" not in df.columns:
        return None
    leave = df.loc[attrition_mask(df[TARGET_COL]), "SoNamTaiCongTy"]
    stay = df.loc[~attrition_mask(df[TARGET_COL]), "SoNamTaiCongTy"]
    if leave.empty or stay.empty:
        return None
    return {
        "group": "Years at Company",
        "title": "Thâm niên tại công ty",
        "insight": (
            f"Nhóm nghỉ việc có số năm tại công ty trung bình {leave.mean():.2f} năm "
            f"(median {leave.median():.2f}), trong khi nhóm ở lại là "
            f"{stay.mean():.2f} năm (median {stay.median():.2f})."
        ),
        "metrics": {
            "leave_mean": float(leave.mean()),
            "stay_mean": float(stay.mean()),
        },
        "supported": True,
    }


def _department_insight(df: pd.DataFrame) -> dict[str, Any] | None:
    table = attrition_rate_by_group(df, "PhongBan")
    if table.empty:
        return None
    top = table.iloc[0]
    overall = attrition_rate(df)
    return {
        "group": "Department / Job Role",
        "title": "Phòng ban có tỷ lệ nghỉ việc nổi bật",
        "insight": (
            f"Phòng ban `{top['PhongBan']}` có tỷ lệ nghỉ việc "
            f"{format_pct(top['attrition_rate'])} "
            f"({int(top['leaving'])}/{int(top['total'])}), "
            f"cao hơn mức chung của dataset ({format_pct(overall)}) "
            f"{float(top['attrition_rate']) - overall:+.2f} điểm phần trăm."
        ),
        "metrics": {
            "department": top["PhongBan"],
            "rate": float(top["attrition_rate"]),
            "overall": overall,
        },
        "supported": True,
    }


def _job_role_insight(df: pd.DataFrame) -> dict[str, Any] | None:
    table = attrition_rate_by_group(df, "ViTriCongViec")
    if table.empty or len(table) < 2:
        return None
    # Chỉ xét nhóm đủ mẫu (>= 20) để tránh kết luận nhiễu
    solid = table[table["total"] >= 20]
    if solid.empty:
        solid = table
    top = solid.iloc[0]
    return {
        "group": "Department / Job Role",
        "title": "Vị trí công việc có tỷ lệ nghỉ việc cao",
        "insight": (
            f"Vị trí `{top['ViTriCongViec']}` có tỷ lệ nghỉ việc "
            f"{format_pct(top['attrition_rate'])} "
            f"trên {int(top['total'])} nhân viên (ngưỡng mẫu tối thiểu đã áp dụng nếu đủ)."
        ),
        "metrics": {
            "role": top["ViTriCongViec"],
            "rate": float(top["attrition_rate"]),
            "total": int(top["total"]),
        },
        "supported": True,
    }


def _distance_insight(df: pd.DataFrame) -> dict[str, Any] | None:
    if "KhoangCachNha_Km" not in df.columns:
        return None
    leave = df.loc[attrition_mask(df[TARGET_COL]), "KhoangCachNha_Km"]
    stay = df.loc[~attrition_mask(df[TARGET_COL]), "KhoangCachNha_Km"]
    if leave.empty or stay.empty:
        return None
    return {
        "group": "Distance From Home",
        "title": "Khoảng cách nhà – nơi làm việc",
        "insight": (
            f"Khoảng cách trung bình nhóm nghỉ việc là {leave.mean():.2f} km, "
            f"nhóm ở lại là {stay.mean():.2f} km "
            f"(chênh lệch {leave.mean() - stay.mean():+.2f} km)."
        ),
        "metrics": {
            "leave_mean": float(leave.mean()),
            "stay_mean": float(stay.mean()),
        },
        "supported": True,
    }


def _wlb_insight(df: pd.DataFrame) -> dict[str, Any] | None:
    if "CanBangCongViec_CuocSong" not in df.columns:
        return None
    table = attrition_rate_by_group(df, "CanBangCongViec_CuocSong").sort_values(
        "CanBangCongViec_CuocSong"
    )
    if len(table) < 2:
        return None
    low, high = table.iloc[0], table.iloc[-1]
    return {
        "group": "Work-Life Balance",
        "title": "Cân bằng công việc – cuộc sống",
        "insight": (
            f"Mức cân bằng {low['CanBangCongViec_CuocSong']}: tỷ lệ nghỉ việc "
            f"{format_pct(low['attrition_rate'])}; "
            f"mức {high['CanBangCongViec_CuocSong']}: "
            f"{format_pct(high['attrition_rate'])}."
        ),
        "metrics": {
            "low_rate": float(low["attrition_rate"]),
            "high_rate": float(high["attrition_rate"]),
        },
        "supported": True,
    }


def _relationship_insight(df: pd.DataFrame) -> dict[str, Any] | None:
    if "HaiLong_QuanHe" not in df.columns:
        return None
    table = attrition_rate_by_group(df, "HaiLong_QuanHe").sort_values("HaiLong_QuanHe")
    if len(table) < 2:
        return None
    low, high = table.iloc[0], table.iloc[-1]
    return {
        "group": "Relationship Satisfaction",
        "title": "Hài lòng quan hệ tại nơi làm việc",
        "insight": (
            f"Mức hài lòng quan hệ {low['HaiLong_QuanHe']}: "
            f"{format_pct(low['attrition_rate'])}; "
            f"mức {high['HaiLong_QuanHe']}: {format_pct(high['attrition_rate'])}."
        ),
        "metrics": {
            "low_rate": float(low["attrition_rate"]),
            "high_rate": float(high["attrition_rate"]),
        },
        "supported": True,
    }


def _performance_insight(df: pd.DataFrame) -> dict[str, Any] | None:
    if "DanhGiaHieuSuat" not in df.columns:
        return None
    leave = df.loc[attrition_mask(df[TARGET_COL]), "DanhGiaHieuSuat"].mean()
    stay = df.loc[~attrition_mask(df[TARGET_COL]), "DanhGiaHieuSuat"].mean()
    return {
        "group": "Performance Rating",
        "title": "Đánh giá hiệu suất",
        "insight": (
            f"Điểm hiệu suất trung bình nhóm nghỉ việc: {leave:.2f}; "
            f"nhóm ở lại: {stay:.2f}."
        ),
        "metrics": {"leave_mean": float(leave), "stay_mean": float(stay)},
        "supported": True,
    }


def _training_insight(df: pd.DataFrame) -> dict[str, Any] | None:
    if "SoLanDaoTao_Nam" not in df.columns:
        return None
    leave = df.loc[attrition_mask(df[TARGET_COL]), "SoLanDaoTao_Nam"].mean()
    stay = df.loc[~attrition_mask(df[TARGET_COL]), "SoLanDaoTao_Nam"].mean()
    return {
        "group": "Training",
        "title": "Đào tạo trong năm",
        "insight": (
            f"Số lần đào tạo/năm trung bình — nghỉ việc: {leave:.2f}; "
            f"ở lại: {stay:.2f}."
        ),
        "metrics": {"leave_mean": float(leave), "stay_mean": float(stay)},
        "supported": True,
    }


def generate_insights(df: pd.DataFrame, min_count: int = 5) -> list[dict[str, Any]]:
    """Sinh tối thiểu các nhóm insight từ dữ liệu thực tế.

    Không hard-code số liệu. Nếu không đủ bằng chứng thì bỏ qua.
    """
    if df.empty or TARGET_COL not in df.columns:
        return []

    generators = [
        _overtime_insight,
        _satisfaction_insight,
        _income_insight,
        _tenure_insight,
        _department_insight,
        _job_role_insight,
        _distance_insight,
        _wlb_insight,
        _relationship_insight,
        _performance_insight,
        _training_insight,
    ]

    insights: list[dict[str, Any]] = []
    for gen in generators:
        item = gen(df)
        if item and item.get("supported"):
            insights.append(item)

    # Đảm bảo có overall context
    overall = attrition_rate(df)
    insights.insert(
        0,
        {
            "group": "Overview",
            "title": "Tỷ lệ nghỉ việc tổng thể",
            "insight": (
                f"Trên {len(df)} nhân viên đang xét, tỷ lệ nghỉ việc là "
                f"{format_pct(overall)} "
                f"({int(attrition_mask(df[TARGET_COL]).sum())} người)."
            ),
            "metrics": {"attrition_rate": overall, "n": len(df)},
            "supported": True,
        },
    )

    return insights[: max(min_count + 1, len(insights))]
