from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


ProjectType = Literal["new_building", "existing_building"]


class ProjectCreate(BaseModel):
    name: str = Field(min_length=3, max_length=200)
    description: str | None = None

    city: str | None = Field(default=None, max_length=100)
    district: str | None = Field(default=None, max_length=100)

    building_type: str | None = Field(default=None, max_length=100)
    project_type: ProjectType = "new_building"

    total_construction_area: Decimal | None = Field(default=None, gt=0)
    parcel_area: Decimal | None = Field(default=None, gt=0)
    floor_count: int | None = Field(default=None, gt=0)

    main_facade_direction: str | None = None
    target_certificate_level: str | None = None
    estimated_budget: Decimal | None = Field(default=None, gt=0)


class ProjectResponse(ProjectCreate):
    id: UUID
    created_by: UUID
    status: str

    model_config = {
        "from_attributes": True
    }