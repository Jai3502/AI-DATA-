from pathlib import Path

from sqlalchemy.orm import Session

from app.data_engine.profiler import profile_dataset
from app.models.dataset import Dataset
from app.models.dataset_profile import DatasetProfile


def profile_uploaded_dataset(
    db: Session,
    dataset: Dataset,
) -> Dataset:
    """
    Profile an uploaded dataset and persist profiling
    metadata in the database.

    Raw cell values are never stored in dataset_profiles.
    """

    storage_path = Path("storage") / "datasets" / dataset.storage_key

    if not storage_path.exists():
        raise FileNotFoundError(
            "Dataset file not found in private storage."
        )

    dataset.status = "profiling"

    db.commit()
    db.refresh(dataset)

    try:
        profile = profile_dataset(
            file_path=str(storage_path),
            file_type=dataset.file_type,
        )

        dataset.row_count = profile["row_count"]
        dataset.column_count = profile["column_count"]

        dataset_profile = DatasetProfile(
            dataset_id=dataset.id,
            row_count=profile["row_count"],
            column_count=profile["column_count"],
            profile_data={
                "columns": profile["columns"],
            },
        )

        db.add(dataset_profile)

        dataset.status = "profiled"

        db.commit()
        db.refresh(dataset)

        return dataset

    except Exception:
        db.rollback()

        dataset.status = "failed"

        db.commit()
        db.refresh(dataset)

        raise