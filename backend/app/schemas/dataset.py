from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DatasetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    created_by: UUID

    name: str
    original_filename: str
    file_type: str
    status: str

    row_count: int | None = None
    column_count: int | None = None
    description: str | None = None