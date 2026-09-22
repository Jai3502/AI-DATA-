import pandas as pd

from app.data_engine.context import DatasetContext


def analyze_data_quality(
    context: DatasetContext,
) -> dict:
    """
    Analyze dataset quality using a shared DatasetContext.

    Raw dataset rows are NOT returned.
    """

    df = context.df

    row_count = context.row_count
    column_count = context.column_count

    # ---------------------------------------------------------
    # Missing values
    # ---------------------------------------------------------

    missing_columns = {}

    for column in df.columns:

        missing_count = int(
            df[column].isna().sum()
        )

        if missing_count > 0:

            missing_columns[str(column)] = {
                "missing_count": missing_count,
                "missing_percentage": round(
                    float(
                        missing_count
                        / row_count
                        * 100
                    ),
                    2,
                ),
            }

    total_missing_values = int(
        df.isna().sum().sum()
    )

    # ---------------------------------------------------------
    # Duplicate rows
    # ---------------------------------------------------------

    duplicate_row_count = int(
        df.duplicated().sum()
    )

    duplicate_percentage = (
        round(
            float(
                duplicate_row_count
                / row_count
                * 100
            ),
            2,
        )
        if row_count > 0
        else 0.0
    )

    # ---------------------------------------------------------
    # Constant columns
    # ---------------------------------------------------------

    constant_columns = []

    for column in df.columns:

        unique_count = int(
            df[column].nunique(
                dropna=False
            )
        )

        if unique_count <= 1:

            constant_columns.append(
                str(column)
            )

    # ---------------------------------------------------------
    # High-cardinality columns
    # ---------------------------------------------------------

    high_cardinality_columns = {}

    for column in df.columns:

        column_dtype = df[column].dtype

        if (
            not pd.api.types.is_object_dtype(
                column_dtype
            )
            and not pd.api.types.is_string_dtype(
                column_dtype
            )
        ):
            continue

        unique_count = int(
            df[column].nunique(
                dropna=True
            )
        )

        unique_percentage = (
            (
                unique_count
                / row_count
            ) * 100
            if row_count > 0
            else 0.0
        )

        if (
            unique_percentage >= 90
            and unique_count > 50
        ):

            high_cardinality_columns[
                str(column)
            ] = {
                "unique_count": unique_count,
                "unique_percentage": round(
                    float(
                        unique_percentage
                    ),
                    2,
                ),
            }

    # ---------------------------------------------------------
    # Empty rows
    # ---------------------------------------------------------

    completely_empty_rows = int(
        df.isna().all(axis=1).sum()
    )

    # ---------------------------------------------------------
    # Quality score
    # ---------------------------------------------------------

    quality_score = 100.0

    if (
        row_count > 0
        and column_count > 0
    ):

        missing_percentage = (
            total_missing_values
            / (
                row_count
                * column_count
            )
        ) * 100

        quality_score -= min(
            missing_percentage,
            40,
        )

        quality_score -= min(
            duplicate_percentage,
            20,
        )

    quality_score -= min(
        len(constant_columns) * 5,
        20,
    )

    quality_score = round(
        max(
            quality_score,
            0.0,
        ),
        2,
    )

    # ---------------------------------------------------------
    # Final result
    # ---------------------------------------------------------

    return {
        "row_count": row_count,
        "column_count": column_count,

        "missing_values": {
            "total_missing_values": (
                total_missing_values
            ),
            "columns_with_missing_values": (
                missing_columns
            ),
        },

        "duplicates": {
            "duplicate_row_count": (
                duplicate_row_count
            ),
            "duplicate_percentage": (
                duplicate_percentage
            ),
        },

        "constant_columns": (
            constant_columns
        ),

        "high_cardinality_columns": (
            high_cardinality_columns
        ),

        "completely_empty_rows": (
            completely_empty_rows
        ),

        "quality_score": quality_score,
    }