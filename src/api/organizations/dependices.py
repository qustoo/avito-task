from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from core.models.business_models import Organization
from core.schemas.organization import OrganizationResponse


async def get_organization_by_id(
    session: AsyncSession, organization_id: UUID
) -> Optional[OrganizationResponse]:
    return await session.get(Organization, organization_id)
