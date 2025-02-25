from fastapi import APIRouter
from fastapi.responses import JSONResponse
from api.routes.websocket import notify_clients

router = APIRouter()
approved_users = set()
rejected_users = set()


@router.get("/sign/{user}/approve")
async def approve_user(user: str):
    approved_users.add(user)
    response = {"status": "approved", "user_id": user, "approved": True}
    await notify_clients(response)
    return JSONResponse(content=response)


@router.get("/sign/{user}/reject")
async def reject_user(user: str):
    rejected_users.add(user)
    response = {"status": "rejected", "user_id": user, "approved": False}
    await notify_clients(response)
    return JSONResponse(content=response)
