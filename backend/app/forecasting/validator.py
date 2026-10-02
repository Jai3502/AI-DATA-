from __future__ import annotations

import pandas as pd


def split_timeseries(
    data: pd.DataFrame,
    test_periods: int = 12,
) -> tuple[pd.DataFrame, pd.DataFrame]:

    if data.empty:
        raise ValueError("Time-series data cannot be empty.")

    if test_periods <= 0:
        raise ValueError("test_periods must be greater than zero.")

    if len(data) <= test_periods:
        raise ValueError(
            "Not enough observations for the requested test period."
        )

    data = data.sort_values("Date").reset_index(drop=True)

    train = data.iloc[:-test_periods].copy()
    test = data.iloc[-test_periods:].copy()

    return train, test