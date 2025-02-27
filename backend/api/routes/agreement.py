from fastapi import APIRouter, Request
from services.doc_agent import create_agreement_details, AgreementRequest
from services.template_doc_agent import template_based_agreement, TemplateAgreementRequest

router = APIRouter()

@router.post("/create-agreement")
async def create_agreement(request: AgreementRequest):
    return await create_agreement_details(request)

@router.post("/create-template-based-agreement")
async def create_template_based_agreement(req: TemplateAgreementRequest):
    return await template_based_agreement(req)
