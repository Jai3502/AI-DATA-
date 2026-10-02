from __future__ import annotations

import pandas as pd

from app.forecasting.features import create_forecasting_features
from app.forecasting.metrics import calculate_forecast_metrics
from app.forecasting.model import (
    SalesForecastModel,
    recursive_forecast,
)


def walk_forward_validation(
    data: pd.DataFrame,
    initial_train_size: int = 83,
    test_periods: int = 12,
    step_size: int = 12,
) -> pd.DataFrame:

    if data.empty:
        raise ValueError(
            "Time-series data cannot be empty."
        )

    if initial_train_size <= 12:
        raise ValueError(
            "initial_train_size must be greater than 12."
        )

    if test_periods <= 0:
        raise ValueError(
            "test_periods must be greater than zero."
        )

    if step_size <= 0:
        raise ValueError(
            "step_size must be greater than zero."
        )

    required_columns = {
        "Date",
        "Weekly_Sales",
        "Holiday_Flag",
    }

    missing_columns = (
        required_columns - set(data.columns)
    )

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    data = (
        data[
            [
                "Date",
                "Weekly_Sales",
                "Holiday_Flag",
            ]
        ]
        .copy()
        .sort_values("Date")
        .reset_index(drop=True)
    )

    results = []

    train_end = initial_train_size

    window_number = 1

    while train_end + test_periods <= len(data):

        train = data.iloc[
            :train_end
        ].copy()

        test = data.iloc[
            train_end:train_end + test_periods
        ].copy()

        train_features = (
            create_forecasting_features(train)
        )

        model = SalesForecastModel()

        model.fit(train_features)

        forecast = recursive_forecast(
            model=model,
            history=train,
            horizon=test_periods,
        )

        metrics = calculate_forecast_metrics(
            actual=test[
                "Weekly_Sales"
            ].reset_index(drop=True),
            predicted=forecast[
                "Forecast"
            ].reset_index(drop=True),
        )

        results.append(
            {
                "window": window_number,
                "train_end_date": train[
                    "Date"
                ].iloc[-1],
                "test_start_date": test[
                    "Date"
                ].iloc[0],
                "test_end_date": test[
                    "Date"
                ].iloc[-1],
                "train_size": len(train),
                "test_size": len(test),
                "mae": metrics["mae"],
                "rmse": metrics["rmse"],
                "mape": metrics["mape"],
            }
        )

        train_end += step_size
        window_number += 1

    if not results:
        raise ValueError(
            "Not enough data for walk-forward validation."
        )

    return pd.DataFrame(results)