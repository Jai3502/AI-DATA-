from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DatasetProfileResponse(BaseModel):
    id: UUID
    dataset_id: UUID
    row_count: int
    column_count: int
    profile_data: dict
    created_at: datetime
    updated_at: datetime