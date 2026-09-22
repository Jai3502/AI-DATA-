from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.data_engine.analysis_engine import analyze_dataset
from app.models.dataset import Dataset
from app.models.dataset_analysis import DatasetAnalysis


def create_analysis_job(
    db: Session,
    dataset: Dataset,
) -> DatasetAnalysis:
    """
    Create a new pending analysis job for a dataset.
    """

    analysis = DatasetAnalysis(
        dataset_id=dataset.id,
        status="pending",
    )

    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    return analysis


def run_analysis_job(
    db: Session,
    analysis: DatasetAnalysis,
    dataset: Dataset,
    storage_path: str,
) -> DatasetAnalysis:
    """
    Execute an analysis job and persist its result.

    Lifecycle:
        pending -> processing -> completed

    On failure:
        processing -> failed

    Raw dataset rows are not stored separately by this service.
    """

    analysis.status = "processing"
    analysis.started_at = datetime.now(
        timezone.utc
    )
    analysis.error_message = None

    db.commit()
    db.refresh(analysis)

    try:
        result = analyze_dataset(
            file_path=storage_path,
            file_type=dataset.file_type,
        )

        analysis.result = result
        analysis.status = "completed"
        analysis.completed_at = datetime.now(
            timezone.utc
        )

        db.commit()
        db.refresh(analysis)

        return analysis

    except Exception:
        db.rollback()

        analysis = (
            db.query(DatasetAnalysis)
            .filter(
                DatasetAnalysis.id
                == analysis.id
            )
            .first()
        )

        if analysis is None:
            raise

        analysis.status = "failed"
        analysis.error_message = (
            "Dataset analysis failed."
        )
        analysis.completed_at = datetime.now(
            timezone.utc
        )

        db.commit()
        db.refresh(analysis)

        return analysis


def get_analysis_by_id(
    db: Session,
    analysis_id: UUID,
) -> DatasetAnalysis | None:
    """
    Retrieve an analysis job by ID.
    """

    return (
        db.query(DatasetAnalysis)
        .filter(
            DatasetAnalysis.id
            == analysis_id
        )
        .first()
    )
