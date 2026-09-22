from pathlib import Path

import pandas as pd

from app.data_engine.profiler import (
    detect_column_type,
    load_dataset,
)


class DatasetContext:
    """
    Shared analysis context for a single dataset.

    The dataset is loaded once and reused by the
    analysis pipeline.

    Raw data remains in server-side memory only and
    is never returned directly from this context.
    """

    def __init__(
        self,
        file_path: str,
        file_type: str,
    ) -> None:

        self.file_path = str(
            Path(file_path)
        )

        self.file_type = (
            file_type.lower().strip()
        )

        self.df: pd.DataFrame = load_dataset(
            file_path=self.file_path,
            file_type=self.file_type,
        )

    @property
    def row_count(self) -> int:
        return int(len(self.df))

    @property
    def column_count(self) -> int:
        return int(len(self.df.columns))

    @property
    def columns(self) -> list[str]:
        return [
            str(column)
            for column in self.df.columns
        ]

    def semantic_types(self) -> dict[str, str]:
        """
        Return semantic types for all columns.
        """

        return {
            str(column): detect_column_type(
                series=self.df[column],
                column_name=str(column),
            )
            for column in self.df.columns
        }

    def numeric_columns(self) -> list[str]:
        """
        Return columns classified as genuinely numeric.
        """

        semantic_types = self.semantic_types()

        return [
            column
            for column, semantic_type
            in semantic_types.items()
            if semantic_type == "numeric"
        ]

    def categorical_columns(self) -> list[str]:
        """
        Return categorical columns.
        """

        semantic_types = self.semantic_types()

        return [
            column
            for column, semantic_type
            in semantic_types.items()
            if semantic_type == "categorical"
        ]

    def datetime_columns(self) -> list[str]:
        """
        Return datetime columns.
        """

        semantic_types = self.semantic_types()

        return [
            column
            for column, semantic_type
            in semantic_types.items()
            if semantic_type == "datetime"
        ]

    def identifier_columns(self) -> list[str]:
        """
        Return identifier-like columns.
        """

        semantic_types = self.semantic_types()

        return [
            column
            for column, semantic_type
            in semantic_types.items()
            if semantic_type == "identifier"
        ]

    def binary_columns(self) -> list[str]:
        """
        Return binary columns.
        """

        semantic_types = self.semantic_types()

        return [
            column
            for column, semantic_type
            in semantic_types.items()
            if semantic_type == "binary"
        ]

    def text_columns(self) -> list[str]:
        """
        Return text columns.
        """

        semantic_types = self.semantic_types()

        return [
            column
            for column, semantic_type
            in semantic_types.items()
            if semantic_type == "text"
        ]