from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class ForecastRequest(BaseModel):
    horizon: int = Field(
        default=12,
        ge=1,
        le=52,
        description="Number of future periods to forecast.",
    )


class ForecastPoint(BaseModel):
    date: date
    forecast: float


class HistoricalPoint(BaseModel):
    date: date
    actual: float


class ForecastResponse(BaseModel):
    dataset_id: str
    horizon: int
    model: str
    frequency: str

    historical_start: date
    historical_end: date

    historical: list[HistoricalPoint]
    forecast: list[ForecastPoint]

    metrics: dict[str, float]
    warnings: list[str]