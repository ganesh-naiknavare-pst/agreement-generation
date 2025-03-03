from fastapi import APIRouter, Request, UploadFile, File, Form
from services.doc_agent import create_agreement_details, AgreementRequest
from services.template_doc_agent import template_based_agreement, TemplateAgreementRequest

router = APIRouter()

@router.post("/create-agreement")
async def create_agreement(request: AgreementRequest):
    return await create_agreement_details(request)

@router.post("/create-template-based-agreement")
async def create_template_based_agreement(
    user_prompt: str = Form(...),
    authority_email: str = Form(...),
    participent_email: str = Form(...),
    file: UploadFile = File(...)
):
    req = TemplateAgreementRequest(
        user_prompt=user_prompt,
        authority_email=authority_email,
        participent_email=participent_email
    )
    return await template_based_agreement(req, file)