from app.data_engine.context import DatasetContext
from app.data_engine.eda import generate_eda
from app.data_engine.insights import generate_insights
from app.data_engine.outliers import analyze_outliers
from app.data_engine.profiler import profile_dataset
from app.data_engine.quality import analyze_data_quality
from app.data_engine.recommendations import generate_recommendations


def analyze_dataset(
    file_path: str,
    file_type: str,
) -> dict:
    """
    Run the complete dataset analysis pipeline
    using a shared DatasetContext.

    The dataset is loaded once and reused across
    all analysis modules.

    Raw dataset rows and raw cell values are NOT
    returned from the final analysis result.
    """

    # ---------------------------------------------------------
    # Create shared dataset context
    # ---------------------------------------------------------

    context = DatasetContext(
        file_path=file_path,
        file_type=file_type,
    )

    # ---------------------------------------------------------
    # Dataset profile
    # ---------------------------------------------------------

    profile_result = profile_dataset(
        file_path=file_path,
        file_type=file_type,
    )

    # ---------------------------------------------------------
    # Exploratory data analysis
    # ---------------------------------------------------------

    eda_result = generate_eda(
        context=context,
    )

    # ---------------------------------------------------------
    # Data quality
    # ---------------------------------------------------------

    quality_result = analyze_data_quality(
        context=context,
    )

    # ---------------------------------------------------------
    # Outlier detection
    # ---------------------------------------------------------

    outlier_result = analyze_outliers(
        context=context,
    )

    # ---------------------------------------------------------
    # Automated insights
    # ---------------------------------------------------------

    insight_result = generate_insights(
        context=context,
    )

    # ---------------------------------------------------------
    # Business recommendations
    # ---------------------------------------------------------

    recommendation_result = (
        generate_recommendations(
            context=context,
        )
    )

    # ---------------------------------------------------------
    # Unified analysis result
    # ---------------------------------------------------------

    return {
        "dataset": {
            "row_count": profile_result[
                "row_count"
            ],
            "column_count": profile_result[
                "column_count"
            ],
            "columns": profile_result[
                "columns"
            ],
        },

        "eda": eda_result,

        "quality": quality_result,

        "outliers": outlier_result,

        "insights": {
            "insight_count": (
                insight_result[
                    "insight_count"
                ]
            ),
            "items": insight_result[
                "insights"
            ],
        },

        "recommendations": {
            "recommendation_count": (
                recommendation_result[
                    "recommendation_count"
                ]
            ),
            "items": (
                recommendation_result[
                    "recommendations"
                ]
            ),
        },
    }