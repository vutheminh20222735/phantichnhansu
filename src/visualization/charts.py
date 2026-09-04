"""Biểu đồ trực quan hóa HR Analytics."""

from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from src.analysis.correlation import compute_correlation_matrix
from src.analysis.eda import attrition_rate_by_group
from src.utils import TARGET_COL, format_pct

# Palette doanh nghiệp (teal / navy)
_C_PRIMARY = "#0B3A4A"
_C_ACCENT = "#1F8A70"
_C_DANGER = "#C0392B"
_C_SUCCESS = "#1E8449"
_C_GOLD = "#CA8A04"

sns.set_theme(style="whitegrid", font="DejaVu Sans", font_scale=0.95)
plt.rcParams.update(
    {
        "figure.figsize": (9, 4.8),
        "axes.titlesize": 12,
        "axes.titleweight": "bold",
        "axes.labelsize": 10,
        "figure.facecolor": "#FFFFFF",
        "axes.facecolor": "#FFFFFF",
        "axes.edgecolor": "#D7E0E6",
        "font.family": "DejaVu Sans",
    }
)


def _bar_count(df: pd.DataFrame, col: str, title: str, xlabel: str, ylabel: str = "Số lượng nhân viên"):
    fig, ax = plt.subplots()
    order = df[col].value_counts().index
    sns.countplot(data=df, y=col, order=order, ax=ax, color=_C_PRIMARY)
    ax.set_title(title)
    ax.set_xlabel(ylabel)
    ax.set_ylabel(xlabel)
    fig.tight_layout()
    top = order[0]
    n_top = int((df[col] == top).sum())
    comment = (
        f"Nhóm `{top}` chiếm số lượng lớn nhất với {n_top} nhân viên "
        f"({n_top / len(df) * 100:.2f}% tổng số)."
    )
    return fig, comment


def chart_dept_distribution(df: pd.DataFrame):
    """Chart 1: Employee Distribution by Department."""
    return _bar_count(
        df, "PhongBan",
        "Phân bố nhân viên theo phòng ban",
        "Phòng ban",
    )


def chart_job_role_distribution(df: pd.DataFrame):
    """Chart 2: Employee Distribution by Job Role."""
    return _bar_count(
        df, "ViTriCongViec",
        "Phân bố nhân viên theo vị trí công việc",
        "Vị trí công việc",
    )


def chart_age_distribution(df: pd.DataFrame):
    """Chart 3: Age Distribution."""
    fig, ax = plt.subplots()
    sns.histplot(df["Tuoi"], bins=20, kde=True, ax=ax, color="#0B3A4A")
    ax.set_title("Phân bố tuổi nhân viên")
    ax.set_xlabel("Tuổi (năm)")
    ax.set_ylabel("Số lượng nhân viên")
    mean_age = float(df["Tuoi"].mean())
    ax.axvline(mean_age, color="#C0392B", linestyle="--", label=f"Mean = {mean_age:.1f}")
    ax.legend()
    fig.tight_layout()
    comment = (
        f"Tuổi trung bình là {mean_age:.2f} năm; "
        f"khoảng tuổi từ {int(df['Tuoi'].min())} đến {int(df['Tuoi'].max())}."
    )
    return fig, comment


def chart_income_distribution(df: pd.DataFrame):
    """Chart 4: Monthly Income Distribution."""
    fig, ax = plt.subplots()
    income_trieu = df["ThuNhapHangThang_VND"] / 1_000_000
    sns.histplot(income_trieu, bins=25, kde=True, ax=ax, color="#1E8449")
    ax.set_title("Phân bố thu nhập hàng tháng")
    ax.set_xlabel("Thu nhập (triệu VND)")
    ax.set_ylabel("Số lượng nhân viên")
    mean_inc = float(income_trieu.mean())
    ax.axvline(mean_inc, color="#C0392B", linestyle="--", label=f"Mean = {mean_inc:.1f} triệu")
    ax.legend()
    fig.tight_layout()
    comment = f"Thu nhập trung bình khoảng {mean_inc:.1f} triệu VND/tháng."
    return fig, comment


