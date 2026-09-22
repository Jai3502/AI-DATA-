
from app.data_engine.context import DatasetContext
from app.data_engine.eda import generate_eda
from app.data_engine.outliers import analyze_outliers
from app.data_engine.quality import analyze_data_quality


def generate_insights(
    context: DatasetContext,
) -> dict:
    """
    Generate safe, aggregated business insights
    from a shared DatasetContext.

    Raw dataset rows are NOT returned.
    """

    df = context.df

    eda_result = generate_eda(
        context=context,
    )

    quality_result = analyze_data_quality(
        context=context,
    )

    outlier_result = analyze_outliers(
        context=context,
    )

    insights = []

    # ---------------------------------------------------------
    # Dataset overview
    # ---------------------------------------------------------

    insights.append(
        {
            "type": "overview",
            "title": "Dataset overview",
            "message": (
                f"The dataset contains "
                f"{context.row_count:,} rows and "
                f"{context.column_count} columns."
            ),
        }
    )

    # ---------------------------------------------------------
    # Missing data insights
    # ---------------------------------------------------------

    total_missing = quality_result[
        "missing_values"
    ]["total_missing_values"]

    if total_missing == 0:

        insights.append(
            {
                "type": "data_quality",
                "title": "No missing values detected",
                "message": (
                    "No missing values were detected "
                    "in the analyzed dataset."
                ),
            }
        )

    else:

        insights.append(
            {
                "type": "data_quality",
                "title": "Missing values detected",
                "message": (
                    f"{total_missing:,} missing values "
                    "were detected across the dataset."
                ),
            }
        )

    # ---------------------------------------------------------
    # Duplicate insights
    # ---------------------------------------------------------

    duplicate_count = quality_result[
        "duplicates"
    ]["duplicate_row_count"]

    if duplicate_count == 0:

        insights.append(
            {
                "type": "data_quality",
                "title": "No duplicate rows detected",
                "message": (
                    "No fully duplicated rows were "
                    "detected in the analyzed dataset."
                ),
            }
        )

    else:

        insights.append(
            {
                "type": "data_quality",
                "title": "Duplicate rows detected",
                "message": (
                    f"{duplicate_count:,} duplicate rows "
                    f"were detected."
                ),
            }
        )

    # ---------------------------------------------------------
    # Quality score
    # ---------------------------------------------------------

    quality_score = quality_result[
        "quality_score"
    ]

    insights.append(
        {
            "type": "data_quality",
            "title": "Data quality score",
            "message": (
                f"The calculated data quality score "
                f"is {quality_score:.2f} out of 100."
            ),
        }
    )

    # ---------------------------------------------------------
    # Numeric insights
    # ---------------------------------------------------------

    numeric_summary = eda_result[
        "numeric_summary"
    ]

    for column, summary in numeric_summary.items():

        if summary["mean"] is None:
            continue

        insights.append(
            {
                "type": "numeric_summary",
                "column": column,
                "title": f"{column} distribution",
                "message": (
                    f"{column} has a mean of "
                    f"{summary['mean']:.2f}, "
                    f"a median of "
                    f"{summary['median']:.2f}, "
                    f"with values ranging from "
                    f"{summary['min']:.2f} to "
                    f"{summary['max']:.2f}."
                ),
            }
        )

    # ---------------------------------------------------------
    # Outlier insights
    # ---------------------------------------------------------

    for column, result in (
        outlier_result["outliers"].items()
    ):

        outlier_count = result[
            "outlier_count"
        ]

        if outlier_count == 0:
            continue

        insights.append(
            {
                "type": "outlier",
                "column": column,
                "title": (
                    f"Potential outliers in {column}"
                ),
                "message": (
                    f"{outlier_count:,} potential "
                    f"outlier observations were detected "
                    f"in {column}, representing "
                    f"{result['outlier_percentage']:.2f}% "
                    f"of analyzed observations."
                ),
                "severity": result["severity"],
            }
        )

    # ---------------------------------------------------------
    # Correlation insights
    # ---------------------------------------------------------

    correlation = eda_result[
        "correlation"
    ]

    processed_pairs = set()

    for column, values in correlation.items():

        for other_column, value in values.items():

            if value is None:
                continue

            if column == other_column:
                continue

            pair = tuple(
                sorted(
                    [column, other_column]
                )
            )

            if pair in processed_pairs:
                continue

            processed_pairs.add(pair)

            absolute_correlation = abs(value)

            if absolute_correlation >= 0.70:

                relationship = (
                    "strong positive"
                    if value > 0
                    else "strong negative"
                )

                insights.append(
                    {
                        "type": "correlation",
                        "columns": [
                            column,
                            other_column,
                        ],
                        "title": (
                            f"Strong correlation between "
                            f"{column} and "
                            f"{other_column}"
                        ),
                        "message": (
                            f"{column} and "
                            f"{other_column} show a "
                            f"{relationship} correlation "
                            f"of {value:.2f}."
                        ),
                    }
                )

    return {
        "row_count": context.row_count,
        "column_count": context.column_count,
        "insight_count": len(insights),
        "insights": insights,
    }