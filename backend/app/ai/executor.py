from __future__ import annotations

from typing import Any, Callable

from app.ai.tools import (
    get_data_quality,
    get_dataset_insights,
    get_dataset_overview,
    get_numeric_statistics,
    get_outlier_analysis,
)
from app.data_engine.context import DatasetContext


ALLOWED_TOOLS: dict[str, Callable[[DatasetContext], dict[str, Any]]] = {
    "dataset_overview": get_dataset_overview,
    "data_quality": get_data_quality,
    "outlier_analysis": get_outlier_analysis,
    "dataset_insights": get_dataset_insights,
    "numeric_statistics": get_numeric_statistics,
}


def execute_analysis_tool(
    tool_name: str,
    context: DatasetContext,
) -> dict[str, Any]:
    """
    Execute one explicitly allowed analysis tool.

    Security rules:
    - Only allowlisted tools can execute.
    - No arbitrary Python execution.
    - No arbitrary shell commands.
    - No arbitrary file-system access.
    - Tools return aggregated analysis results.
    """

    tool = ALLOWED_TOOLS.get(tool_name)

    if tool is None:
        raise ValueError(
            f"Analysis tool '{tool_name}' is not allowed."
        )

    return tool(context)