from fastapi import APIRouter, Depends, Request
from helpers.state_manager import agreement_state, template_agreement_state
from database.connection import get_db
from prisma import Prisma
from auth.clerk_auth import requires_auth

router = APIRouter()


class Data:
    agreement_id: int
    user_id: int


@router.get("/rent-agreement-user")
@requires_auth
async def get_rent_agreement_user(
    data: Data, request: Request, db: Prisma = Depends(get_db)
):
    user = await db.userrentagreementstatus.find_many(
        where={"agreementId": data.agreement_id, "userId": data.user_id},
        order={"createdAt": "desc"},
    )
    return user


@router.get("/template-agreement-user")
@requires_auth
async def get_rent_agreement_user(
    data: Data, request: Request, db: Prisma = Depends(get_db)
):
    user = await db.useragreementstatus.find_many(
        where={"agreementId": data.agreement_id, "userId": data.user_id},
        order={"createdAt": "desc"},
    )
    return user
