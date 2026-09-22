from app.data_engine.context import DatasetContext
from app.data_engine.insights import generate_insights


def generate_recommendations(
    context: DatasetContext,
) -> dict:
    """
    Generate business-oriented recommendations
    from aggregated dataset insights.

    Raw dataset rows and raw cell values
    are NOT returned.
    """

    insight_result = generate_insights(
        context=context,
    )

    recommendations = []

    insights = insight_result["insights"]

    # ---------------------------------------------------------
    # Data quality recommendations
    # ---------------------------------------------------------

    quality_score = None

    for insight in insights:

        if insight["type"] != "data_quality":
            continue

        if insight["title"] != "Data quality score":
            continue

        message = insight["message"]

        try:
            quality_score = float(
                message.split("is ")[1]
                .split(" out of")[0]
            )
        except (IndexError, ValueError):
            quality_score = None

    if quality_score is not None:

        if quality_score >= 95:

            recommendations.append(
                {
                    "type": "data_quality",
                    "priority": "low",
                    "title": "Maintain current data quality",
                    "recommendation": (
                        "The dataset currently has a strong "
                        "calculated quality score. Continue "
                        "using validation checks during future "
                        "data uploads."
                    ),
                }
            )

        elif quality_score >= 80:

            recommendations.append(
                {
                    "type": "data_quality",
                    "priority": "medium",
                    "title": "Improve data quality",
                    "recommendation": (
                        "Review missing values, duplicate "
                        "records, and other quality issues "
                        "before using the dataset for "
                        "business-critical analysis."
                    ),
                }
            )

        else:

            recommendations.append(
                {
                    "type": "data_quality",
                    "priority": "high",
                    "title": "Prioritize data quality cleanup",
                    "recommendation": (
                        "Significant data quality issues may "
                        "affect downstream analysis. Clean "
                        "and validate the dataset before "
                        "relying on analytical results."
                    ),
                }
            )

    # ---------------------------------------------------------
    # Missing value recommendations
    # ---------------------------------------------------------

    for insight in insights:

        if (
            insight["type"] == "data_quality"
            and insight["title"]
            == "Missing values detected"
        ):

            recommendations.append(
                {
                    "type": "missing_values",
                    "priority": "high",
                    "title": "Review missing data",
                    "recommendation": (
                        "Identify the affected columns and "
                        "determine whether missing values "
                        "should be imputed, removed, or "
                        "retained based on business context."
                    ),
                }
            )

    # ---------------------------------------------------------
    # Duplicate recommendations
    # ---------------------------------------------------------

    for insight in insights:

        if (
            insight["type"] == "data_quality"
            and insight["title"]
            == "Duplicate rows detected"
        ):

            recommendations.append(
                {
                    "type": "duplicates",
                    "priority": "medium",
                    "title": "Review duplicate records",
                    "recommendation": (
                        "Investigate duplicate records and "
                        "define a reliable deduplication rule "
                        "before downstream reporting."
                    ),
                }
            )

    # ---------------------------------------------------------
    # Outlier recommendations
    # ---------------------------------------------------------

    for insight in insights:

        if insight["type"] != "outlier":
            continue

        severity = insight.get(
            "severity",
            "none",
        )

        column = insight.get(
            "column",
            "the affected column",
        )

        if severity == "high":

            recommendations.append(
                {
                    "type": "outlier",
                    "priority": "high",
                    "title": (
                        f"Investigate outliers in "
                        f"{column}"
                    ),
                    "recommendation": (
                        f"A relatively high proportion of "
                        f"potentially unusual observations "
                        f"was detected in {column}. "
                        f"Investigate the underlying business "
                        f"context before removing or modifying "
                        f"these records."
                    ),
                }
            )

        elif severity == "medium":

            recommendations.append(
                {
                    "type": "outlier",
                    "priority": "medium",
                    "title": (
                        f"Review outliers in "
                        f"{column}"
                    ),
                    "recommendation": (
                        f"Potentially unusual observations "
                        f"were detected in {column}. Review "
                        f"these observations to determine "
                        f"whether they represent legitimate "
                        f"business events or data-quality "
                        f"issues."
                    ),
                }
            )

        elif severity == "low":

            recommendations.append(
                {
                    "type": "outlier",
                    "priority": "low",
                    "title": (
                        f"Monitor outliers in "
                        f"{column}"
                    ),
                    "recommendation": (
                        f"A small number of potentially "
                        f"unusual observations were detected "
                        f"in {column}. Monitor them during "
                        f"future analysis without automatically "
                        f"removing them."
                    ),
                }
            )

    # ---------------------------------------------------------
    # Correlation recommendations
    # ---------------------------------------------------------

    for insight in insights:

        if insight["type"] != "correlation":
            continue

        columns = insight.get(
            "columns",
            [],
        )

        if len(columns) != 2:
            continue

        first_column = columns[0]
        second_column = columns[1]

        recommendations.append(
            {
                "type": "correlation",
                "priority": "medium",
                "title": (
                    f"Investigate relationship between "
                    f"{first_column} and "
                    f"{second_column}"
                ),
                "recommendation": (
                    f"The analysis identified a strong "
                    f"relationship between {first_column} "
                    f"and {second_column}. Investigate the "
                    f"business relationship further before "
                    f"interpreting the correlation as a "
                    f"causal relationship."
                ),
            }
        )

    # ---------------------------------------------------------
    # General analytical recommendation
    # ---------------------------------------------------------

    if not recommendations:

        recommendations.append(
            {
                "type": "general",
                "priority": "low",
                "title": "Continue exploratory analysis",
                "recommendation": (
                    "The current automated checks did not "
                    "identify major issues requiring immediate "
                    "action. Continue with business-specific "
                    "analysis and monitoring."
                ),
            }
        )

    # ---------------------------------------------------------
    # Priority ordering
    # ---------------------------------------------------------

    priority_order = {
        "high": 1,
        "medium": 2,
        "low": 3,
    }

    recommendations.sort(
        key=lambda item: priority_order.get(
            item["priority"],
            99,
        )
    )

    # ---------------------------------------------------------
    # Final result
    # ---------------------------------------------------------

    return {
        "row_count": context.row_count,
        "column_count": context.column_count,
        "recommendation_count": len(
            recommendations
        ),
        "recommendations": recommendations,
    }