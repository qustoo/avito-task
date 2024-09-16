import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError, ResponseValidationError

from api import (
    bids_router,
    employee_router,
    organization_responsibles_router,
    organization_router,
    pong_router,
    tenders_router,
)
from core.models.base import Base
from core.models.db_helper import database_helper
from error_response_models import BadRequestErrorResponse
from src.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("my_fastapi_app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with database_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await database_helper.dispose()


app = FastAPI(lifespan=lifespan)


# catch all unexpected entity
@app.exception_handler(RequestValidationError)
@app.exception_handler(ResponseValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError | ResponseValidationError
):
    return BadRequestErrorResponse(
        content=f"Неверные параметры запроса: причина = {str(exc)}"
    )


app.include_router(pong_router, prefix=settings.api.prefix)
app.include_router(bids_router, prefix=settings.api.prefix)
app.include_router(tenders_router, prefix=settings.api.prefix)
app.include_router(employee_router, prefix=settings.api.prefix)
app.include_router(organization_router, prefix=settings.api.prefix)
app.include_router(organization_responsibles_router, prefix=settings.api.prefix)
app.include_router(bids_router, prefix=settings.api.prefix)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
