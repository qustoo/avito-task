from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.business_enums import ServiceType, TenderStatus
from core.models.business_models import Tender, TenderHistory
from core.schemas.tender import TenderCreate, TenderUpdate


async def get_history_tender(
    session: AsyncSession, tenderID: UUID, username: str, version: int
):
    stmt = select(TenderHistory).filter(
        TenderHistory.refer_tender_id == tenderID,
        TenderHistory.creator_username == username,
        TenderHistory.version == version,
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_tenders(
    session: AsyncSession, limit: int, offset: int, service_type: ServiceType
) -> Sequence[Tender]:
    stmt = (
        select(Tender)
        .limit(limit)
        .offset(offset)
        .where(Tender.service_type == service_type)
        .order_by(Tender.name)
    )
    result = await session.scalars(stmt)
    return result.all()


async def get_user_tender(
    session: AsyncSession, tenderID: UUID, username: str
) -> Tender:
    stmt = (
        select(Tender)
        .filter(Tender.id == tenderID, Tender.creator_username == username)
        .order_by(Tender.version.desc())
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_tender(session: AsyncSession, tenderID: UUID) -> Tender | None:
    return await session.get(Tender, tenderID)


async def create_tender(session: AsyncSession, tender: TenderCreate) -> Tender:
    new_tender = Tender(**tender.model_dump())
    session.add(new_tender)
    await session.commit()
    await session.refresh(new_tender)
    return new_tender


async def get_user_tenders(
    session: AsyncSession, limit: int, offset: int, username: str
) -> Sequence[Tender]:
    stmt = (
        select(Tender)
        .limit(limit)
        .offset(offset)
        .where(Tender.creator_username == username)
        .order_by(Tender.name)
    )
    result = await session.scalars(stmt)
    return result.all()


async def get_tender_status(session: AsyncSession, tenderID, username: str) -> Tender:
    stmt = select(Tender).filter(
        Tender.id == tenderID, Tender.creator_username == username
    )
    result = await session.execute(stmt)
    tender = result.scalar_one_or_none()
    return tender


async def change_tender_status(
    session: AsyncSession, tenderID: UUID, new_status: TenderStatus, username: str
) -> Tender:
    stmt = select(Tender).filter(
        Tender.id == tenderID, Tender.creator_username == username
    )
    result = await session.execute(stmt)
    tender = result.scalar_one_or_none()
    tender.status = new_status
    await session.commit()
    await session.refresh(tender)
    return tender


async def update_tender(
    session: AsyncSession, tenderID: UUID, tender_update: TenderUpdate, username: str
) -> Tender:
    tender = await get_user_tender(session, tenderID, username)
    old_tender_entry = TenderHistory(
        refer_tender_id=tender.id,
        name=tender.name,
        description=tender.description,
        service_type=tender.service_type,
        status=tender.status,
        version=tender.version,
        organization_id=tender.organization_id,
        creator_username=tender.creator_username,
    )
    for name, value in tender_update.model_dump(exclude_unset=True).items():
        setattr(tender, name, value)
    tender.version += 1
    session.add(old_tender_entry)
    await session.commit()
    await session.refresh(tender)
    return tender


async def rollback_tender(
    session: AsyncSession, tenderId: UUID, version: int, username: str
) -> Tender:
    history_tender = await get_history_tender(session, tenderId, username, version)
    tender = await get_user_tender(session, tenderId, username)
    # Set attributes by tender version
    tender.name = history_tender.name
    tender.description = history_tender.description
    tender.service_type = history_tender.service_type
    tender.version += 1
    tender.organization_id = history_tender.organization_id
    tender.creator_username = history_tender.creator_username
    tender.created_at = history_tender.created_at
    tender.updated_at = history_tender.updated_at

    await session.commit()
    await session.refresh(tender)
    return tender
