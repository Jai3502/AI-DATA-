import pandas as pd

from app.data_engine.context import DatasetContext


def detect_outliers_iqr(
    series: pd.Series,
) -> dict:
    """
    Detect potential outliers using the IQR method.

    Returns aggregated statistics only.
    Raw rows/values are NOT returned.
    """

    numeric_series = pd.to_numeric(
        series,
        errors="coerce",
    ).dropna()

    if numeric_series.empty:

        return {
            "outlier_count": 0,
            "outlier_percentage": 0.0,
            "lower_bound": None,
            "upper_bound": None,
            "severity": "none",
        }

    q1 = float(
        numeric_series.quantile(0.25)
    )

    q3 = float(
        numeric_series.quantile(0.75)
    )

    iqr = q3 - q1

    lower_bound = q1 - (1.5 * iqr)

    upper_bound = q3 + (1.5 * iqr)

    outlier_mask = (
        (numeric_series < lower_bound)
        | (numeric_series > upper_bound)
    )

    outlier_count = int(
        outlier_mask.sum()
    )

    total_count = len(
        numeric_series
    )

    outlier_percentage = (
        (
            outlier_count
            / total_count
        )
        * 100
        if total_count > 0
        else 0.0
    )

    if outlier_percentage == 0:

        severity = "none"

    elif outlier_percentage < 1:

        severity = "low"

    elif outlier_percentage < 5:

        severity = "medium"

    else:

        severity = "high"

    return {
        "outlier_count": outlier_count,
        "outlier_percentage": round(
            float(
                outlier_percentage
            ),
            2,
        ),
        "lower_bound": round(
            lower_bound,
            4,
        ),
        "upper_bound": round(
            upper_bound,
            4,
        ),
        "severity": severity,
    }


def analyze_outliers(
    context: DatasetContext,
) -> dict:
    """
    Analyze potential outliers across
    semantically numeric columns.

    Identifier, binary, datetime,
    categorical, and text columns
    are excluded.

    Raw dataset rows are NOT returned.
    """

    df = context.df

    numeric_columns = (
        context.numeric_columns()
    )

    outliers = {}

    analyzed_columns = []

    skipped_columns = {}

    semantic_types = (
        context.semantic_types()
    )

    for column in df.columns:

        column_name = str(column)

        semantic_type = semantic_types[
            column_name
        ]

        if semantic_type == "numeric":

            outliers[column_name] = (
                detect_outliers_iqr(
                    df[column]
                )
            )

            analyzed_columns.append(
                column_name
            )

        else:

            skipped_columns[
                column_name
            ] = {
                "semantic_type": (
                    semantic_type
                ),
                "reason": (
                    "IQR outlier detection "
                    "is not applicable to "
                    "this column type."
                ),
            }

    return {
        "row_count": context.row_count,

        "numeric_column_count": len(
            numeric_columns
        ),

        "analyzed_columns": (
            analyzed_columns
        ),

        "skipped_columns": (
            skipped_columns
        ),

        "outliers": outliers,
    }