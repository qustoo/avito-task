from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

pong_router = APIRouter()


@pong_router.get("/pong", status_code=200)
async def pong_status():
    return PlainTextResponse("ok")
