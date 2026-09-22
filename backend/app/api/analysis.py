import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.dataset import Dataset
from app.models.dataset_analysis import DatasetAnalysis
from app.models.organization_membership import OrganizationMembership
from app.models.user import User
from app.services.analysis_queue import enqueue_analysis_job
from app.services.analysis_service import create_analysis_job


router = APIRouter(
    prefix="/datasets",
    tags=["Dataset Analysis"],
)

STORAGE_ROOT = Path("storage") / "datasets"


def get_dataset_for_user(
    db: Session,
    dataset_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Dataset:
    """
    Fetch a dataset only when the current user
    belongs to its organization.
    """

    dataset = (
        db.query(Dataset)
        .filter(
            Dataset.id == dataset_id
        )
        .first()
    )

    if dataset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found.",
        )

    membership = (
        db.query(OrganizationMembership)
        .filter(
            OrganizationMembership.organization_id
            == dataset.organization_id,
            OrganizationMembership.user_id
            == user_id,
        )
        .first()
    )

    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You are not a member of "
                "this organization."
            ),
        )

    return dataset


def get_storage_path(
    dataset: Dataset,
) -> Path:
    """
    Build and validate the private storage path
    for a dataset.
    """

    storage_root = (
        STORAGE_ROOT
        / str(dataset.organization_id)
    ).resolve()

    filename = Path(
        dataset.storage_key
    ).name

    storage_path = (
        storage_root / filename
    ).resolve()

    if storage_root not in storage_path.parents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid dataset storage path.",
        )

    return storage_path


@router.post(
    "/{dataset_id}/analyze",
    status_code=status.HTTP_202_ACCEPTED,
)
def analyze_dataset_endpoint(
    dataset_id: uuid.UUID,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    """
    Create an asynchronous analysis job.

    The API creates a pending job and places it
    into Redis. A separate worker performs the
    actual dataset analysis.
    """

    dataset = get_dataset_for_user(
        db=db,
        dataset_id=dataset_id,
        user_id=current_user.id,
    )

    storage_path = get_storage_path(
        dataset
    )

    if not storage_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset file not found.",
        )

    analysis = create_analysis_job(
        db=db,
        dataset=dataset,
    )

    try:

        enqueue_analysis_job(
            analysis_id=str(
                analysis.id
            ),
            storage_path=str(
                storage_path
            ),
        )

    except Exception:

        analysis.status = "failed"
        analysis.error_message = (
            "Analysis job could not be queued."
        )

        db.commit()

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Analysis service is temporarily "
                "unavailable."
            ),
        )

    return {
        "analysis_id": analysis.id,
        "dataset_id": dataset.id,
        "organization_id": dataset.organization_id,
        "status": "pending",
        "message": (
            "Dataset analysis job has been queued."
        ),
    }


@router.get(
    "/{dataset_id}/analyses/{analysis_id}",
    status_code=status.HTTP_200_OK,
)
def get_analysis_result(
    dataset_id: uuid.UUID,
    analysis_id: uuid.UUID,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    """
    Get the status and result of a dataset analysis.

    Access is restricted to authenticated users
    belonging to the dataset's organization.
    """

    dataset = get_dataset_for_user(
        db=db,
        dataset_id=dataset_id,
        user_id=current_user.id,
    )

    analysis = (
        db.query(DatasetAnalysis)
        .filter(
            DatasetAnalysis.id == analysis_id,
            DatasetAnalysis.dataset_id == dataset.id,
        )
        .first()
    )

    if analysis is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found.",
        )

    return {
        "analysis_id": analysis.id,
        "dataset_id": dataset.id,
        "organization_id": dataset.organization_id,
        "status": analysis.status,
        "started_at": analysis.started_at,
        "completed_at": analysis.completed_at,
        "error_message": (
            analysis.error_message
            if analysis.status == "failed"
            else None
        ),
        "analysis": (
            analysis.result
            if analysis.status == "completed"
            else None
        ),
    }