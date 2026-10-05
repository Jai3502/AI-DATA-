from __future__ import annotations

from pathlib import Path

from app.forecasting.features import create_forecasting_features
from app.forecasting.backtesting import walk_forward_validation
from app.forecasting.model import (
    SalesForecastModel,
    recursive_forecast,
)
from app.forecasting.preprocessor import prepare_sales_timeseries
from app.schemas.forecast import (
    ForecastPoint,
    ForecastResponse,
    HistoricalPoint,
)


def generate_forecast(
    dataset_id: str,
    file_path: str,
    horizon: int,
) -> ForecastResponse:

    path = Path(file_path)

    if not path.exists():
        raise ValueError(
            "Dataset file was not found."
        )

    # ---------------------------------
    # Prepare historical time series
    # ---------------------------------

    data = prepare_sales_timeseries(
        file_path=str(path),
        date_column="Date",
        target_column="Weekly_Sales",
    )

    if len(data) < 12:
        raise ValueError(
            "At least 12 historical observations "
            "are required for forecasting."
        )

    # ---------------------------------
    # Create training features
    # ---------------------------------

    features = create_forecasting_features(
        data
    )

    # ---------------------------------
    # Train forecasting model
    # ---------------------------------

    model = SalesForecastModel()

    model.fit(features)

    # ---------------------------------
    # Generate future forecast
    # ---------------------------------

    forecast = recursive_forecast(
        model=model,
        history=data,
        horizon=horizon,
    )

    # ---------------------------------
    # Walk-forward validation
    # ---------------------------------

    backtest_results = walk_forward_validation(
        data
    )

    metrics = {
        "mae": float(
            backtest_results["mae"].mean()
        ),
        "rmse": float(
            backtest_results["rmse"].mean()
        ),
        "mape": float(
            backtest_results["mape"].mean()
        ),
    }

    # ---------------------------------
    # Historical response points
    # ---------------------------------

    historical_points = [
        HistoricalPoint(
            date=row.Date.date(),
            actual=float(row.Weekly_Sales),
        )
        for row in data.itertuples(
            index=False
        )
    ]

    # ---------------------------------
    # Forecast response points
    # ---------------------------------

    forecast_points = [
        ForecastPoint(
            date=row.Date.date(),
            forecast=float(row.Forecast),
        )
        for row in forecast.itertuples(
            index=False
        )
    ]

    # ---------------------------------
    # Forecast warnings / notes
    # ---------------------------------

    warnings = [
        "Future holiday flags are generated using "
        "the forecasting holiday calendar."
    ]

    # ---------------------------------
    # Final response
    # ---------------------------------

    return ForecastResponse(
        dataset_id=dataset_id,
        horizon=horizon,
        model="random_forest",
        frequency="weekly",
        historical_start=data["Date"].min().date(),
        historical_end=data["Date"].max().date(),
        historical=historical_points,
        forecast=forecast_points,
        metrics=metrics,
        warnings=warnings,
    )