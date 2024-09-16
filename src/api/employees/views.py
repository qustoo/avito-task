from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.business_models import Employee
from core.models.db_helper import database_helper
from core.schemas.employee import EmployeeCreate

employee_router = APIRouter(prefix="/employees", tags=["employees"])


@employee_router.get(
    "/",
    description="Получение всех пользователей",
    status_code=200,
)
async def get_all_employees(
    session: Annotated[AsyncSession, Depends(database_helper.session_getter)],
):
    stmt = select(Employee).order_by(Employee.first_name)
    result = await session.scalars(stmt)
    return result.all()


@employee_router.post(
    "/new", description="Создание нового пользователя", status_code=200
)
async def create_new_employee(
    session: Annotated[AsyncSession, Depends(database_helper.session_getter)],
    employee: EmployeeCreate,
):
    new_employee = Employee(**employee.model_dump())
    session.add(new_employee)
    await session.commit()
    await session.refresh(new_employee)
    return {"message": "employee created successfully", "employee": new_employee}
