from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.business_enums import AuthorType
from core.models.business_models import Bid, Decision, OrganizationResponsible


async def get_user_bids_responsible(session: AsyncSession, bid_id: UUID, user_id: UUID):
    stmt = (
        select(Bid)
        .filter(Bid.author_type == AuthorType.ORGANIZATION)
        .join(
            OrganizationResponsible,
            Bid.author_id == OrganizationResponsible.organization_id,
        )
    )
    # stmt = select(Bid).filter(Bid.id == bid_id, Bid.author_type == AuthorType.USER, Bid.author_id == user_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_bid_by_id(session: AsyncSession, bid_id: UUID):
    return await session.get(Bid, bid_id)


async def get_decisions(session: AsyncSession, bid_id: UUID):
    stmt = select(Decision).filter(Decision.bid_id == bid_id)
    result = await session.execute(stmt)
    return result.all()
