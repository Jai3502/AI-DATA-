from __future__ import annotations

from typing import Any

from app.data_engine.context import DatasetContext
from app.data_engine.insights import generate_insights
from app.data_engine.outliers import analyze_outliers
from app.data_engine.quality import analyze_data_quality


def get_dataset_overview(
    context: DatasetContext,
) -> dict[str, Any]:
    """
    Return safe high-level dataset metadata.

    This tool does not expose raw dataset rows.
    """

    return {
        "row_count": context.row_count,
        "column_count": context.column_count,
        "columns": context.columns,
        "numeric_columns": context.numeric_columns(),
        "categorical_columns": context.categorical_columns(),
        "datetime_columns": context.datetime_columns(),
        "identifier_columns": context.identifier_columns(),
        "binary_columns": context.binary_columns(),
        "text_columns": context.text_columns(),
    }


def get_data_quality(
    context: DatasetContext,
) -> dict[str, Any]:
    """
    Return aggregated data-quality information.

    No raw dataset rows are returned.
    """

    result = analyze_data_quality(
        context=context
    )

    return {
        "quality_score": result.get(
            "quality_score"
        ),
        "missing_values": result.get(
            "missing_values"
        ),
        "duplicate_rows": result.get(
            "duplicate_rows"
        ),
        "issues": result.get(
            "issues",
            [],
        ),
    }


def get_outlier_analysis(
    context: DatasetContext,
) -> dict[str, Any]:
    """
    Return aggregated outlier information.

    Raw rows are never returned.
    """

    result = analyze_outliers(
        context=context
    )

    outliers = result.get(
        "outliers",
        {}
    )

    total_outliers = sum(
        int(
            details.get(
                "outlier_count",
                0,
            )
        )
        for details in outliers.values()
    )

    columns = []

    for column, details in outliers.items():
        columns.append(
            {
                "column": column,
                "outlier_count": int(
                    details.get(
                        "outlier_count",
                        0,
                    )
                ),
                "outlier_percentage": float(
                    details.get(
                        "outlier_percentage",
                        0.0,
                    )
                ),
                "severity": details.get(
                    "severity",
                    "none",
                ),
            }
        )

    return {
        "row_count": result.get(
            "row_count"
        ),
        "numeric_column_count": result.get(
            "numeric_column_count"
        ),
        "total_outlier_count": total_outliers,
        "columns": columns,
    }


def get_dataset_insights(
    context: DatasetContext,
) -> dict[str, Any]:
    """
    Return generated business/data insights.

    This tool returns aggregated insights only.
    """

    result = generate_insights(
        context=context
    )

    return {
        "insight_count": result.get(
            "insight_count",
            0,
        ),
        "insights": result.get(
            "insights",
            [],
        ),
    }


def get_numeric_statistics(
    context: DatasetContext,
) -> dict[str, Any]:
    """
    Return statistical summaries for
    semantic numeric columns.

    No raw dataset rows are returned.
    """

    statistics: list[dict[str, Any]] = []

    for column in context.numeric_columns():

        series = context.df[column]

        numeric_series = series.copy()

        try:
            numeric_series = (
                numeric_series.astype(
                    "float64"
                )
            )

        except (
            TypeError,
            ValueError,
        ):
            continue

        numeric_series = (
            numeric_series.dropna()
        )

        if numeric_series.empty:
            continue

        statistics.append(
            {
                "column": column,
                "count": int(
                    numeric_series.count()
                ),
                "mean": float(
                    numeric_series.mean()
                ),
                "median": float(
                    numeric_series.median()
                ),
                "minimum": float(
                    numeric_series.min()
                ),
                "maximum": float(
                    numeric_series.max()
                ),
                "standard_deviation": float(
                    numeric_series.std()
                ),
            }
        )

    return {
        "statistics": statistics,
    }