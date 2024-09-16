from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field

from core.models.business_enums import OrganizationType

OrganizationName = Annotated[
    str, Field(..., min_length=1, max_length=100, description="Название организации")
]
OrganizationDescription = Annotated[
    str, Field(..., min_length=1, max_length=500, description="Описание организации")
]


class OrganizationBase(BaseModel):
    name: OrganizationName
    description: OrganizationDescription
    type: OrganizationType


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationResponse(OrganizationBase):
    id: UUID
