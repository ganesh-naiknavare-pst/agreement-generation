from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, Form
from services.doc_agent import create_agreement_details, AgreementRequest
from auth.clerk_auth import requires_auth
from database.connection import get_db
from prisma import Prisma
from services.template_doc_agent import (
    template_based_agreement,
    TemplateAgreementRequest,
)
from services.email_verification import send_otp_endpoint, OTPRequest, OTPVerification, verify_otp_endpoint

router = APIRouter()


@router.post("/create-agreement")
@requires_auth
async def create_agreement(
    agreement: AgreementRequest, request: Request, db: Prisma = Depends(get_db)
):
    agreements = await db.agreement.create(
        data={
            "address": agreement.property_address,
            "city": agreement.city,
            "startDate": agreement.start_date,
            "rentAmount": agreement.rent_amount,
            "agreementPeriod": agreement.agreement_period,
        }
    )

    await db.owner.create(
        data={
            "agreementId": agreements.id,
            "name": agreement.owner_name,
            "email": agreement.owner_email,
        }
    )
    for tenant in agreement.tenant_details:
        await db.tenant.create(
            data={
                "agreementId": agreements.id,
                "name": tenant.get("name"),
                "email": tenant.get("email"),
            }
        )

    return await create_agreement_details(agreement, agreements.id, db)


@router.post("/create-template-based-agreement")
async def create_template_based_agreement(
    user_prompt: str = Form(...),
    authority_email: str = Form(...),
    participant_email: str = Form(...),
    file: UploadFile = File(...),
    db: Prisma = Depends(get_db),
):
    req = TemplateAgreementRequest(
        user_prompt=user_prompt,
        authority_email=authority_email,
        participant_email=participant_email,
    )
    agreements = await db.templateagreement.create(
        data={
            "status": "PROCESSING",
        }
    )

    await db.authority.create(
        data={
            "agreementId": agreements.id,
            "email": authority_email,
        }
    )
    await db.participant.create(
        data={
            "agreementId": agreements.id,
            "email": participant_email,
        }
    )
    return await template_based_agreement(req, file, agreements.id, db)


@router.get("/agreements")
async def get_agreements(db: Prisma = Depends(get_db)):
    agreements = await db.agreement.find_many(
        include={
            "owner": True,
            "tenants": True,
        },
        order={"createdAt": "desc"},
    )
    return agreements


@router.get("/template-agreements")
async def get_agreements(db: Prisma = Depends(get_db)):
    agreements = await db.templateagreement.find_many(
        include={
            "authority": True,
            "participant": True,
        },
        order={"createdAt": "desc"},
    )
    return agreements

@router.post("/send-otp")
def send_otp(sendotp: OTPRequest,request: Request):
    return send_otp_endpoint(sendotp)

@router.post("/verify-otp")
def otp_verification(verify_otp: OTPVerification):
    return verify_otp_endpoint(verify_otp)
