from __future__ import annotations

import pandas as pd


def analyze_sales_seasonality(
    data: pd.DataFrame,
) -> dict:
    if data.empty:
        raise ValueError("Time-series data cannot be empty.")

    required_columns = {"Date", "Weekly_Sales"}

    missing_columns = required_columns - set(data.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    df = data[["Date", "Weekly_Sales"]].copy()

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce",
    )

    df["Weekly_Sales"] = pd.to_numeric(
        df["Weekly_Sales"],
        errors="coerce",
    )

    df = df.dropna(
        subset=["Date", "Weekly_Sales"]
    )

    df = df.sort_values("Date").reset_index(drop=True)

    df["year"] = df["Date"].dt.year
    df["month"] = df["Date"].dt.month
    df["week_of_year"] = df["Date"].dt.isocalendar().week.astype(int)

    monthly_sales = (
        df.groupby("month")["Weekly_Sales"]
        .agg(["mean", "min", "max", "count"])
        .reset_index()
    )

    yearly_sales = (
        df.groupby("year")["Weekly_Sales"]
        .agg(["mean", "min", "max", "count"])
        .reset_index()
    )

    return {
        "row_count": len(df),
        "date_start": df["Date"].min(),
        "date_end": df["Date"].max(),
        "monthly_sales": monthly_sales,
        "yearly_sales": yearly_sales,
    }