import uuid
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as UUIDType
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from core.models.base import Base
from core.models.business_enums import (
    AuthorType,
    BidStatus,
    DecisionType,
    OrganizationType,
    ServiceType,
    TenderStatus,
)


class Employee(Base):
    __tablename__ = "employee"

    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)


class Organization(Base):
    __tablename__ = "organization"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    type: Mapped["OrganizationType"] = mapped_column(
        Enum(OrganizationType), nullable=True
    )


class OrganizationResponsible(Base):
    __tablename__ = "organization_responsible"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organization.id"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("employee.id"), nullable=False
    )


class Tender(Base):
    __tablename__ = "tender"
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    service_type: Mapped["ServiceType"] = mapped_column(
        Enum(ServiceType), nullable=False
    )
    status: Mapped["TenderStatus"] = mapped_column(Enum(TenderStatus), nullable=False)
    version: Mapped[int] = mapped_column(
        Integer, default=1, nullable=False, autoincrement=True
    )
    organization_id: Mapped[str] = mapped_column(
        ForeignKey("organization.id"), nullable=False
    )
    creator_username: Mapped[str] = mapped_column(
        String, ForeignKey("employee.username"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    def __repr__(self):
        return f"<Tender(id={self.id}, name={self.name}, status={self.status})>"


class TenderHistory(Base):
    __tablename__ = "tender_history"
    refer_tender_id: Mapped[str] = mapped_column(
        ForeignKey("tender.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    service_type: Mapped["ServiceType"] = mapped_column(
        Enum(ServiceType), nullable=False
    )
    status: Mapped["TenderStatus"] = mapped_column(Enum(TenderStatus), nullable=False)
    version: Mapped[int] = mapped_column(
        Integer, default=1, nullable=False, autoincrement=True
    )
    organization_id: Mapped[str] = mapped_column(
        ForeignKey("organization.id"), nullable=False
    )
    creator_username: Mapped[str] = mapped_column(
        String, ForeignKey("employee.username"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())


class Bid(Base):
    __tablename__ = "bid"
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(
        String,
    )
    status: Mapped["BidStatus"] = mapped_column(
        Enum(BidStatus), default=BidStatus.CREATED, nullable=False
    )
    tender_id: Mapped[str] = mapped_column(ForeignKey("tender.id"))
    author_type: Mapped["AuthorType"] = mapped_column(Enum(AuthorType), nullable=False)
    author_id: Mapped[UUID] = mapped_column(UUIDType(as_uuid=True), default=uuid4)
    version: Mapped[int] = mapped_column(
        Integer, default=1, nullable=False, autoincrement=True
    )


class Decision(Base):
    __tablename__ = "decision"

    bid_id: Mapped[str] = mapped_column(ForeignKey("bid.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("employee.id"), nullable=False)
    decision_type: Mapped["DecisionType"] = mapped_column(
        Enum(DecisionType), nullable=False
    )


class Review(Base):
    description: Mapped[str] = mapped_column(String, nullable=False)
    bid_id: Mapped[UUID] = mapped_column(ForeignKey("bid.id"), nullable=False)
    reviewer_id: Mapped[UUID] = mapped_column(
        ForeignKey("employee.id"), nullable=False
    )  # Assuming a User model exists
