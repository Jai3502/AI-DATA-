import pandas as pd

from app.data_engine.profiler import load_dataset


def generate_eda(
    file_path: str,
    file_type: str,
) -> dict:
    """
    Generate safe, aggregated EDA metadata.

    Raw dataset rows are NOT returned.
    """

    df = load_dataset(
        file_path=file_path,
        file_type=file_type,
    )

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns.tolist()

    categorical_columns = df.select_dtypes(
        exclude="number"
    ).columns.tolist()

    numeric_summary = {}

    for column in numeric_columns:
        series = df[column]

        numeric_summary[str(column)] = {
            "mean": float(series.mean())
            if not series.dropna().empty
            else None,

            "median": float(series.median())
            if not series.dropna().empty
            else None,

            "min": float(series.min())
            if not series.dropna().empty
            else None,

            "max": float(series.max())
            if not series.dropna().empty
            else None,

            "std": float(series.std())
            if not series.dropna().empty
            else None,
        }

    categorical_summary = {}

    for column in categorical_columns:
        series = df[column]

        categorical_summary[str(column)] = {
            "unique_count": int(
                series.nunique(dropna=True)
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
        correlation_df = df[numeric_columns].corr()

        correlation = {
            str(column): {
                str(other_column): (
                    None
                    if pd.isna(value)
                    else round(float(value), 4)
                )
                for other_column, value in row.items()
            }
            for column, row in correlation_df.to_dict().items()
        }

    return {
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "numeric_columns": [
            str(column)
            for column in numeric_columns
        ],
        "categorical_columns": [
            str(column)
            for column in categorical_columns
        ],
        "numeric_summary": numeric_summary,
        "categorical_summary": categorical_summary,
        "missing_summary": missing_summary,
        "correlation": correlation,
    }