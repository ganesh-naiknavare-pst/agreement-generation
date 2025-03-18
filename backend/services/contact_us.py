from constants import SMTP2GO_EMAIL_SEND_URL
from config import SMTP2GO_API_KEY, SENDER_EMAIL, CONTACT_MAIL
import requests
import logging

EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>New Issue/Feedback From {name}</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4; text-align: center;">
        <table role="presentation" width="100%" bgcolor="#f4f4f4" cellpadding="0" cellspacing="0" border="0">
            <tr>
                <td align="center" style="padding: 20px;">
                    <table role="presentation" width="600" bgcolor="#ffffff" cellpadding="0" cellspacing="0" border="0" style="max-width: 600px; width: 100%; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);">

                        <!-- Header -->
                        <tr>
                            <td bgcolor="#007bff" style="padding: 15px; font-size: 20px; font-weight: bold; color: #ffffff; text-align: center; border-radius: 8px 8px 0 0;">
                            New Issue/Feedback from {name}
                            </td>
                        </tr>

                        <!-- Content -->
                        <tr>
                            <td style="padding: 20px; font-size: 16px; color: #333333; text-align: left; line-height: 1.5;">
                                <p>Hello,</p>
                                <p>You have received a new issue/feedback from:</p>
                                <p><strong>Requestor Name:</strong> {name}</p>
                                <p><strong>Requestor Email:</strong> {email}</p>
                                <p><strong>Issue/Feedback Details:</strong><br>{email_body}</p>
                                <p>Best regards,</p>
                                <p><strong>Agreement Agent Team</strong></p>
                            </td>
                        </tr>

                        <!-- Footer -->
                        <tr>
                            <td style="padding: 15px; font-size: 14px; color: #666666; text-align: center; border-top: 1px solid #dddddd;">
                                This email was generated automatically. Please do not respond to this email.
                            </td>
                        </tr>

                    </table>
                </td>
            </tr>
        </table>
    </body>
</html>
"""


def send_email(email: str, email_body: str, subject: str, name: str):

    payload = {
        "sender": SENDER_EMAIL,
        "to": [CONTACT_MAIL],
        "subject": subject,
        "html_body": EMAIL_TEMPLATE.format(
            name=name, email=email, email_body=email_body
        ),
    }

    headers = {
        "X-Smtp2go-Api-Key": SMTP2GO_API_KEY,
        "Content-Type": "application/json",
    }

    response = requests.post(SMTP2GO_EMAIL_SEND_URL, headers=headers, json=payload)

    if response.status_code == 200:
        logging.info(f"Email sent successfully to {CONTACT_MAIL}")
    else:
        logging.info(f"Failed to send email to {CONTACT_MAIL}: {response.text}")
