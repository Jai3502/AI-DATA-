from __future__ import annotations

from typing import Any


def generate_analysis_response(
    tool_name: str,
    result: dict[str, Any],
) -> str:
    """
    Convert a controlled analysis result into a
    concise, human-readable business response.

    This layer does not perform any data analysis.
    It only formats already-computed results.

    Security:
    - Does not access the dataset.
    - Does not execute Python, SQL, shell commands,
      or filesystem operations.
    - Uses only aggregated tool results.
    """

    if tool_name == "outlier_analysis":
        return _format_outlier_response(result)

    if tool_name == "data_quality":
        return _format_quality_response(result)

    if tool_name == "numeric_statistics":
        return _format_numeric_statistics_response(
            result
        )

    if tool_name == "dataset_insights":
        return _format_insights_response(result)

    if tool_name == "dataset_overview":
        return _format_overview_response(result)

    return (
        "The analysis was completed, but a "
        "readable response could not be generated."
    )


def _format_outlier_response(
    result: dict[str, Any],
) -> str:
    total_outliers = int(
        result.get("total_outlier_count", 0)
    )

    row_count = int(
        result.get("row_count", 0)
    )

    columns = result.get(
        "columns",
        [],
    )

    response = (
        f"The dataset contains {row_count:,} rows "
        f"and {total_outliers:,} potential outlier "
        f"observations across its numeric columns."
    )

    significant_columns = [
        column
        for column in columns
        if int(
            column.get(
                "outlier_count",
                0,
            )
        )
        > 0
    ]

    if not significant_columns:
        return (
            response
            + " No potential outliers were detected."
        )

    response += "\n\nOutlier breakdown:"

    for column in significant_columns:
        name = column.get(
            "column",
            "Unknown",
        )

        count = int(
            column.get(
                "outlier_count",
                0,
            )
        )

        percentage = float(
            column.get(
                "outlier_percentage",
                0.0,
            )
        )

        severity = column.get(
            "severity",
            "none",
        )

        response += (
            f"\n• {name}: {count:,} "
            f"({percentage:.2f}%) "
            f"— {severity} severity"
        )

    return response


def _format_quality_response(
    result: dict[str, Any],
) -> str:
    quality_score = result.get(
        "quality_score"
    )

    missing_values = result.get(
        "missing_values",
        {},
    )

    issues = result.get(
        "issues",
        [],
    )

    total_missing = int(
        missing_values.get(
            "total_missing_values",
            0,
        )
    )

    response = (
        f"The calculated data quality score is "
        f"{float(quality_score):.2f} out of 100."
    )

    if total_missing == 0:
        response += (
            " No missing values were detected."
        )
    else:
        response += (
            f" {total_missing:,} missing values "
            f"were detected."
        )

    if issues:
        response += (
            f" {len(issues)} data-quality issue(s) "
            f"were identified."
        )
    else:
        response += (
            " No additional data-quality issues "
            "were reported."
        )

    return response


def _format_numeric_statistics_response(
    result: dict[str, Any],
) -> str:
    statistics = result.get(
        "statistics",
        [],
    )

    if not statistics:
        return (
            "No numeric statistics were available "
            "for this dataset."
        )

    response = (
        f"Statistical summaries are available for "
        f"{len(statistics)} numeric columns."
    )

    for item in statistics:
        column = item.get(
            "column",
            "Unknown",
        )

        mean = float(
            item.get(
                "mean",
                0.0,
            )
        )

        median = float(
            item.get(
                "median",
                0.0,
            )
        )

        minimum = float(
            item.get(
                "minimum",
                0.0,
            )
        )

        maximum = float(
            item.get(
                "maximum",
                0.0,
            )
        )

        response += (
            f"\n\n• {column}"
            f"\n  Mean: {mean:,.2f}"
            f"\n  Median: {median:,.2f}"
            f"\n  Minimum: {minimum:,.2f}"
            f"\n  Maximum: {maximum:,.2f}"
        )

    return response


def _format_insights_response(
    result: dict[str, Any],
) -> str:
    insights = result.get(
        "insights",
        [],
    )

    if not insights:
        return (
            "No significant insights were generated "
            "for this dataset."
        )

    response = (
        f"I found {len(insights)} dataset insights:"
    )

    for insight in insights:
        title = insight.get(
            "title",
            "Insight",
        )

        message = insight.get(
            "message",
            "",
        )

        response += (
            f"\n\n• {title}: {message}"
        )

    return response


def _format_overview_response(
    result: dict[str, Any],
) -> str:
    row_count = int(
        result.get(
            "row_count",
            0,
        )
    )

    column_count = int(
        result.get(
            "column_count",
            0,
        )
    )

    columns = result.get(
        "columns",
        [],
    )

    numeric_columns = result.get(
        "numeric_columns",
        [],
    )

    categorical_columns = result.get(
        "categorical_columns",
        [],
    )

    datetime_columns = result.get(
        "datetime_columns",
        [],
    )

    return (
        f"The dataset contains {row_count:,} rows "
        f"and {column_count:,} columns.\n\n"
        f"Columns: {', '.join(columns)}\n\n"
        f"Numeric columns: "
        f"{len(numeric_columns)}\n"
        f"Categorical columns: "
        f"{len(categorical_columns)}\n"
        f"Datetime columns: "
        f"{len(datetime_columns)}"
    )