from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.permissions import require_permission

from app.api.datasets import get_organization_membership
from app.api.analysis import get_storage_path

from app.models.dataset import Dataset
from app.models.user import User

from app.schemas.forecast import ForecastRequest, ForecastResponse
from app.services.forecast_service import generate_forecast


router = APIRouter(
    prefix="/datasets",
    tags=["forecasting"],
)


# =========================================================
# Create Forecast
# =========================================================

@router.post(
    "/{dataset_id}/forecast",
    response_model=ForecastResponse,
)
def create_forecast(
    dataset_id: UUID,
    request: ForecastRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # -----------------------------------------------------
    # 1. Get dataset
    # -----------------------------------------------------

    dataset = (
        db.query(Dataset)
        .filter(
            Dataset.id == dataset_id,
        )
        .first()
    )

    if dataset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found.",
        )

    # -----------------------------------------------------
    # 2. Verify organization membership + permission
    # -----------------------------------------------------

    membership = get_organization_membership(
        db=db,
        organization_id=dataset.organization_id,
        user_id=current_user.id,
    )

    require_permission(
        role=membership.role,
        permission="analysis_run",
    )

    # -----------------------------------------------------
    # 3. Dataset must be profiled
    # -----------------------------------------------------

    if dataset.status != "profiled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dataset must be profiled before forecasting.",
        )

    # -----------------------------------------------------
    # 4. Generate forecast
    # -----------------------------------------------------

    try:
        return generate_forecast(
            dataset_id=str(dataset.id),
            file_path=str(get_storage_path(dataset)),
            horizon=request.horizon,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc