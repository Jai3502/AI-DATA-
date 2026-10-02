from __future__ import annotations

import pandas as pd


def create_forecasting_features(
    data: pd.DataFrame,
) -> pd.DataFrame:

    if data.empty:
        raise ValueError("Time-series data cannot be empty.")

    required_columns = {
        "Date",
        "Weekly_Sales",
        "Holiday_Flag",
    }

    missing_columns = required_columns - set(data.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    df = data[
        [
            "Date",
            "Weekly_Sales",
            "Holiday_Flag",
        ]
    ].copy()

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce",
    )

    df["Weekly_Sales"] = pd.to_numeric(
        df["Weekly_Sales"],
        errors="coerce",
    )

    df["Holiday_Flag"] = pd.to_numeric(
        df["Holiday_Flag"],
        errors="coerce",
    )

    df = df.dropna(
        subset=[
            "Date",
            "Weekly_Sales",
            "Holiday_Flag",
        ]
    )

    df = df.sort_values(
        "Date"
    ).reset_index(drop=True)

    df["month"] = df["Date"].dt.month

    df["week_of_year"] = (
        df["Date"]
        .dt.isocalendar()
        .week
        .astype(int)
    )

    df["holiday_flag"] = (
        df["Holiday_Flag"]
        .astype(int)
    )

    df["lag_1"] = (
        df["Weekly_Sales"]
        .shift(1)
    )

    df["lag_2"] = (
        df["Weekly_Sales"]
        .shift(2)
    )

    df["lag_4"] = (
        df["Weekly_Sales"]
        .shift(4)
    )

    df["lag_8"] = (
        df["Weekly_Sales"]
        .shift(8)
    )
    df["lag_12"] = (
    df["Weekly_Sales"]
    .shift(12)
)

    df["lag_52"] = (
    df["Weekly_Sales"]
    .shift(52)
)

    df["rolling_mean_4"] = (
        df["Weekly_Sales"]
        .shift(1)
        .rolling(window=4)
        .mean()
    )

    df["rolling_mean_8"] = (
        df["Weekly_Sales"]
        .shift(1)
        .rolling(window=8)
        .mean()
    )

    df["rolling_mean_12"] = (
        df["Weekly_Sales"]
        .shift(1)
        .rolling(window=12)
        .mean()
    )

    return df.dropna().reset_index(drop=True)