def chart_attrition_distribution(df: pd.DataFrame):
    """Chart 5: Attrition Distribution."""
    fig, ax = plt.subplots()
    counts = df[TARGET_COL].value_counts()
    colors = ["#1E8449" if x == "Không" else "#C0392B" for x in counts.index]
    ax.bar(counts.index.astype(str), counts.values, color=colors)
    ax.set_title("Phân bố tình trạng nghỉ việc")
    ax.set_xlabel("NghiViec")
    ax.set_ylabel("Số lượng nhân viên")
    for i, (label, val) in enumerate(counts.items()):
        pct = val / len(df) * 100
        ax.text(i, val, f"{val}\n({pct:.2f}%)", ha="center", va="bottom", fontsize=9)
    fig.tight_layout()
    leave_pct = counts.get("Có", 0) / len(df) * 100
    comment = f"Tỷ lệ nghỉ việc hiện tại là {format_pct(leave_pct)} ({int(counts.get('Có', 0))} người)."
    return fig, comment


def chart_attrition_donut(df: pd.DataFrame):
    """Donut chart phân bố nghỉ việc — cùng dữ liệu với distribution."""
    counts = df[TARGET_COL].value_counts()
    leave = int(counts.get("Có", 0))
    stay = int(counts.get("Không", 0))
    fig, ax = plt.subplots(figsize=(5.2, 4.2))
    wedges, texts, autotexts = ax.pie(
        [leave, stay],
        labels=["Nghỉ việc", "Ở lại"],
        colors=[_C_DANGER, _C_SUCCESS],
        autopct="%1.1f%%",
        startangle=90,
        pctdistance=0.75,
        wedgeprops=dict(width=0.42, edgecolor="white"),
    )
    for t in texts + autotexts:
        t.set_fontsize(9)
    centre = plt.Circle((0, 0), 0.35, fc="white")
    ax.add_artist(centre)
    rate = leave / len(df) * 100 if len(df) else 0
    ax.text(0, 0.05, f"{rate:.1f}%", ha="center", va="center", fontsize=16, fontweight="bold", color=_C_DANGER)
    ax.text(0, -0.12, "Attrition", ha="center", va="center", fontsize=9, color="#5B6E78")
    ax.set_title("Tình trạng nghỉ việc")
    fig.tight_layout()
    comment = f"{leave} nghỉ / {stay} ở lại — tỷ lệ {format_pct(rate)}."
    return fig, comment


def chart_attrition_by_dept(df: pd.DataFrame):
    """Chart 6: Attrition Rate by Department."""
    table = attrition_rate_by_group(df, "PhongBan")
    fig, ax = plt.subplots()
    sns.barplot(data=table, y="PhongBan", x="attrition_rate", ax=ax, color="#C0392B")
    ax.set_title("Tỷ lệ nghỉ việc theo phòng ban")
    ax.set_xlabel("Tỷ lệ nghỉ việc (%)")
    ax.set_ylabel("Phòng ban")
    fig.tight_layout()
    top = table.iloc[0]
    comment = (
        f"`{top['PhongBan']}` có tỷ lệ nghỉ việc cao nhất: "
        f"{format_pct(top['attrition_rate'])}."
    )
    return fig, comment, table


