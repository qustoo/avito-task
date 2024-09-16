import uuid
from datetime import datetime
from typing import Annotated, Optional

from pydantic import UUID4, BaseModel, ConfigDict, Field

from core.models.business_enums import ServiceType, TenderStatus

TenderID = Annotated[
    uuid.UUID,
    Field(
        ...,
        default_factory=uuid.uuid4,
        description="Уникальный идентификатор тендера, присвоенный сервером.",
    ),
]
TenderName = Annotated[
    str, Field(..., max_lenght=100, description="Полное название тендера")
]
TenderDescription = Annotated[
    str, Field(..., max_length=500, description="Описание тендера")
]
TenderServiceType = Annotated[
    ServiceType, Field(..., description="Вид услуги, к которой относиться тендер")
]
TenderEnumStatus = Annotated[TenderStatus, Field(..., description="Статус тендер")]
TenderVersion = Annotated[
    int, Field(..., ge=1, description="Номер версии после правок")
]
TenderCreatorUsername = Annotated[str, Field(..., min_length=1, max_length=50)]


class TenderCreate(BaseModel):
    name: TenderName
    description: TenderDescription
    service_type: TenderServiceType
    status: TenderEnumStatus
    organization_id: UUID4
    creator_username: TenderCreatorUsername


class TenderResponse(BaseModel):
    id: TenderID
    name: TenderName
    description: TenderDescription
    status: TenderEnumStatus
    service_type: TenderServiceType
    version: TenderVersion
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class TenderUpdate(BaseModel):
    name: Optional[TenderName] = None
    description: Optional[TenderDescription] = None
    service_type: Optional[TenderServiceType] = None
