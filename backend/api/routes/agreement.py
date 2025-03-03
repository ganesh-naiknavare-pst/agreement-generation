from fastapi import APIRouter, Request
from services.doc_agent import create_agreement_details, AgreementRequest
from auth.clerk_auth import requires_auth
router = APIRouter()

@router.post("/create-agreement")
@requires_auth
async def create_agreement(agreement: AgreementRequest, request: Request):
    return await create_agreement_details(agreement)