def chart_attrition_by_overtime(df: pd.DataFrame):
    """Chart 7: Attrition Rate by Overtime."""
    table = attrition_rate_by_group(df, "LamThemGio")
    fig, ax = plt.subplots()
    sns.barplot(data=table, x="LamThemGio", y="attrition_rate", hue="LamThemGio", ax=ax, palette=["#0B3A4A", "#C0392B"], legend=False)
    ax.set_title("Tỷ lệ nghỉ việc theo làm thêm giờ")
    ax.set_xlabel("Làm thêm giờ")
    ax.set_ylabel("Tỷ lệ nghỉ việc (%)")
    fig.tight_layout()
    comment = "So sánh tỷ lệ nghỉ việc giữa nhóm Có/Không làm thêm giờ dựa trên dữ liệu thực tế."
    if len(table) >= 2:
        comment = (
            f"Tỷ lệ nghỉ việc — Có OT: "
            f"{format_pct(float(table.loc[table['LamThemGio']=='Có','attrition_rate'].mean() if (table['LamThemGio']=='Có').any() else 0))}; "
            f"Không OT: "
            f"{format_pct(float(table.loc[table['LamThemGio']=='Không','attrition_rate'].mean() if (table['LamThemGio']=='Không').any() else 0))}."
        )
    return fig, comment, table


def chart_attrition_by_satisfaction(df: pd.DataFrame):
    """Chart 8: Attrition Rate by Job Satisfaction."""
    table = attrition_rate_by_group(df, "HaiLong_CongViec").sort_values("HaiLong_CongViec")
    fig, ax = plt.subplots()
    sns.barplot(data=table, x="HaiLong_CongViec", y="attrition_rate", ax=ax, color="#CA8A04")
    ax.set_title("Tỷ lệ nghỉ việc theo mức hài lòng công việc")
    ax.set_xlabel("Hài lòng công việc (1–5)")
    ax.set_ylabel("Tỷ lệ nghỉ việc (%)")
    fig.tight_layout()
    if not table.empty:
        low = table.iloc[0]
        high = table.iloc[-1]
        comment = (
            f"Mức hài lòng {low['HaiLong_CongViec']}: {format_pct(low['attrition_rate'])}; "
            f"mức {high['HaiLong_CongViec']}: {format_pct(high['attrition_rate'])}."
        )
    else:
        comment = "Không đủ dữ liệu."
    return fig, comment, table


def chart_income_by_attrition(df: pd.DataFrame):
    """Chart 9: Monthly Income by Attrition (boxplot)."""
    fig, ax = plt.subplots()
    plot_df = df.copy()
    plot_df["Thu nhập (triệu VND)"] = plot_df["ThuNhapHangThang_VND"] / 1_000_000
    sns.boxplot(data=plot_df, x=TARGET_COL, y="Thu nhập (triệu VND)", hue=TARGET_COL, ax=ax, palette=["#1E8449", "#C0392B"], legend=False)
    ax.set_title("Thu nhập hàng tháng theo tình trạng nghỉ việc")
    ax.set_xlabel("NghiViec")
    ax.set_ylabel("Thu nhập (triệu VND)")
    fig.tight_layout()
    med = plot_df.groupby(TARGET_COL)["Thu nhập (triệu VND)"].median()
    comment = (
        "Median thu nhập — "
        + "; ".join([f"{k}: {v:.1f} triệu VND" for k, v in med.items()])
        + "."
    )
    return fig, comment


def chart_tenure_by_attrition(df: pd.DataFrame):
    """Chart 10: Years at Company by Attrition."""
    fig, ax = plt.subplots()
    sns.boxplot(data=df, x=TARGET_COL, y="SoNamTaiCongTy", hue=TARGET_COL, ax=ax, palette=["#1E8449", "#C0392B"], legend=False)
    ax.set_title("Số năm tại công ty theo tình trạng nghỉ việc")
    ax.set_xlabel("NghiViec")
    ax.set_ylabel("Số năm tại công ty")
    fig.tight_layout()
    med = df.groupby(TARGET_COL)["SoNamTaiCongTy"].median()
    comment = "Median thâm niên — " + "; ".join([f"{k}: {v:.1f} năm" for k, v in med.items()]) + "."
    return fig, comment


