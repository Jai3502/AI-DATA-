import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.dataset import Dataset
from app.models.dataset_profile import DatasetProfile
from app.models.organization_membership import OrganizationMembership
from app.models.user import User
from app.schemas.dataset import DatasetResponse
from app.services.dataset_service import profile_uploaded_dataset
from app.schemas.dataset_profile import DatasetProfileResponse


router = APIRouter(
    prefix="/datasets",
    tags=["Datasets"],
)


ALLOWED_EXTENSIONS = {
    ".csv",
    ".xlsx",
    ".xls",
}

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

STORAGE_ROOT = Path("storage") / "datasets"


def validate_file_extension(filename: str) -> str:
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Allowed types: CSV, XLSX, XLS.",
        )

    return extension


def get_organization_membership(
    db: Session,
    organization_id: uuid.UUID,
    user_id: uuid.UUID,
) -> OrganizationMembership:

    membership = (
        db.query(OrganizationMembership)
        .filter(
            OrganizationMembership.organization_id == organization_id,
            OrganizationMembership.user_id == user_id,
        )
        .first()
    )

    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this organization.",
        )

    return membership


@router.post(
    "/upload",
    response_model=DatasetResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_dataset(
    organization_id: uuid.UUID = Form(...),
    name: str = Form(...),
    description: str | None = Form(None),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    # 1. Verify organization membership
    get_organization_membership(
        db=db,
        organization_id=organization_id,
        user_id=current_user.id,
    )

    # 2. Validate filename
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required.",
        )

    extension = validate_file_extension(file.filename)

    # 3. Validate dataset name
    name = name.strip()

    if not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dataset name cannot be empty.",
        )

    if len(name) > 255:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dataset name cannot exceed 255 characters.",
        )

    # 4. Generate private storage key
    file_id = uuid.uuid4()

    storage_key = (
        f"{organization_id}/{file_id}{extension}"
    )

    storage_path = STORAGE_ROOT / str(organization_id) / f"{file_id}{extension}"

    # 5. Create storage directory
    storage_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # 6. Save file with size protection
    total_size = 0

    try:
        with storage_path.open("wb") as output_file:

            while True:
                chunk = await file.read(1024 * 1024)

                if not chunk:
                    break

                total_size += len(chunk)

                if total_size > MAX_FILE_SIZE:
                    output_file.close()

                    if storage_path.exists():
                        storage_path.unlink()

                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="File size cannot exceed 50 MB.",
                    )

                output_file.write(chunk)

    finally:
        await file.close()

    # 7. Create dataset database record
    dataset = Dataset(
        organization_id=organization_id,
        created_by=current_user.id,
        name=name,
        original_filename=file.filename,
        storage_key=storage_key,
        file_type=extension.lstrip("."),
        status="uploaded",
        description=description.strip() if description else None,
    )

    try:
        db.add(dataset)
        db.commit()
        db.refresh(dataset)

    except Exception:
        db.rollback()

        if storage_path.exists():
            storage_path.unlink()

        raise

    try:
       dataset = profile_uploaded_dataset(
        db=db,
        dataset=dataset,
    )

    except Exception:
     raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Dataset profiling failed.",
    )

    return dataset

@router.get(
    "/{dataset_id}/profile",
    response_model=DatasetProfileResponse,
    status_code=status.HTTP_200_OK,
)
def get_dataset_profile(
    dataset_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    dataset = (
        db.query(Dataset)
        .filter(Dataset.id == dataset_id)
        .first()
    )

    if dataset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found.",
        )

    get_organization_membership(
        db=db,
        organization_id=dataset.organization_id,
        user_id=current_user.id,
    )

    profile = (
        db.query(DatasetProfile)
        .filter(
            DatasetProfile.dataset_id == dataset.id
        )
        .first()
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset profile not found.",
        )

    return profile

@router.get(
    "",
    response_model=list[DatasetResponse],
    status_code=status.HTTP_200_OK,
)
def get_datasets(
    organization_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Verify organization membership
    get_organization_membership(
        db=db,
        organization_id=organization_id,
        user_id=current_user.id,
    )

    # Get only datasets belonging to this organization
    datasets = (
        db.query(Dataset)
        .filter(
            Dataset.organization_id == organization_id
        )
        .order_by(Dataset.created_at.desc())
        .all()
    )

    return datasets