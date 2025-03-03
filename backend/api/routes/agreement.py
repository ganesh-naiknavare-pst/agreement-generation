from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, Form
from services.doc_agent import create_agreement_details, AgreementRequest
from database.connection import get_db
from prisma import Prisma
from datetime import datetime, timezone
from services.template_doc_agent import template_based_agreement, TemplateAgreementRequest

router = APIRouter()

@router.post("/create-agreement")
async def create_agreement(request: AgreementRequest, db: Prisma = Depends(get_db)):
    agreements = await db.agreement.create(
       data={
            "address": request.property_address,
            "city": request.city,
            "startDate": request.start_date,
        }
    )

    await db.owner.create(
        data={
            "agreementId": agreements.id,
            "name": request.owner_name,
            "email": request.owner_email,
        }
    )
    for tenant in request.tenant_details:
        await db.tenant.create(
            data={
                "agreementId": agreements.id,
                "name": tenant.get("name"),
                "email": tenant.get("email"),
            }
        )

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
