from fastapi import APIRouter, Request
from auth.clerk_auth import requires_auth
from pydantic import BaseModel
from services.contact_us import send_email

router = APIRouter()


class Details(BaseModel):
    email: str
    name: str
    subject: str
    email_body: str


@router.post("/contact-us")
@requires_auth
async def contact_us(details: Details, request: Request):
    send_email(details.email, details.email_body, details.subject, details.name)
