import uuid
from typing import Annotated

from pydantic import BaseModel, Field

OrganizationID: Annotated[uuid.UUID, Field(..., description="Айди организации")]
UserID: Annotated[uuid.UUID, Field(..., description="Айди пользователя")]


class OrganizationResponsiblesCreate(BaseModel):
    organization_id: uuid.UUID
    user_id: uuid.UUID
