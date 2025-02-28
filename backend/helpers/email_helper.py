import base64
import requests
from constants import SMTP2GO_EMAIL_SEND_URL
from config import SMTP2GO_API_KEY, SENDER_EMAIL
from helpers.state_manager import agreement_state
from templates import generate_email_template


def send_email_with_attachment(recipient_email: str, pdf_path: str, role: str, user_id=None):

    with open(pdf_path, "rb") as attachment_file:
        file_content = attachment_file.read()
        encoded_file = base64.b64encode(file_content).decode("utf-8")

    # Use the provided user_id for tenants, or owner_id for owner
    if role == "owner" or user_id is None:
        user_id = agreement_state.owner_id  # fallback, though this shouldn't happen

    email_body = generate_email_template(role, user_id)

    payload = {
        "sender": SENDER_EMAIL,
        "to": [recipient_email],
        "subject": f"Rental Agreement for {role.capitalize()}",
        "html_body": email_body,
        "attachments": [
            {
                "fileblob": encoded_file,
                "filename": "rental-agreement.pdf",
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
