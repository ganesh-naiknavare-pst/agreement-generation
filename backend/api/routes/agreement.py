from fastapi import APIRouter
from services.doc_agent import create_agreement_details, AgreementRequest

router = APIRouter()

@router.post("/create-agreement")
async def create_agreement(request: AgreementRequest):
    return await create_agreement_details(request)
