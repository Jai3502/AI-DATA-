from __future__ import annotations

import numpy as np
import pandas as pd


def calculate_forecast_metrics(
    actual: pd.Series,
    predicted: pd.Series,
) -> dict[str, float]:

    if len(actual) != len(predicted):
        raise ValueError(
            "Actual and predicted values must have the same length."
        )

    actual_values = actual.astype(float).to_numpy()
    predicted_values = predicted.astype(float).to_numpy()

    errors = actual_values - predicted_values

    mae = np.mean(np.abs(errors))
    rmse = np.sqrt(np.mean(errors**2))

    non_zero_actual = actual_values != 0

    if non_zero_actual.any():
        mape = np.mean(
            np.abs(
                errors[non_zero_actual]
                / actual_values[non_zero_actual]
            )
        ) * 100
    else:
        mape = 0.0

    return {
        "mae": float(mae),
        "rmse": float(rmse),
        "mape": float(mape),
    }