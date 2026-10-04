from __future__ import annotations

from pathlib import Path

from app.forecasting.features import create_forecasting_features
from app.forecasting.backtesting import walk_forward_validation
from app.forecasting.model import SalesForecastModel, recursive_forecast
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
        raise ValueError("Dataset file was not found.")

    data = prepare_sales_timeseries(
        file_path=str(path),
        date_column="Date",
        target_column="Weekly_Sales",
    )

    if len(data) < 12:
        raise ValueError(
            "At least 12 historical observations are required for forecasting."
        )

    features = create_forecasting_features(data)

    model = SalesForecastModel()
    model.fit(features)

    forecast = recursive_forecast(
        model=model,
        history=data,
        horizon=horizon,
    )

    backtest_results = walk_forward_validation(data)

    metrics = {
        "mae": float(backtest_results["mae"].mean()),
        "rmse": float(backtest_results["rmse"].mean()),
        "mape": float(backtest_results["mape"].mean()),
    }
    historical_points = [
        HistoricalPoint(
            date=row.Date.date(),
            actual=float(row.Weekly_Sales),
        )
        for row in data.itertuples(index=False)
    ]

    forecast_points = [
        ForecastPoint(
            date=row.Date.date(),
            forecast=float(row.Forecast),
        )
        for row in forecast.itertuples(index=False)
    ]

    warnings = [
        "Future holiday flags are currently estimated with a placeholder and "
        "should be replaced with a proper holiday calendar before production use."
    ]

    return ForecastResponse(
        dataset_id=dataset_id,
        horizon=horizon,
        model="random_forest",
        frequency="weekly",
        historical_start=data["Date"].min().date(),
        historical_end=data["Date"].max().date(),
        forecast=forecast_points,
        historical=historical_points,
        metrics=metrics,
        warnings=warnings,
    )