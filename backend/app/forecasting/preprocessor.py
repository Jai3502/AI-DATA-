from __future__ import annotations

import pandas as pd


def prepare_sales_timeseries(
    file_path: str,
    date_column: str,
    target_column: str,
) -> pd.DataFrame:
    df = pd.read_csv(file_path)

    if date_column not in df.columns:
        raise ValueError(
            f"Date column '{date_column}' was not found in the dataset."
        )

    if target_column not in df.columns:
        raise ValueError(
            f"Target column '{target_column}' was not found in the dataset."
        )

    data = df[
    [date_column, target_column, "Holiday_Flag"]
].copy()

    data[date_column] = pd.to_datetime(
        data[date_column],
        format="%d-%m-%Y",
        errors="coerce",
    )

    data[target_column] = pd.to_numeric(
        data[target_column],
        errors="coerce",
    )

    data = data.dropna(
        subset=[date_column, target_column]
    )

    data = data.sort_values(date_column)

    data = (
    data.groupby(date_column, as_index=False)
    .agg(
        {
            target_column: "sum",
            "Holiday_Flag": "max",
        }
    )
)

    return data