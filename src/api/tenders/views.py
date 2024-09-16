import logging
from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from api.employees.dependices import get_user_by_username
from api.organization_responsibles.dependices import (
    user_is_responsible_for_organization,
)
from api.tenders import crud
from api.tenders.dependies import get_tender_by_id, user_is_responsible_for_tender
from core.models.business_enums import ServiceType, TenderStatus
from core.models.db_helper import database_helper
from core.schemas.tender import TenderCreate, TenderResponse, TenderUpdate
from error_response_models import (
    TenderNotExistErrorResponse,
    UserIsNotResponsibleForOrganizationErrorResponse,
    UserIsNotResponsibleForTenderErrorResponse,
    UserNotExistErrorResponse,
)

tenders_router = APIRouter(prefix="/tenders", tags=["tenders"])

logger = logging.getLogger(__name__)


@tenders_router.get(
    "/",
    description="Получение списка тендеров",
    response_model=List[TenderResponse],
    status_code=200,
)
async def get_all_tenders(
    session: Annotated[AsyncSession, Depends(database_helper.session_getter)],
    limit: int = Query(default=5, ge=0),
    offset: int = Query(default=0, ge=0),
    service_type: ServiceType = Query(),
):
    return await crud.get_tenders(session, limit, offset, service_type)


@tenders_router.post(
    "/new",
    description="Создание нового тендера",
    status_code=200,
    response_model=TenderResponse,
)
async def create_new_tender(
    session: Annotated[AsyncSession, Depends(database_helper.session_getter)],
    tender: TenderCreate,
):
    user = await get_user_by_username(session, tender.creator_username)
    if not user:
        return UserNotExistErrorResponse()  # 401
    if not await user_is_responsible_for_organization(
        session, tender.organization_id, user.id
    ):
        return UserIsNotResponsibleForOrganizationErrorResponse()  # 403
    return await crud.create_tender(session, tender)


@tenders_router.get(
    "/my",
    description="Получить тендеры пользователя",
    response_model=List[TenderResponse],
)
async def get_user_tenders(
    session: Annotated[AsyncSession, Depends(database_helper.session_getter)],
    limit: int = Query(default=5, ge=0),
    offset: int = Query(default=0, ge=0),
    username: str = Query(default="test_user"),
):
    if not await get_user_by_username(session, username):
        return UserNotExistErrorResponse()  # 401
    return await crud.get_user_tenders(session, limit, offset, username)


@tenders_router.get(
    "/{tenderId}/status", description="Получение текущего статуса тендера"
)
async def get_tender_status_by_id(
    session: Annotated[AsyncSession, Depends(database_helper.session_getter)],
    tender_id: Annotated[UUID, Path(..., alias="tenderId")],
    username: str = Query(default="test_user"),
):
    user = await get_user_by_username(session, username)
    if not user:
        return UserNotExistErrorResponse()  # 401
    if not await user_is_responsible_for_tender(session, tender_id, user.username):
        return UserIsNotResponsibleForTenderErrorResponse()  # 403
    if not await get_tender_by_id(session, tender_id):
        return TenderNotExistErrorResponse()  # 404
    if tender_data := await crud.get_tender_status(session, tender_id, username):
        return JSONResponse(status_code=200, content=tender_data.status.value)


@tenders_router.put(
    "/{tenderId}/status",
    description="Изменение статуса тендера",
    response_model=TenderResponse,
)
async def change_tender_status(
    session: Annotated[AsyncSession, Depends(database_helper.session_getter)],
    tender_id: Annotated[UUID, Path(..., alias="tenderId")],
    new_tender_status: TenderStatus,
    username: str = Query(default="test_user"),
):
    user = await get_user_by_username(session, username)
    if not user:
        return UserNotExistErrorResponse()  # 401
    if not await user_is_responsible_for_tender(session, tender_id, user.username):
        return UserIsNotResponsibleForTenderErrorResponse()  # 403
    if not await get_tender_by_id(session, tender_id):
        return TenderNotExistErrorResponse()  # 404
    return await crud.change_tender_status(
        session, tender_id, new_tender_status, username
    )


@tenders_router.patch(
    "/{tenderId}/edit",
    description="Редактирование тендера",
    response_model=TenderResponse,
)
async def edit_tender_data(
    session: Annotated[AsyncSession, Depends(database_helper.session_getter)],
    tender_id: Annotated[UUID, Path(..., alias="tenderId")],
    tender_update: TenderUpdate,
    username: str = Query(default="test_user"),
):
    user = await get_user_by_username(session, username)
    if not user:
        return UserNotExistErrorResponse()  # 401
    if not await user_is_responsible_for_tender(session, tender_id, user.username):
        return UserIsNotResponsibleForTenderErrorResponse()  # 403
    if not await get_tender_by_id(session, tender_id):
        return TenderNotExistErrorResponse()  # 404
    return await crud.update_tender(session, tender_id, tender_update, username)


@tenders_router.put(
    "/{tenderId}/rollback/{version}",
    description="Откат версии тендера",
    response_model=TenderResponse,
)
async def rollback_tender_to_version(
    session: Annotated[AsyncSession, Depends(database_helper.session_getter)],
    tender_id: Annotated[UUID, Path(..., alias="tenderId")],
    version: Annotated[int, Path(..., ge=1)],
    username: str = Query(default="test_user"),
):
    user = await get_user_by_username(session, username)
    if not user:
        return UserNotExistErrorResponse()  # 401
    if not await user_is_responsible_for_tender(session, tender_id, user.username):
        return UserIsNotResponsibleForTenderErrorResponse()  # 403
    if not await get_tender_by_id(session, tender_id):
        return TenderNotExistErrorResponse()  # 404
    return await crud.rollback_tender(session, tender_id, version, username)
