from typing import Sequence
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.bids.dependices import get_bid_by_id, get_decisions
from api.organization_responsibles.dependices import (
    get_user_organization_id,
    user_is_responsible_for_organization,
)
from api.tenders.dependies import get_tender_by_id
from core.models.business_enums import BidStatus, DecisionType, TenderStatus
from core.models.business_models import Bid, Decision, OrganizationResponsible, Review
from core.schemas.bid import BidCreate, BidUpdate


async def create_bid(session: AsyncSession, bid: BidCreate):
    new_tender = Bid(**bid.model_dump())
    session.add(new_tender)
    await session.commit()
    await session.refresh(new_tender)
    return new_tender


async def get_user_bids(
    session: AsyncSession, limit: int, offset: int, user_id: UUID
) -> Sequence[Bid]:
    stmt = select(Bid).limit(limit).offset(offset).where(Bid.author_id == user_id)
    result = await session.scalars(stmt)
    return result.all()


async def get_bids_list_for_tender(
    session: AsyncSession, tenderId: UUID, user_id: UUID, limit: int, offset: int
):
    stmt = (
        select(Bid)
        .filter(Bid.author_id == user_id, Bid.tender_id == tenderId)
        .offset(offset)
        .limit(limit)
        .order_by(Bid.name)
    )
    result = await session.scalars(stmt)
    return result.all()


async def get_bid_status(session: AsyncSession, bid_id: UUID):
    bid = await get_bid_by_id(session, bid_id)
    return bid.status.value


async def change_big_status(
    session: AsyncSession, bid_id: UUID, new_bid_status: BidStatus, user_id: UUID
) -> Bid:
    user_organization_id = await get_user_organization_id(session, user_id)
    stmt = select(Bid).filter(Bid.id == bid_id, Bid.author_id == user_organization_id)
    result = await session.execute(stmt)
    bid = result.scalar_one_or_none()
    bid.status = new_bid_status
    bid.version += 1
    await session.commit()
    await session.refresh(bid)
    return bid


async def update_bid(
    session: AsyncSession,
    bid_id: UUID,
    bid_update: BidUpdate,
):
    bid = await get_bid_by_id(session, bid_id)
    for name, value in bid_update.model_dump(exclude_unset=True).items():
        setattr(bid, name, value)
    bid.version += 1
    await session.commit()
    await session.refresh(bid)
    return bid


async def submit_decision(
    session: AsyncSession,
    bid_id: UUID,
    decision: DecisionType,
    user_id: UUID,
):
    bid = await get_bid_by_id(session, bid_id)

    responsible_user = await user_is_responsible_for_organization(
        session, bid.author_id, user_id
    )
    if not responsible_user:
        return

    new_decision = Decision(bid_id=bid.id, user_id=user_id, decision_type=decision)
    session.add(new_decision)
    await session.commit()

    decisions = await get_decisions(session, bid_id)

    if any(d.decision_type == DecisionType.REJECTED for d in decisions):
        return {"STATUS": "REJECTED"}

    approvals_count = sum(
        1 for decision in decisions if decision.decision_type == DecisionType.APPROVED
    )

    organization_id = bid.author_id
    stmt = select(func.count(OrganizationResponsible)).filter(
        OrganizationResponsible.organization_id == organization_id
    )
    total_responsible_users = await session.scalars(stmt)
    quorum = min(3, total_responsible_users.first())
    is_approved = approvals_count >= quorum
    if is_approved:
        tender = await get_tender_by_id(session, bid.tender_id)
        tender.status = TenderStatus.CLOSED
        await session.commit()
    return bid


async def send_feedback(
    session: AsyncSession,
    bid_id: UUID,
    description: str,
    user_id: UUID,
):
    bid = await get_bid_by_id(session, bid_id)
    responsible_user = await user_is_responsible_for_organization(
        session, bid.author_id, user_id
    )
    if not responsible_user:
        return "ERROR"
    new_review = Review(description=description, bid_id=bid_id, reviewer_id=user_id)
    session.add(new_review)
    await session.commit()
