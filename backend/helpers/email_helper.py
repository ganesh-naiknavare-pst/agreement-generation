import base64
import requests
from constants import SMTP2GO_EMAIL_SEND_URL
from config import SMTP2GO_API_KEY, SENDER_EMAIL
from helpers.state_manager import agreement_state, template_agreement_state
from templates import generate_email_template


def send_rejection_email(rejected_by_name: str, rejected_by_role: str=None, is_template: bool=False):
    """Send rejection notification emails to all parties involved in the agreement."""
    # Get all email addresses
    emails_to_notify = []
    
    # Add owner's email
    if is_template:
        if hasattr(template_agreement_state, 'authority_email') and template_agreement_state.authority_email:
            emails_to_notify.append((template_agreement_state.authority_email, "Authority", template_agreement_state.authority_id))
        if hasattr(template_agreement_state, 'participant_email') and template_agreement_state.participant_email:
            emails_to_notify.append((template_agreement_state.participant_email, "Participant", template_agreement_state.participant_id))
    
        
    else:
        if hasattr(agreement_state, 'owner_email') and agreement_state.owner_email:
            emails_to_notify.append((agreement_state.owner_email, "owner", agreement_state.owner_id))
        # Add all tenants' emails
        for tenant_id in agreement_state.tenants.keys():
            tenant_email = getattr(agreement_state, 'tenant_emails', {}).get(tenant_id)
            if tenant_email:
                emails_to_notify.append((tenant_email, "tenant", tenant_id))

    success_list = []
    failed_list = {}

    for email, role, user_id in emails_to_notify:
        email_body = generate_email_template(
            role=role,
            user_id=user_id,
            is_rejection=True,
            rejected_by=f"{rejected_by_name} ({rejected_by_role})" if rejected_by_name and rejected_by_role else rejected_by_name
        )
        
        payload = {
            "sender": SENDER_EMAIL,
            "to": [email],
            "subject": "Rental Agreement Rejected",
            "html_body": email_body
        }
        
        headers = {
            "X-Smtp2go-Api-Key": SMTP2GO_API_KEY,
            "Content-Type": "application/json",
        }
        
        response = requests.post(SMTP2GO_EMAIL_SEND_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            print(f"Email sent successfully to {email}")
            success_list.append(email)
        else:
            print(f"Failed to send email to {email}: {response.text}")
            failed_list[email] = response.text

    return {"success": success_list, "failed": failed_list}


def send_email_with_attachment(recipient_email: str, pdf_path: str, role: str, is_template: bool=False, user_id=None):

    with open(pdf_path, "rb") as attachment_file:
        file_content = attachment_file.read()
        encoded_file = base64.b64encode(file_content).decode("utf-8")

    # Use the provided user_id for tenants, or owner_id for owner
    if is_template:
        user_id = (template_agreement_state.participant_id if role == "Participant" else template_agreement_state.authority_id)
    else :
        if role == "owner" or user_id is None:
            user_id = agreement_state.owner_id

    email_body = generate_email_template(role, user_id, is_template)

    payload = {
        "sender": SENDER_EMAIL,
        "to": [recipient_email],
        "subject": f"Agreement for {role.capitalize()}" if is_template else f"Rental Agreement for {role.capitalize()}",
        "html_body": email_body,
        "attachments": [
            {
                "fileblob": encoded_file,
                "filename": "agreement.pdf" if is_template else "rental-agreement.pdf",
                "content_type": "application/pdf",
            }
        ],
    }
    headers = {
        "X-Smtp2go-Api-Key": SMTP2GO_API_KEY,
        "Content-Type": "application/json",
    }

    response = requests.post(SMTP2GO_EMAIL_SEND_URL, headers=headers, json=payload)
    if response.status_code == 200:
        print(f"Successfully sent email to {recipient_email}")
    else:
        print(f"Failed to send email to {recipient_email}: {response.text}")
    return response.status_code == 200, response.text
