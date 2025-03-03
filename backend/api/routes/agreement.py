from fastapi import APIRouter, Depends, HTTPException
from services.doc_agent import create_agreement_details, AgreementRequest
from database.connection import get_db
from prisma import Prisma
from datetime import datetime, timezone

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
