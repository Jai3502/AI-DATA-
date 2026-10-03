from __future__ import annotations

import pandas as pd

from sklearn.ensemble import RandomForestRegressor

from app.forecasting.features import create_forecasting_features



FEATURE_COLUMNS = [
    "month",
    "week_of_year",
    "is_christmas_period",
    "holiday_flag",
    "lag_1",
    "lag_2",
    "lag_4",
    "lag_8",
    "lag_12",
    "lag_51",
    "lag_52",
    "rolling_mean_4",
    "rolling_mean_8",
    "rolling_mean_12",

]


class SalesForecastModel:
    def __init__(
        self,
        n_estimators: int = 300,
        random_state: int = 42,
    ) -> None:
        self.model = RandomForestRegressor(
            n_estimators=n_estimators,
            random_state=random_state,
            n_jobs=-1,
        )

    def fit(
        self,
        data: pd.DataFrame,
    ) -> "SalesForecastModel":

        missing_columns = (
            set(FEATURE_COLUMNS) - set(data.columns)
        )

        if missing_columns:
            raise ValueError(
                f"Missing feature columns: {sorted(missing_columns)}"
            )

        if "Weekly_Sales" not in data.columns:
            raise ValueError(
                "Target column 'Weekly_Sales' is missing."
            )

        X = data[FEATURE_COLUMNS]
        y = data["Weekly_Sales"]

        if X.empty:
            raise ValueError(
                "Training data cannot be empty."
            )

        self.model.fit(X, y)

        return self

    def predict(
        self,
        data: pd.DataFrame,
    ) -> pd.Series:

        missing_columns = (
            set(FEATURE_COLUMNS) - set(data.columns)
        )

        if missing_columns:
            raise ValueError(
                f"Missing feature columns: {sorted(missing_columns)}"
            )

        predictions = self.model.predict(
            data[FEATURE_COLUMNS]
        )

        return pd.Series(
            predictions,
            index=data.index,
            name="Forecast",
        )


def recursive_forecast(
    model: SalesForecastModel,
    history: pd.DataFrame,
    horizon: int,
) -> pd.DataFrame:

    if history.empty:
        raise ValueError("History cannot be empty.")

    if horizon <= 0:
        raise ValueError(
            "Forecast horizon must be greater than zero."
        )

    required_columns = {
        "Date",
        "Weekly_Sales",
        "Holiday_Flag",
    }

    missing_columns = (
        required_columns - set(history.columns)
    )

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    history = history[
        [
            "Date",
            "Weekly_Sales",
            "Holiday_Flag",
        ]
    ].copy()

    history["Date"] = pd.to_datetime(
        history["Date"],
        errors="coerce",
    )

    history["Weekly_Sales"] = pd.to_numeric(
        history["Weekly_Sales"],
        errors="coerce",
    )

    history["Holiday_Flag"] = pd.to_numeric(
        history["Holiday_Flag"],
        errors="coerce",
    )

    history = (
        history
        .dropna(
            subset=[
                "Date",
                "Weekly_Sales",
                "Holiday_Flag",
            ]
        )
        .sort_values("Date")
        .reset_index(drop=True)
    )

    if len(history) < 12:
        raise ValueError(
            "At least 12 historical observations are required."
        )

    future_rows = []

    working_data = history.copy()

    for _ in range(horizon):

        next_date = (
            working_data["Date"].iloc[-1]
            + pd.Timedelta(weeks=1)
        )

        # Future holiday flag is initially 0.
        # This will be improved with a proper
        # holiday calendar in a later step.
        future_holiday_flag = 0

        temp = pd.concat(
            [
                working_data,
                pd.DataFrame(
                    {
                        "Date": [next_date],
                        "Weekly_Sales": [float("nan")],
                        "Holiday_Flag": [future_holiday_flag],
                    }
                ),
            ],
            ignore_index=True,
        )

        features = create_forecasting_features(
            temp
        )

        latest_features = features.iloc[[-1]]

        prediction = float(
            model.predict(
                latest_features
            ).iloc[0]
        )

        future_rows.append(
            {
                "Date": next_date,
                "Forecast": prediction,
            }
        )

        working_data = pd.concat(
            [
                working_data,
                pd.DataFrame(
                    {
                        "Date": [next_date],
                        "Weekly_Sales": [prediction],
                        "Holiday_Flag": [future_holiday_flag],
                    }
                ),
            ],
            ignore_index=True,
        )

    return pd.DataFrame(
        future_rows
    )