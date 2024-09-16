from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

EmployeeUserName = Annotated[
    str, Field(..., min_length=1, max_length=50, description="slug пользователя")
]
EmployeeFirstName = Annotated[
    str, Field(..., min_length=1, max_length=50, description="Имя пользователя")
]
EmployeeLastName = Annotated[
    str, Field(..., min_length=1, max_length=50, description="Фамилия пользователя")
]


class EmployeeBase(BaseModel):
    username: EmployeeUserName
    first_name: EmployeeFirstName
    last_name: EmployeeLastName


class EmployeeCreate(EmployeeBase):
    pass


class Employee(EmployeeBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)
