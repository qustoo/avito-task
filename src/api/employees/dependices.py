from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.business_models import Employee


async def get_user_by_id(session: AsyncSession, user_id: UUID) -> Optional[Employee]:
    employee = await session.get(Employee, user_id)
    return employee


async def get_user_by_username(
    session: AsyncSession, username: str
) -> Optional[Employee]:
    stmt = select(Employee).where(Employee.username == username)
    result_user = await session.execute(stmt)
    return result_user.scalar_one_or_none()