def chart_distance_by_attrition(df: pd.DataFrame):
    """Chart 11: Distance From Home by Attrition."""
    fig, ax = plt.subplots()
    sns.boxplot(data=df, x=TARGET_COL, y="KhoangCachNha_Km", hue=TARGET_COL, ax=ax, palette=["#1E8449", "#C0392B"], legend=False)
    ax.set_title("Khoảng cách nhà – công ty theo tình trạng nghỉ việc")
    ax.set_xlabel("NghiViec")
    ax.set_ylabel("Khoảng cách (km)")
    fig.tight_layout()
    mean = df.groupby(TARGET_COL)["KhoangCachNha_Km"].mean()
    comment = "Khoảng cách trung bình — " + "; ".join([f"{k}: {v:.2f} km" for k, v in mean.items()]) + "."
    return fig, comment


def chart_correlation_heatmap(df: pd.DataFrame):
    """Chart 12: Correlation Heatmap."""
    corr = compute_correlation_matrix(df, include_target=True)
    fig, ax = plt.subplots(figsize=(12, 10))
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    sns.heatmap(
        corr,
        mask=mask,
        annot=False,
        cmap="RdBu_r",
        center=0,
        ax=ax,
        square=True,
        cbar_kws={"label": "Pearson r"},
    )
    ax.set_title("Ma trận tương quan các biến số (+ NghiViec đã mã hóa)")
    ax.set_xlabel("Biến")
    ax.set_ylabel("Biến")
    fig.tight_layout()
    comment = (
        "Heatmap thể hiện mức độ liên hệ tuyến tính giữa các biến số. "
        "Tương quan mạnh không đồng nghĩa với quan hệ nhân quả."
    )
    return fig, comment, corr


def build_all_charts(df: pd.DataFrame) -> list[dict[str, Any]]:
    """Tạo danh sách >= 12 biểu đồ kèm nhận xét."""
    charts: list[dict[str, Any]] = []

    fig, comment = chart_dept_distribution(df)
    charts.append({"id": 1, "title": "Phân bố theo phòng ban", "fig": fig, "comment": comment})

    fig, comment = chart_job_role_distribution(df)
    charts.append({"id": 2, "title": "Phân bố theo vị trí", "fig": fig, "comment": comment})

    fig, comment = chart_age_distribution(df)
    charts.append({"id": 3, "title": "Phân bố tuổi", "fig": fig, "comment": comment})

    fig, comment = chart_income_distribution(df)
    charts.append({"id": 4, "title": "Phân bố thu nhập", "fig": fig, "comment": comment})

    fig, comment = chart_attrition_distribution(df)
    charts.append({"id": 5, "title": "Phân bố nghỉ việc", "fig": fig, "comment": comment})

    fig, comment, _ = chart_attrition_by_dept(df)
    charts.append({"id": 6, "title": "Tỷ lệ nghỉ việc theo phòng ban", "fig": fig, "comment": comment})

    fig, comment, _ = chart_attrition_by_overtime(df)
    charts.append({"id": 7, "title": "Tỷ lệ nghỉ việc theo OT", "fig": fig, "comment": comment})

    fig, comment, _ = chart_attrition_by_satisfaction(df)
    charts.append({"id": 8, "title": "Tỷ lệ nghỉ việc theo hài lòng CV", "fig": fig, "comment": comment})

    fig, comment = chart_income_by_attrition(df)
    charts.append({"id": 9, "title": "Thu nhập theo nghỉ việc", "fig": fig, "comment": comment})

    fig, comment = chart_tenure_by_attrition(df)
    charts.append({"id": 10, "title": "Thâm niên theo nghỉ việc", "fig": fig, "comment": comment})

    fig, comment = chart_distance_by_attrition(df)
    charts.append({"id": 11, "title": "Khoảng cách theo nghỉ việc", "fig": fig, "comment": comment})

    fig, comment, _ = chart_correlation_heatmap(df)
    charts.append({"id": 12, "title": "Correlation heatmap", "fig": fig, "comment": comment})

    return charts
