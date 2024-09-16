import uuid
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from core.models.business_enums import AuthorType

BidID = Annotated[
    uuid.UUID,
    Field(
        ...,
        default_factory=uuid.uuid4,
        description="Уникальный идентификатор предложения, присвоенный сервером",
    ),
]
AuthorID = Annotated[
    uuid.UUID,
    Field(
        ...,
        default_factory=uuid.uuid4,
        description="Уникальный идентификатор автора предложения",
    ),
]
TenderID = Annotated[
    uuid.UUID,
    Field(
        ...,
        default_factory=uuid.uuid4,
        description="Уникальный идентификатор тендера, присвоенный сервером.",
    ),
]
BidName = Annotated[
    str, Field(..., max_lenght=100, description="Полное название предложения")
]
BidDescription = Annotated[
    str, Field(..., max_length=500, description="Описание предложения")
]
BidVersion = Annotated[int, Field(..., ge=1, description="Номер версии после правок")]


class BidCreate(BaseModel):
    name: BidName
    description: BidDescription
    tender_id: TenderID
    author_type: AuthorType
    author_id: AuthorID


class BidResponse(BaseModel):
    id: BidID
    name: BidName
    description: BidDescription
    tender_id: TenderID
    author_type: AuthorType
    author_id: AuthorID
    version: BidVersion
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class BidUpdate(BaseModel):
    name: BidName
    description: BidDescription
