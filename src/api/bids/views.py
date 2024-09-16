import logging
from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from api.employees.dependices import get_user_by_id, get_user_by_username
from api.organizations.dependices import get_organization_by_id
from api.tenders.dependies import get_tender_by_id
from core.models.business_enums import BidStatus, DecisionType
from core.models.db_helper import database_helper
from core.schemas.bid import AuthorType, BidCreate, BidResponse, BidUpdate
from error_response_models import (
    BidNotExistErrorResponse,
    ForbiddenErrorResponse,
    OrganizationNotExistErrorResponse,
    TenderNotExistErrorResponse,
    UserIsNotResponsibleForBidErrorResponse,
    UserNotExistErrorResponse,
)

from . import crud
from .dependices import get_bid_by_id, get_user_bids_responsible

bids_router = APIRouter(prefix="/bids", tags=["bids"])

logger = logging.getLogger(__name__)


@bids_router.post(
    "/new", description="Создание нового предложения", response_model=BidResponse
)
async def create_new_bid(
    session: Annotated[AsyncSession, Depends(database_helper.session_getter)],
    bid: BidCreate,
):
    if not await get_tender_by_id(session, bid.tender_id):
        return TenderNotExistErrorResponse()
    if bid.author_type == AuthorType.USER and not await get_user_by_id(
        session, bid.author_id
    ):
        return UserNotExistErrorResponse()
    if bid.author_type == AuthorType.ORGANIZATION and not await get_organization_by_id(
        session, bid.author_id
    ):
        return OrganizationNotExistErrorResponse()
    return await crud.create_bid(session, bid)


@bids_router.get(
    "/my",
    description="Получение списках предложений пользователя",
    response_model=List[BidResponse],
)
async def get_user_bids(
    session: Annotated[AsyncSession, Depends(database_helper.session_getter)],
    limit: int = Query(default=5, ge=0),
    offset: int = Query(default=0, ge=0),
    username: str = Query(default="test_user"),
):
    user = await get_user_by_username(session, username)
    if not user:
        return UserNotExistErrorResponse()
    return await crud.get_user_bids(session, limit, offset, user.id)


@bids_router.get(
    "/{tenderId}/list",
    description="Получение списка предложений для тендера",
)
async def get_list_bids_for_tender(
    session: Annotated[AsyncSession, Depends(database_helper.session_getter)],
    tender_id: Annotated[UUID, Path(..., alias="tenderId")],
    username: str = Query(default="test_user"),
    limit: int = Query(default=5, ge=0),
    offset: int = Query(default=0, ge=0),
):
    user = await get_user_by_username(session, username)
    if not user:
        return UserNotExistErrorResponse()  # 401
    if not await get_tender_by_id(session, tender_id):
        return TenderNotExistErrorResponse()  # 404
    return await crud.get_bids_list_for_tender(
        session, tender_id, user.id, limit, offset
    )


@bids_router.get(
    "{bidId}/status",
    description="Получение статуса предложения",
    response_model=BidResponse,
)
async def get_bid_status(
    session: Annotated[AsyncSession, Depends(database_helper.session_getter)],
    bid_id: Annotated[UUID, Path(..., alias="bidId")],
    username: str = Query(default="test_user"),
):
    user = await get_user_by_username(session, username)
    if not user:
        return UserNotExistErrorResponse()  # 401
    if not await get_user_bids_responsible(session, bid_id, user.id):
        return ForbiddenErrorResponse()  # 403
    if not await get_bid_by_id(session, bid_id):
        return BidNotExistErrorResponse()  # 404
    bid_status = await crud.get_bid_status(session, bid_id)
    return JSONResponse(status_code=200, content=bid_status)


@bids_router.put(
    "{bidId}/status",
    description="Изменение статуса предложения",
    response_model=BidResponse,
)
async def change_bid_status(
    session: Annotated[AsyncSession, Depends(database_helper.session_getter)],
    bid_id: Annotated[UUID, Path(..., alias="bidId")],
    new_bid_status: BidStatus,
    username: str = Query(default="test_user"),
):
    user = await get_user_by_username(session, username)
    if not user:
        return UserNotExistErrorResponse()  # 401
    if not await get_user_bids_responsible(session, bid_id, user.username):
        return UserIsNotResponsibleForBidErrorResponse()  # 403
    if not await get_bid_by_id(session, bid_id):
        return BidNotExistErrorResponse()  # 404
    return await crud.change_big_status(session, bid_id, new_bid_status, user.id)


@bids_router.patch(
    "/{bidId}/edit",
    description="Редактирования параметров предложения",
    response_model=BidResponse,
)
async def edit_bit_data(
    session: Annotated[AsyncSession, Depends(database_helper.session_getter)],
    bid_id: Annotated[UUID, Path(..., alias="bidId")],
    bid_update: BidUpdate,
    username: str = Query(default="test_user"),
):
    user = await get_user_by_username(session, username)
    if not user:
        return UserNotExistErrorResponse()  # 401
    if not await get_user_bids_responsible(session, bid_id, user.username):
        return UserIsNotResponsibleForBidErrorResponse()  # 403
    if not await get_bid_by_id(session, bid_id):
        return BidNotExistErrorResponse()  # 404
    return await crud.update_bid(session, bid_id, bid_update)


@bids_router.put(
    "/{bidId}/submit_decision",
    description="Отправка решения по предложению",
    response_model=BidResponse,
)
async def submit_bid_decision(
    session: Annotated[AsyncSession, Depends(database_helper.session_getter)],
    bid_id: Annotated[UUID, Path(..., alias="bidId")],
    decision: DecisionType,
    username: str = Query(default="test_user"),
):
    user = await get_user_by_username(session, username)
    if not user:
        return UserNotExistErrorResponse()  # 401
    if not await get_user_bids_responsible(session, bid_id, user.username):
        return UserIsNotResponsibleForBidErrorResponse()  # 403
    if not await get_bid_by_id(session, bid_id):
        return BidNotExistErrorResponse()  # 404
    await crud.submit_decision(session, bid_id, decision, user.id)


@bids_router.put("/{bidId}/feedback", description="Отправка отзыва по предложению")
async def send_bid_feedback(
    session: Annotated[AsyncSession, Depends(database_helper.session_getter)],
    bid_id: Annotated[UUID, Path(..., alias="bidId")],
    bid_feedback: Annotated[str, Query(..., alias="bidFeedback")],
    username: str = Query(default="test_user"),
):
    user = await get_user_by_username(session, username)
    if not user:
        return UserNotExistErrorResponse()  # 401
    await crud.send_feedback(session, bid_id, bid_feedback, user.id)
