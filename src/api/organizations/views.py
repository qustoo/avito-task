from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.business_models import Organization
from core.models.db_helper import database_helper
from core.schemas.organization import OrganizationCreate

organization_router = APIRouter(prefix="/organizations", tags=["organizations"])


@organization_router.get(
    "/",
    description="Получение всех организаций",
    status_code=200,
)
async def get_all_organization(
    session: Annotated[AsyncSession, Depends(database_helper.session_getter)],
):
    stmt = select(Organization)
    result = await session.scalars(stmt)
    return result.all()


@organization_router.post(
    "/new", description="Создание новой организации", status_code=200
)
async def create_new_organization(
    session: Annotated[AsyncSession, Depends(database_helper.session_getter)],
    organization: OrganizationCreate,
):
    new_organization = Organization(**organization.model_dump())
    session.add(new_organization)
    await session.commit()
    await session.refresh(new_organization)
    return {
        "message": "Organization created successfully",
        "Organization": new_organization,
    }
