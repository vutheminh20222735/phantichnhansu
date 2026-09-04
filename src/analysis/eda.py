"""Phân tích khám phá dữ liệu (EDA) theo Research Questions."""

from __future__ import annotations

from typing import Any

import pandas as pd

from src.utils import TARGET_COL, attrition_mask, attrition_rate, format_pct, format_vnd


def attrition_rate_by_group(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    """Attrition Rate = Employees Leaving / Total Employees theo nhóm."""
    if group_col not in df.columns or TARGET_COL not in df.columns or df.empty:
        return pd.DataFrame(columns=[group_col, "total", "leaving", "attrition_rate"])

    leave = attrition_mask(df[TARGET_COL])
    g = (
        df.assign(_leave=leave.astype(int))
        .groupby(group_col, dropna=False)
        .agg(total=("_leave", "size"), leaving=("_leave", "sum"))
        .reset_index()
    )
    g["attrition_rate"] = (g["leaving"] / g["total"] * 100).round(2)
    return g.sort_values("attrition_rate", ascending=False).reset_index(drop=True)


def rq1_attrition_distribution(df: pd.DataFrame) -> dict[str, Any]:
    """RQ1: Tình trạng nghỉ việc phân bố như thế nào?"""
    if TARGET_COL not in df.columns or df.empty:
        return {"table": pd.DataFrame(), "summary": "Không có dữ liệu."}

    vc = df[TARGET_COL].value_counts(dropna=False)
    pct = df[TARGET_COL].value_counts(normalize=True, dropna=False) * 100
    table = pd.DataFrame(
        {
            "NghiViec": vc.index.astype(str),
            "count": vc.values,
            "percentage": [round(float(x), 2) for x in pct.values],
        }
    )
    leave_pct = float(pct.get("Có", 0.0))
    stay_pct = float(pct.get("Không", 0.0))
    summary = (
        f"Trong {len(df)} nhân viên, tỷ lệ nghỉ việc là {format_pct(leave_pct)}, "
        f"tỷ lệ ở lại là {format_pct(stay_pct)}."
    )
    return {"table": table, "summary": summary}


def rq2_attrition_by_department(df: pd.DataFrame) -> dict[str, Any]:
    """RQ2: Phòng ban nào có tỷ lệ nghỉ việc cao?"""
    table = attrition_rate_by_group(df, "PhongBan")
    if table.empty:
        return {"table": table, "summary": "Không đủ dữ liệu phòng ban."}
    top = table.iloc[0]
    summary = (
        f"Phòng ban có tỷ lệ nghỉ việc cao nhất là `{top['PhongBan']}` "
        f"với {format_pct(top['attrition_rate'])} "
        f"({int(top['leaving'])}/{int(top['total'])} nhân viên)."
    )
    return {"table": table, "summary": summary}


def rq3_overtime_attrition(df: pd.DataFrame) -> dict[str, Any]:
    """RQ3: Làm thêm giờ có liên quan đến nghỉ việc không?"""
    table = attrition_rate_by_group(df, "LamThemGio")
    if table.empty:
        return {"table": table, "summary": "Không đủ dữ liệu làm thêm giờ."}

    rate_yes = float(table.loc[table["LamThemGio"] == "Có", "attrition_rate"].mean()) if (
        table["LamThemGio"] == "Có"
    ).any() else None
    rate_no = float(table.loc[table["LamThemGio"] == "Không", "attrition_rate"].mean()) if (
        table["LamThemGio"] == "Không"
    ).any() else None

    if rate_yes is not None and rate_no is not None:
        diff = rate_yes - rate_no
        summary = (
            f"Nhóm làm thêm giờ có tỷ lệ nghỉ việc {format_pct(rate_yes)}, "
            f"nhóm không làm thêm giờ là {format_pct(rate_no)}. "
            f"Chênh lệch {diff:+.2f} điểm phần trăm. "
            "Đây là mối liên hệ quan sát được, không khẳng định quan hệ nhân quả."
        )
    else:
        summary = "Không đủ cả hai nhóm Có/Không để so sánh."

    return {
        "table": table,
        "summary": summary,
        "rate_yes": rate_yes,
        "rate_no": rate_no,
    }


def rq4_job_satisfaction(df: pd.DataFrame) -> dict[str, Any]:
    """RQ4: Mức độ hài lòng công việc và nghỉ việc."""
    table = attrition_rate_by_group(df, "HaiLong_CongViec")
    if table.empty:
        return {"table": table, "summary": "Không đủ dữ liệu hài lòng công việc."}
    low = table.nsmallest(1, "HaiLong_CongViec").iloc[0]
    high = table.nlargest(1, "HaiLong_CongViec").iloc[0]
    summary = (
        f"Ở mức hài lòng thấp nhất ({low['HaiLong_CongViec']}), "
        f"tỷ lệ nghỉ việc là {format_pct(low['attrition_rate'])}; "
        f"ở mức cao nhất ({high['HaiLong_CongViec']}) là "
        f"{format_pct(high['attrition_rate'])}."
    )
    return {"table": table.sort_values("HaiLong_CongViec").reset_index(drop=True), "summary": summary}


def rq5_income_by_attrition(df: pd.DataFrame) -> dict[str, Any]:
    """RQ5: Thu nhập khác biệt giữa nghỉ việc và ở lại."""
    if "ThuNhapHangThang_VND" not in df.columns or TARGET_COL not in df.columns:
        return {"table": pd.DataFrame(), "summary": "Thiếu cột thu nhập hoặc target."}

    tmp = df[[TARGET_COL, "ThuNhapHangThang_VND"]].copy()
    tmp["ThuNhapHangThang_VND"] = pd.to_numeric(tmp["ThuNhapHangThang_VND"], errors="coerce")
    table = (
        tmp.groupby(TARGET_COL)["ThuNhapHangThang_VND"]
        .agg(["count", "mean", "median", "std", "min", "max"])
        .reset_index()
    )
    table["mean"] = table["mean"].round(0)
    table["median"] = table["median"].round(0)

    leave_mean = tmp.loc[attrition_mask(tmp[TARGET_COL]), "ThuNhapHangThang_VND"].mean()
    stay_mean = tmp.loc[~attrition_mask(tmp[TARGET_COL]), "ThuNhapHangThang_VND"].mean()
    summary = (
        f"Thu nhập trung bình nhóm nghỉ việc: {format_vnd(leave_mean)}; "
        f"nhóm ở lại: {format_vnd(stay_mean)}. "
        "Sự khác biệt phản ánh xu hướng trong dữ liệu, không suy ra nhân quả."
    )
    return {"table": table, "summary": summary}


def rq6_tenure_attrition(df: pd.DataFrame) -> dict[str, Any]:
    """RQ6: Thâm niên và nghỉ việc."""
    if "SoNamTaiCongTy" not in df.columns:
        return {"table": pd.DataFrame(), "summary": "Thiếu cột SoNamTaiCongTy."}

    tmp = df[[TARGET_COL, "SoNamTaiCongTy"]].copy()
    tmp["SoNamTaiCongTy"] = pd.to_numeric(tmp["SoNamTaiCongTy"], errors="coerce")
    table = (
        tmp.groupby(TARGET_COL)["SoNamTaiCongTy"]
        .agg(["count", "mean", "median", "std"])
        .reset_index()
        .round(2)
    )
    leave_med = tmp.loc[attrition_mask(tmp[TARGET_COL]), "SoNamTaiCongTy"].median()
    stay_med = tmp.loc[~attrition_mask(tmp[TARGET_COL]), "SoNamTaiCongTy"].median()
    summary = (
        f"Số năm tại công ty (median) nhóm nghỉ việc: {leave_med:.2f} năm; "
        f"nhóm ở lại: {stay_med:.2f} năm."
    )
    return {"table": table, "summary": summary}


def rq7_distance_attrition(df: pd.DataFrame) -> dict[str, Any]:
    """RQ7: Khoảng cách nhà – nơi làm việc."""
    if "KhoangCachNha_Km" not in df.columns:
        return {"table": pd.DataFrame(), "summary": "Thiếu cột KhoangCachNha_Km."}

    tmp = df[[TARGET_COL, "KhoangCachNha_Km"]].copy()
    tmp["KhoangCachNha_Km"] = pd.to_numeric(tmp["KhoangCachNha_Km"], errors="coerce")
    table = (
        tmp.groupby(TARGET_COL)["KhoangCachNha_Km"]
        .agg(["count", "mean", "median", "std"])
        .reset_index()
        .round(2)
    )
    leave_mean = tmp.loc[attrition_mask(tmp[TARGET_COL]), "KhoangCachNha_Km"].mean()
    stay_mean = tmp.loc[~attrition_mask(tmp[TARGET_COL]), "KhoangCachNha_Km"].mean()
    summary = (
        f"Khoảng cách trung bình nhóm nghỉ việc: {leave_mean:.2f} km; "
        f"nhóm ở lại: {stay_mean:.2f} km."
    )
    return {"table": table, "summary": summary}


def rq8_performance_training(df: pd.DataFrame) -> dict[str, Any]:
    """RQ8: Đánh giá hiệu suất và đào tạo."""
    results: dict[str, Any] = {}
    summaries = []

    if "DanhGiaHieuSuat" in df.columns:
        perf = attrition_rate_by_group(df, "DanhGiaHieuSuat").sort_values("DanhGiaHieuSuat")
        results["performance"] = perf
        if not perf.empty:
            summaries.append(
                f"Tỷ lệ nghỉ việc theo đánh giá hiệu suất dao động từ "
                f"{format_pct(perf['attrition_rate'].min())} đến "
                f"{format_pct(perf['attrition_rate'].max())}."
            )

    if "SoLanDaoTao_Nam" in df.columns:
        train = attrition_rate_by_group(df, "SoLanDaoTao_Nam").sort_values("SoLanDaoTao_Nam")
        results["training"] = train
        leave_mean = df.loc[attrition_mask(df[TARGET_COL]), "SoLanDaoTao_Nam"].mean()
        stay_mean = df.loc[~attrition_mask(df[TARGET_COL]), "SoLanDaoTao_Nam"].mean()
        summaries.append(
            f"Số lần đào tạo/năm trung bình — nghỉ việc: {leave_mean:.2f}; "
            f"ở lại: {stay_mean:.2f}."
        )

    results["summary"] = " ".join(summaries) if summaries else "Không đủ dữ liệu."
    return results


def run_all_rq(df: pd.DataFrame) -> dict[str, Any]:
    """Chạy toàn bộ research questions."""
    return {
        "rq1": rq1_attrition_distribution(df),
        "rq2": rq2_attrition_by_department(df),
        "rq3": rq3_overtime_attrition(df),
        "rq4": rq4_job_satisfaction(df),
        "rq5": rq5_income_by_attrition(df),
        "rq6": rq6_tenure_attrition(df),
        "rq7": rq7_distance_attrition(df),
        "rq8": rq8_performance_training(df),
        "overall_attrition_rate": attrition_rate(df),
    }
