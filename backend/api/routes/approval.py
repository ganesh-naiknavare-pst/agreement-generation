from fastapi import APIRouter
from fastapi.responses import JSONResponse
from api.routes.websocket import notify_clients
from helpers.email_helper import send_rejection_email
from helpers.state_manager import agreement_state

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
    
    # Determine the role and name of the person who rejected
    rejected_by_name = None
    rejected_by_role = None
    
    if user == agreement_state.owner_id:
        rejected_by_name = agreement_state.owner_name
        rejected_by_role = "owner"
    elif user in agreement_state.tenant_names:
        rejected_by_name = agreement_state.tenant_names[user]
        rejected_by_role = "tenant"
    
    # Send rejection notifications to all parties
    if rejected_by_name and rejected_by_role:
        send_rejection_email(rejected_by_name, rejected_by_role)
    
    response = {"status": "rejected", "user_id": user, "approved": False}
    await notify_clients(response)
    return JSONResponse(content=response)
