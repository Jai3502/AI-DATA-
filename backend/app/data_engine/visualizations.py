from __future__ import annotations

from typing import Any

import pandas as pd

from app.data_engine.context import DatasetContext


MAX_CATEGORIES = 20
MAX_TIME_POINTS = 100
MAX_NUMERIC_DISTRIBUTION_BINS = 20


def _json_safe(value: Any) -> Any:
    """
    Convert pandas / NumPy values into JSON-safe Python values.
    """

    if pd.isna(value):
        return None

    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass

    if isinstance(value, pd.Timestamp):
        return value.isoformat()

    return value


def _round_value(value: Any, digits: int = 4) -> Any:
    """
    Safely round numeric values.
    """

    value = _json_safe(value)

    if isinstance(value, (int, float)):
        return round(value, digits)

    return value


def _build_numeric_kpis(
    context: DatasetContext,
) -> list[dict[str, Any]]:
    """
    Generate KPI-style summaries for numeric columns.

    Only aggregated statistics are returned.
    """

    kpis: list[dict[str, Any]] = []

    for column in context.numeric_columns():

        series = pd.to_numeric(
            context.df[column],
            errors="coerce",
        ).dropna()

        if series.empty:
            continue

        kpis.append(
            {
                "column": column,
                "count": int(series.count()),
                "mean": _round_value(series.mean()),
                "median": _round_value(series.median()),
                "min": _round_value(series.min()),
                "max": _round_value(series.max()),
                "std": _round_value(series.std()),
            }
        )

    return kpis


def _build_categorical_charts(
    context: DatasetContext,
) -> list[dict[str, Any]]:
    """
    Generate bar-chart data for categorical columns.

    Only the top categories are returned.
    """

    charts: list[dict[str, Any]] = []

    for column in context.categorical_columns():

        series = (
            context.df[column]
            .astype("string")
            .fillna("Unknown")
        )

        value_counts = (
            series.value_counts()
            .head(MAX_CATEGORIES)
        )

        if value_counts.empty:
            continue

        data = [
            {
                "category": str(category),
                "count": int(count),
            }
            for category, count in value_counts.items()
        ]

        charts.append(
            {
                "type": "bar",
                "chart_id": f"category_distribution_{column}",
                "title": f"{column} distribution",
                "x_axis": column,
                "y_axis": "Count",
                "data": data,
            }
        )

    return charts


def _build_numeric_distributions(
    context: DatasetContext,
) -> list[dict[str, Any]]:
    """
    Generate histogram-style distribution data
    for numeric columns.

    Raw rows are not returned.
    """

    charts: list[dict[str, Any]] = []

    for column in context.numeric_columns():

        series = pd.to_numeric(
            context.df[column],
            errors="coerce",
        ).dropna()

        if series.empty:
            continue

        if series.nunique() <= 1:
            continue

        try:
            counts, bin_edges = pd.cut(
                series,
                bins=MAX_NUMERIC_DISTRIBUTION_BINS,
                retbins=True,
                duplicates="drop",
            )

            grouped = (
                series.groupby(
                    counts,
                    observed=False,
                )
                .size()
            )

        except Exception:
            continue

        data: list[dict[str, Any]] = []

        for interval, count in grouped.items():

            if pd.isna(interval):
                continue

            data.append(
                {
                    "range_start": _round_value(
                        interval.left
                    ),
                    "range_end": _round_value(
                        interval.right
                    ),
                    "count": int(count),
                }
            )

        if not data:
            continue

        charts.append(
            {
                "type": "histogram",
                "chart_id": f"distribution_{column}",
                "title": f"{column} distribution",
                "x_axis": column,
                "y_axis": "Count",
                "data": data,
            }
        )

    return charts


