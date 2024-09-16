from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.employees.dependices import get_user_by_id
from api.organizations.dependices import get_organization_by_id
from core.models.business_models import OrganizationResponsible
from core.models.db_helper import database_helper
from core.schemas.organization_responsible import OrganizationResponsiblesCreate
from error_response_models import (
    OrganizationNotExistErrorResponse,
    UserNotExistErrorResponse,
)

organization_responsibles_router = APIRouter(
    prefix="/organization_responsibles", tags=["organization_responsibles"]
)


@organization_responsibles_router.post(
    "/", description="Запись отвественных за организацию"
)
async def create_organization_responsible(
    session: Annotated[AsyncSession, Depends(database_helper.session_getter)],
    organization_responsible: OrganizationResponsiblesCreate,
):
    if not await get_organization_by_id(
        session, organization_responsible.organization_id
    ):
        return OrganizationNotExistErrorResponse()
    if not await get_user_by_id(session, organization_responsible.user_id):
        return UserNotExistErrorResponse()
    new_organization_responsible = OrganizationResponsible(
        **organization_responsible.model_dump()
    )
    session.add(new_organization_responsible)
    await session.commit()
    await session.refresh(new_organization_responsible)
    return {
        "message": "new_organization_responsible created successfully",
        "organization_responsible": new_organization_responsible,
    }


@organization_responsibles_router.get(
    "/new",
    description="Получить всех отвественных за организаци",
    status_code=200,
)
async def get_all_organization_responsibles(
    session: Annotated[AsyncSession, Depends(database_helper.session_getter)],
):
    stmt = select(OrganizationResponsible)
    result = await session.scalars(stmt)
    return result.all()
