from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.ai.executor import execute_analysis_tool
from app.ai.response_generator import generate_analysis_response
from app.data_engine.context import DatasetContext


@dataclass(frozen=True)
class ToolDecision:
    """
    Represents the tool selected for a user question.
    """

    tool_name: str
    reason: str


class AIAnalystOrchestrator:
    """
    Safe orchestration layer for the AI Data Analyst.

    Responsibilities:
    - Understand the basic intent of a user question.
    - Select only an allowlisted analysis tool.
    - Execute the selected tool through the safe executor.
    - Convert the controlled result into a readable response.
    - Never execute arbitrary Python, SQL, shell commands,
      or filesystem operations.
    """

    TOOL_KEYWORDS: dict[str, tuple[str, ...]] = {
        "data_quality": (
            "missing",
            "null",
            "empty",
            "duplicate",
            "duplicates",
            "quality",
            "data quality",
            "clean",
            "cleaning",
            "data problem",
            "data problems",
        ),
        "outlier_analysis": (
            "outlier",
            "outliers",
            "unusual",
            "anomaly",
            "anomalies",
            "abnormal",
            "extreme value",
            "extreme values",
        ),
        "numeric_statistics": (
            "average",
            "mean",
            "median",
            "minimum",
            "minimum value",
            "maximum",
            "maximum value",
            "max",
            "min",
            "standard deviation",
            "std",
            "statistics",
            "statistical",
            "range",
        ),
        "dataset_insights": (
            "insight",
            "insights",
            "important insight",
            "important insights",
            "findings",
            "finding",
            "summary",
            "summarize",
            "overall",
            "what do you see",
            "what can you tell me",
        ),
        "dataset_overview": (
            "overview",
            "dataset overview",
            "dataset information",
            "dataset info",
            "columns",
            "column names",
            "how many rows",
            "how many columns",
            "row count",
            "column count",
            "dataset size",
            "structure",
        ),
    }

    DEFAULT_TOOL = "dataset_overview"

    def decide_tool(
        self,
        question: str,
    ) -> ToolDecision:
        """
        Select an allowlisted analysis tool based on
        the user's question.
        """

        if not isinstance(question, str):
            raise TypeError(
                "Question must be a string."
            )

        normalized_question = (
            question.strip().lower()
        )

        if not normalized_question:
            raise ValueError(
                "Question cannot be empty."
            )

        priority_order = (
            "outlier_analysis",
            "data_quality",
            "numeric_statistics",
            "dataset_insights",
            "dataset_overview",
        )

        for tool_name in priority_order:
            keywords = self.TOOL_KEYWORDS[
                tool_name
            ]

            for keyword in keywords:
                if keyword in normalized_question:
                    return ToolDecision(
                        tool_name=tool_name,
                        reason=(
                            f"Question matched keyword "
                            f"'{keyword}'."
                        ),
                    )

        return ToolDecision(
            tool_name=self.DEFAULT_TOOL,
            reason=(
                "No specific analysis intent was detected; "
                "using the safe dataset overview tool."
            ),
        )

    def analyze(
        self,
        question: str,
        context: DatasetContext,
    ) -> dict[str, Any]:
        """
        Route the user question to a safe analysis tool,
        execute it, and generate a readable response.
        """

        decision = self.decide_tool(
            question=question
        )

        result = execute_analysis_tool(
            tool_name=decision.tool_name,
            context=context,
        )

        answer = generate_analysis_response(
            tool_name=decision.tool_name,
            result=result,
        )

        return {
            "question": question,
            "tool": decision.tool_name,
            "reason": decision.reason,
            "answer": answer,
            "result": result,
        }


def analyze_user_question(
    question: str,
    context: DatasetContext,
) -> dict[str, Any]:
    """
    Convenience function for API/service layers.
    """

    orchestrator = AIAnalystOrchestrator()

    return orchestrator.analyze(
        question=question,
        context=context,
    )