from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.business_models import OrganizationResponsible


async def user_is_responsible_for_organization(
    session: AsyncSession, organization_id: UUID, user_id: UUID
):
    organization_stmt = select(OrganizationResponsible).filter(
        OrganizationResponsible.organization_id == organization_id,
        OrganizationResponsible.user_id == user_id,
    )
    result = await session.scalars(organization_stmt)
    return result.first()


async def get_user_organization_id(session: AsyncSession, user_id: UUID):
    organization_stmt = select(OrganizationResponsible.organization_id).filter(
        OrganizationResponsible.user_id == user_id
    )
    result = await session.scalars(organization_stmt)
    return result.first()
