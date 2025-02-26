import base64
import requests
from constants import SMTP2GO_EMAIL_SEND_URL
from config import SMTP2GO_API_KEY, SENDER_EMAIL, BASE_APPROVAL_URL
from helpers.state_manager import agreement_state


def generate_email_template(role: str, user_id: str) -> str:
    approve_url = f"{BASE_APPROVAL_URL}/{user_id}/approve"
    reject_url = f"{BASE_APPROVAL_URL}/{user_id}/reject"

    if agreement_state.is_fully_approved():
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Agreement Fully Approved</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    padding: 20px;
                    background-color: #f4f4f4;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: #fff;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <p>Hello,</p>
                <p>The rental agreement has been approved</p>
                <p>Please find the signed agreement attached for your reference.</p>
                <p>Best regards,<br>Docu Sign Team</p>
            </div>
        </body>
        </html>
        """

    else:
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Rental Agreement for {role}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    padding: 20px;
                    background-color: #f4f4f4;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: #fff;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                }}
                .button {{
                    display: inline-block;
                    padding: 10px 20px;
                    margin: 10px 5px;
                    border-radius: 5px;
                    text-decoration: none;
                    color: white;
                }}
                .approve {{
                    background-color: #28a745;
                }}
                .reject {{
                    background-color: #dc3545;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <p>Hello,</p>
                <p>Please review and sign the attached rental agreement document.</p>
                <p>Click on one of the following links to approve or reject the agreement:</p>
                <p>
                    <a href="{approve_url}" class="button approve">Approve Agreement</a>
                    <a href="{reject_url}" class="button reject">Reject Agreement</a>
                </p>
                <p>Best regards,<br>Docu Sign Team</p>
            </div>
        </body>
        </html>
        """

def send_email_with_attachment(recipient_email: str, pdf_path: str, role: str):

    with open(pdf_path, "rb") as attachment_file:
        file_content = attachment_file.read()
        encoded_file = base64.b64encode(file_content).decode("utf-8")

    user_id = (
        agreement_state.tenant_id if role == "tenant" else agreement_state.owner_id
    )
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
    return response.status_code == 200, response.text
