from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.business_models import Tender


async def get_tender_by_id(session: AsyncSession, tenderID: UUID) -> Optional[Tender]:
    return await session.get(Tender, tenderID)


async def user_is_responsible_for_tender(
    session: AsyncSession, tenderID: UUID, creator_username: str
):
    stmt = select(Tender).filter(
        Tender.id == tenderID, Tender.creator_username == creator_username
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
