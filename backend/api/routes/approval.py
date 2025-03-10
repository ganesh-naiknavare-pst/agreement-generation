import os
import shutil
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from api.routes.websocket import notify_clients
from helpers.email_helper import send_rejection_email
from helpers.state_manager import agreement_state, template_agreement_state
from services.doc_agent import delete_temp_file
from services.template_doc_agent import delete_template_file
from pydantic import BaseModel

router = APIRouter()
approved_users = set()
rejected_users = set()


class Data(BaseModel):
    user: str


@router.post("/approve")
async def approve_user(data: Data):
    approved_users.add(data.user)
    response = {"status": "approved", "user_id": data.user, "approved": True}
    await notify_clients(response)
    return JSONResponse(content=response)


@router.post("/reject")
async def reject_user(data: Data):
    rejected_users.add(data.user)

    # Determine the role and name of the person who rejected
    rejected_by_name = None
    rejected_by_role = None

    if data.user == agreement_state.owner_id:
        rejected_by_name = agreement_state.owner_name
        rejected_by_role = "owner"
    elif data.user in agreement_state.tenants:
        rejected_by_name = agreement_state.tenant_names[data.user]
        rejected_by_role = "tenant"
    elif data.user == template_agreement_state.authority_id:
        rejected_by_name = "Authority"
    elif data.user == template_agreement_state.participant_id:
        rejected_by_name = "Participant"

    # Send rejection notifications to all parties
    if rejected_by_name and rejected_by_role:
        send_rejection_email(
            rejected_by_name=rejected_by_name,
            rejected_by_role=rejected_by_role,
            is_template=False,
        )
        delete_temp_file()
        if os.path.exists("./utils"):
            shutil.rmtree("./utils")
    elif rejected_by_name:
        send_rejection_email(rejected_by_name, is_template=True)
        delete_temp_file()
        delete_template_file()

    response = {"status": "rejected", "user_id": data.user, "approved": False}
    await notify_clients(response)
    return JSONResponse(content=response)
