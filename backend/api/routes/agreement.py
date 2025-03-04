from fastapi import APIRouter, Request, Depends
from services.doc_agent import create_agreement_details, AgreementRequest
from auth.clerk_auth import requires_auth
from database.connection import get_db
from prisma import Prisma

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

    return await create_agreement_details(agreement)
