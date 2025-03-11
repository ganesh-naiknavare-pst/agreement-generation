from helpers.state_manager import agreement_state
from services.doc_agent import save_base64_image
from services.template_doc_agent import (
    template_based_agreement,
    TemplateAgreementRequest,
)
from pydantic import BaseModel
from typing import Optional


class Data(BaseModel):
    user: str
    imageUrl: Optional[str] = ""
    signature: Optional[str] = ""
    agreement_type: str


async def image_and_sign_upload(agreement: Data):
    if agreement.user == agreement_state.owner_id:
        agreement_state.owner_photo = save_base64_image(
            agreement.imageUrl, agreement_state.owner_name
        )
        agreement_state.owner_signature = save_base64_image(
            agreement.signature, agreement_state.owner_name, is_signature=True
        )

    elif agreement.user in agreement_state.tenants.keys():
        tenant_photo_path = save_base64_image(
            agreement.imageUrl, agreement_state.tenant_names[agreement.user]
        )
        tenant_signature_path = save_base64_image(
            agreement.signature,
            agreement_state.tenant_names[agreement.user],
            is_signature=True,
        )
        agreement_state.update_tenant(
            tenant_signature_path, tenant_photo_path, agreement.user
        )
