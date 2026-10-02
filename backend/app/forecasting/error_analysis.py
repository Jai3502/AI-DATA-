from __future__ import annotations

import pandas as pd

from app.forecasting.features import create_forecasting_features
from app.forecasting.model import (
    SalesForecastModel,
    recursive_forecast,
)


def analyze_backtest_errors(
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

        comparison = pd.DataFrame(
            {
                "Window": window_number,
                "Train_End": train[
                    "Date"
                ].iloc[-1],
                "Date": test[
                    "Date"
                ].reset_index(drop=True),
                "Actual": test[
                    "Weekly_Sales"
                ].reset_index(drop=True),
                "Forecast": forecast[
                    "Forecast"
                ].reset_index(drop=True),
                "Holiday_Flag": test[
                    "Holiday_Flag"
                ].reset_index(drop=True),
            }
        )

        comparison["Absolute_Error"] = (
            comparison["Actual"]
            - comparison["Forecast"]
        ).abs()

        non_zero_actual = (
            comparison["Actual"] != 0
        )

        comparison["Percentage_Error"] = 0.0

        comparison.loc[
            non_zero_actual,
            "Percentage_Error",
        ] = (
            comparison.loc[
                non_zero_actual,
                "Absolute_Error",
            ]
            / comparison.loc[
                non_zero_actual,
                "Actual",
            ].abs()
            * 100
        )

        results.append(comparison)

        train_end += step_size
        window_number += 1

    if not results:
        raise ValueError(
            "Not enough data for error analysis."
        )

    return pd.concat(
        results,
        ignore_index=True,
    )