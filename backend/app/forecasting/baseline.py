from __future__ import annotations

import pandas as pd


def naive_forecast(
    train: pd.DataFrame,
    horizon: int,
) -> pd.DataFrame:

    if train.empty:
        raise ValueError("Training data cannot be empty.")

    if horizon <= 0:
        raise ValueError("Forecast horizon must be greater than zero.")

    last_value = float(train["Weekly_Sales"].iloc[-1])

    last_date = pd.Timestamp(train["Date"].iloc[-1])

    future_dates = pd.date_range(
        start=last_date + pd.Timedelta(weeks=1),
        periods=horizon,
        freq="7D",
    )

    forecast = pd.DataFrame(
        {
            "Date": future_dates,
            "Forecast": last_value,
        }
    )

    return forecast