def _build_datetime_charts(
    context: DatasetContext,
) -> list[dict[str, Any]]:
    """
    Generate time-series charts.

    Numeric columns are aggregated by date.

    If a dataset contains many dates, the result is
    resampled to keep the dashboard payload bounded.
    """

    charts: list[dict[str, Any]] = []

    datetime_columns = context.datetime_columns()
    numeric_columns = context.numeric_columns()

    if not datetime_columns or not numeric_columns:
        return charts

    for date_column in datetime_columns:

        date_series = pd.to_datetime(
            context.df[date_column],
            errors="coerce",
            dayfirst=True,
        )

        valid_mask = date_series.notna()

        if not valid_mask.any():
            continue

        working_df = context.df.loc[
            valid_mask
        ].copy()

        working_df["_analysis_date"] = (
            date_series.loc[valid_mask]
        )

        working_df = working_df.sort_values(
            "_analysis_date"
        )

        unique_dates = (
            working_df["_analysis_date"]
            .dt.normalize()
            .nunique()
        )

        for numeric_column in numeric_columns:

            numeric_series = pd.to_numeric(
                working_df[numeric_column],
                errors="coerce",
            )

            valid_numeric = numeric_series.notna()

            if not valid_numeric.any():
                continue

            chart_df = working_df.loc[
                valid_numeric
            ].copy()

            chart_df["_analysis_value"] = (
                numeric_series.loc[valid_numeric]
            )

            if chart_df.empty:
                continue

            daily = (
                chart_df
                .assign(
                    _analysis_date=chart_df[
                        "_analysis_date"
                    ].dt.normalize()
                )
                .groupby(
                    "_analysis_date",
                    as_index=False,
                )["_analysis_value"]
                .mean()
            )

            if len(daily) > MAX_TIME_POINTS:

                daily = (
                    daily.set_index(
                        "_analysis_date"
                    )
                    .resample("W")[
                        "_analysis_value"
                    ]
                    .mean()
                    .dropna()
                    .reset_index()
                )

            if len(daily) > MAX_TIME_POINTS:

                step = max(
                    1,
                    len(daily)
                    // MAX_TIME_POINTS,
                )

                daily = daily.iloc[::step]

            data = [
                {
                    "date": _json_safe(row[
                        "_analysis_date"
                    ]),
                    "value": _round_value(
                        row["_analysis_value"]
                    ),
                }
                for _, row in daily.iterrows()
            ]

            if not data:
                continue

            charts.append(
                {
                    "type": "line",
                    "chart_id": (
                        f"time_series_"
                        f"{date_column}_"
                        f"{numeric_column}"
                    ),
                    "title": (
                        f"{numeric_column} over time"
                    ),
                    "x_axis": date_column,
                    "y_axis": numeric_column,
                    "aggregation": "mean",
                    "source_date_count": int(
                        unique_dates
                    ),
                    "data": data,
                }
            )

    return charts


def _build_correlation_chart(
    context: DatasetContext,
) -> dict[str, Any] | None:
    """
    Generate a correlation matrix for genuinely
    numeric columns.
    """

    numeric_columns = context.numeric_columns()

    if len(numeric_columns) < 2:
        return None

    numeric_df = context.df[
        numeric_columns
    ].apply(
        pd.to_numeric,
        errors="coerce",
    )

    correlation = numeric_df.corr()

    data: list[dict[str, Any]] = []

    for column in numeric_columns:

        for other_column in numeric_columns:

            value = correlation.loc[
                column,
                other_column,
            ]

            if pd.isna(value):
                continue

            data.append(
                {
                    "x": column,
                    "y": other_column,
                    "correlation": _round_value(
                        value,
                        digits=4,
                    ),
                }
            )

    if not data:
        return None

    return {
        "type": "heatmap",
        "chart_id": "numeric_correlation",
        "title": "Numeric column correlation",
        "x_axis": "Column",
        "y_axis": "Column",
        "data": data,
    }


def generate_visualizations(
    context: DatasetContext,
) -> dict[str, Any]:
    """
    Generate dashboard-ready visualization metadata
    from a shared DatasetContext.

    The function does not return raw dataset rows.

    Visualization groups:
        - KPI summaries
        - Categorical distributions
        - Numeric distributions
        - Time-series charts
        - Correlation heatmap
    """

    numeric_kpis = _build_numeric_kpis(
        context
    )

    categorical_charts = (
        _build_categorical_charts(
            context
        )
    )

    numeric_distribution_charts = (
        _build_numeric_distributions(
            context
        )
    )

    datetime_charts = (
        _build_datetime_charts(
            context
        )
    )

    correlation_chart = (
        _build_correlation_chart(
            context
        )
    )

    charts = (
        categorical_charts
        + numeric_distribution_charts
        + datetime_charts
    )

    if correlation_chart is not None:
        charts.append(
            correlation_chart
        )

    return {
        "row_count": context.row_count,
        "column_count": context.column_count,
        "numeric_columns": (
            context.numeric_columns()
        ),
        "categorical_columns": (
            context.categorical_columns()
        ),
        "datetime_columns": (
            context.datetime_columns()
        ),
        "kpis": numeric_kpis,
        "chart_count": len(charts),
        "charts": charts,
    }