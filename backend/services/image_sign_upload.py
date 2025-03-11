from helpers.state_manager import agreement_state, template_agreement_state
from services.doc_agent import save_base64_image
from pydantic import BaseModel
from typing import Optional


class Data(BaseModel):
    user: str
    imageUrl: Optional[str] = ""
    signature: Optional[str] = ""


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

async def image_and_sign_upload_for_template(agreement: Data):
    if agreement.user == template_agreement_state.authority_id:
        template_agreement_state.authority_signature = save_base64_image(
            agreement.signature, template_agreement_state.authority_email, is_signature=True
        )

    elif agreement.user == template_agreement_state.participant_id: 
        template_agreement_state.participant_signature = save_base64_image(
            agreement.signature,
            template_agreement_state.participant_email,
            is_signature=True,
        )
