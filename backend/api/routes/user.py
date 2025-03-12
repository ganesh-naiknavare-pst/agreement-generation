from fastapi import APIRouter, Depends, Request
from database.connection import get_db
from prisma import Prisma
from auth.clerk_auth import requires_auth

router = APIRouter()


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
