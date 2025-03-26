from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from database.connection import get_db
from prisma import Prisma
from auth.clerk_auth import requires_auth

router = APIRouter()


class Data(BaseModel):
    user_id: str
    agreement_id: int
    is_template: bool


@router.get("/rent-agreement-user")
@requires_auth
async def get_rent_agreement_user(
    agreement_id: int, user_id: str, request: Request, db: Prisma = Depends(get_db)
):
    user = await db.userrentagreementstatus.find_first(
        where={"agreementId": agreement_id, "userId": user_id},
    )
    return user


@router.get("/template-agreement-user")
@requires_auth
async def get_template_agreement_user(
    agreement_id: int, user_id: str, request: Request, db: Prisma = Depends(get_db)
):
    user = await db.useragreementstatus.find_first(
        where={"agreementId": agreement_id, "userId": user_id},
    )
    return user


@router.post("/update-user-ids")
@requires_auth
async def get_template_agreement_user(
    data: Data, request: Request, db: Prisma = Depends(get_db)
):
    table = db.templateagreement if data.is_template else db.agreement
    current_agreement = await table.find_first(where={"id": data.agreement_id})
    if data.user_id not in current_agreement.clerkUserIds:
        return await table.update(
            where={"id": data.agreement_id},
            data={"clerkUserIds": {"push": data.user_id}},
        )

    return current_agreement
