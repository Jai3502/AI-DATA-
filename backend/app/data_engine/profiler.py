from pathlib import Path

import pandas as pd


MAX_PROFILE_ROWS = 100_000


def load_dataset(
    file_path: str,
    file_type: str,
) -> pd.DataFrame:
    """
    Load a supported dataset into a pandas DataFrame.

    Only intended for server-side processing of private uploaded files.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError("Dataset file not found.")

    file_type = file_type.lower().strip()

    if file_type == "csv":
        df = pd.read_csv(
            path,
            nrows=MAX_PROFILE_ROWS,
        )

    elif file_type in {"xlsx", "xls"}:
        df = pd.read_excel(
            path,
            nrows=MAX_PROFILE_ROWS,
        )

    else:
        raise ValueError("Unsupported dataset file type.")

    return df


def detect_column_type(
    series: pd.Series,
    column_name: str,
) -> str:
    """
    Detect a practical semantic type for a dataset column.

    Returns one of:
    - numeric
    - datetime
    - binary
    - categorical
    - text
    - identifier
    """

    column_name_lower = column_name.strip().lower()

    # Numeric columns
    if pd.api.types.is_numeric_dtype(series):

        unique_values = series.dropna().unique()

        # Binary numeric columns
        if len(unique_values) == 2:
            return "binary"

        # Identifier-like integer columns
        if (
            pd.api.types.is_integer_dtype(series)
            and series.nunique(dropna=True) >= 10
        ):
            return "identifier"

        return "numeric"

    # Datetime columns already recognized by pandas
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"

    # String / object columns
    if (
        pd.api.types.is_object_dtype(series)
        or pd.api.types.is_string_dtype(series)
    ):

        non_null = series.dropna()

        if not non_null.empty:

            date_keywords = {
                "date",
                "datetime",
                "timestamp",
                "time",
                "created_at",
                "updated_at",
                "start_date",
                "end_date",
            }

            has_date_name = any(
                keyword in column_name_lower
                for keyword in date_keywords
            )

            # Explicitly test common date formats
            date_formats = [
                "%d-%m-%Y",
                "%d/%m/%Y",
                "%Y-%m-%d",
                "%Y/%m/%d",
                "%m-%d-%Y",
                "%m/%d/%Y",
            ]

            for date_format in date_formats:

                parsed_dates = pd.to_datetime(
                    non_null,
                    format=date_format,
                    errors="coerce",
                )

                parse_success_rate = float(
                    parsed_dates.notna().mean()
                )

                if parse_success_rate >= 0.90:
                    return "datetime"

            # Fallback parser
            parsed_dates = pd.to_datetime(
                non_null,
                errors="coerce",
                dayfirst=True,
            )

            parse_success_rate = float(
                parsed_dates.notna().mean()
            )

            if has_date_name and parse_success_rate >= 0.80:
                return "datetime"

            if parse_success_rate >= 0.90:
                return "datetime"

        # Low-cardinality string -> categorical
        unique_count = series.nunique(
            dropna=True
        )

        if unique_count <= 50:
            return "categorical"

        return "text"

    return "categorical"


def profile_dataset(
    file_path: str,
    file_type: str,
) -> dict:
    """
    Generate safe metadata/profile information for a dataset.

    Raw cell values are NOT returned.
    """

    df = load_dataset(
        file_path=file_path,
        file_type=file_type,
    )

    columns = []

    for column in df.columns:

        series = df[column]

        columns.append(
            {
                "name": str(column),
                "dtype": str(series.dtype),
                "semantic_type": detect_column_type(
                    series=series,
                    column_name=str(column),
                ),
                "missing_count": int(
                    series.isna().sum()
                ),
                "missing_percentage": round(
                    float(
                        series.isna().mean() * 100
                    ),
                    2,
                ),
                "unique_count": int(
                    series.nunique(
                        dropna=True
                    )
                ),
            }
        )

    return {
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "columns": columns,
    }