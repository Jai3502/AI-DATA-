from app.data_engine.context import DatasetContext


def generate_eda(
    context: DatasetContext,
) -> dict:
    """
    Generate semantic-type-aware EDA metadata.

    The dataset is loaded once through DatasetContext.

    Raw dataset rows are NOT returned.
    """

    df = context.df

    semantic_types = context.semantic_types()

    numeric_columns = [
        column
        for column, semantic_type
        in semantic_types.items()
        if semantic_type == "numeric"
    ]

    categorical_columns = [
        column
        for column, semantic_type
        in semantic_types.items()
        if semantic_type == "categorical"
    ]

    datetime_columns = [
        column
        for column, semantic_type
        in semantic_types.items()
        if semantic_type == "datetime"
    ]

    numeric_summary = {}

    for column in numeric_columns:

        series = df[column]

        numeric_summary[column] = {
            "mean": (
                float(series.mean())
                if not series.dropna().empty
                else None
            ),
            "median": (
                float(series.median())
                if not series.dropna().empty
                else None
            ),
            "min": (
                float(series.min())
                if not series.dropna().empty
                else None
            ),
            "max": (
                float(series.max())
                if not series.dropna().empty
                else None
            ),
            "std": (
                float(series.std())
                if not series.dropna().empty
                else None
            ),
        }

    categorical_summary = {}

    for column in categorical_columns:

        series = df[column]

        categorical_summary[column] = {
            "unique_count": int(
                series.nunique(
                    dropna=True
                )
            ),
            "missing_count": int(
                series.isna().sum()
            ),
        }

    datetime_summary = {}

    for column in datetime_columns:

        series = df[column]

        datetime_summary[column] = {
            "unique_count": int(
                series.nunique(
                    dropna=True
                )
            ),
            "missing_count": int(
                series.isna().sum()
            ),
        }

    missing_summary = {}

    for column in df.columns:

        missing_count = int(
            df[column].isna().sum()
        )

        missing_summary[str(column)] = {
            "missing_count": missing_count,
            "missing_percentage": round(
                float(
                    df[column].isna().mean() * 100
                ),
                2,
            ),
        }

    correlation = {}

    if len(numeric_columns) >= 2:

        correlation_df = df[
            numeric_columns
        ].corr()

        correlation = {
            str(column): {
                str(other_column): (
                    None
                    if value != value
                    else round(
                        float(value),
                        4,
                    )
                )
                for other_column, value
                in row.items()
            }
            for column, row
            in correlation_df.to_dict().items()
        }

    return {
        "row_count": context.row_count,
        "column_count": context.column_count,

        "numeric_columns": numeric_columns,

        "categorical_columns": (
            categorical_columns
        ),

        "datetime_columns": datetime_columns,

        "numeric_summary": numeric_summary,

        "categorical_summary": (
            categorical_summary
        ),

        "datetime_summary": datetime_summary,

        "missing_summary": missing_summary,

        "correlation": correlation,
    }