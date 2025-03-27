from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import random
import time
import requests
from constants import SMTP2GO_EMAIL_SEND_URL, OTP_EXPIRY_SECONDS
from config import SMTP2GO_API_KEY, SENDER_EMAIL

app = FastAPI()

otp_storage = {}

EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your OTP for Verification</title>
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4; text-align: center;">

    <table role="presentation" width="100%" bgcolor="#f4f4f4" cellpadding="0" cellspacing="0" border="0">
        <tr>
            <td align="center" style="padding: 20px;">
                <table role="presentation" width="600" bgcolor="#ffffff" cellpadding="0" cellspacing="0" border="0" style="max-width: 600px; width: 100%; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);">

                    <!-- Header -->
                    <tr>
                        <td bgcolor="#007bff" style="padding: 15px; font-size: 20px; font-weight: bold; color: #ffffff; text-align: center; border-radius: 8px 8px 0 0;">
                            OTP Verification Code
                        </td>
                    </tr>

                    <!-- Content -->
                    <tr>
                        <td style="padding: 20px; font-size: 16px; color: #333333; text-align: left; line-height: 1.5;">
                            <p>Hello,</p>
                            <p>Your One-Time Password (OTP) for verification is:</p>

                            <!-- OTP Box -->
                            <div style="text-align: center; margin: 10px 0;">
                                <input type="text" value="{otp}" id="otpInput"
                                       style="font-size: 20px; text-align: center; font-weight: bold; border: 2px solid #007bff; border-radius: 5px; padding: 5px; width: 150px; background-color: #f8f9fa; color: #007bff;"
                                       readonly>
                            </div>

                            <p>This OTP is valid for {expiry} minutes.</p>
                            <p>If you did not request this OTP, please ignore this email.</p>
                            <p>Best regards,</p>
                            <p><strong>Agreement Agent Team</strong></p>
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="padding: 15px; font-size: 14px; color: #666666; text-align: center; border-top: 1px solid #dddddd;">
                            This email was generated automatically for security purposes. Please do not respond to this email.
                        </td>
                    </tr>

                </table>
            </td>
        </tr>
    </table>

</body>
</html>

"""


class OTPRequest(BaseModel):
    email: EmailStr
    type: str


class OTPVerification(BaseModel):
    email: EmailStr
    otp: str
    type: str


# Generate a random OTP
def generate_otp():
    return str(random.randint(100000, 999999))


# Send OTP via SMTP2GO API
def send_otp(email, otp):
    email_template = EMAIL_TEMPLATE.format(otp=otp, expiry=OTP_EXPIRY_SECONDS // 60)

    payload = {
        "api_key": SMTP2GO_API_KEY,
        "to": [email],
        "sender": SENDER_EMAIL,
        "subject": "Your OTP for Verification",
        "html_body": email_template,
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(SMTP2GO_EMAIL_SEND_URL, json=payload, headers=headers)
        response_data = response.json()
        return response.status_code == 200 and response_data.get("data", {}).get(
            "succeeded", False
        )
    except requests.exceptions.RequestException:
        return False


def send_otp_endpoint(request: OTPRequest):
    email = request.email
    verification_type = request.type
    otp = generate_otp()
    otp_storage[email] = {
        "otp": otp,
        "timestamp": time.time(),
        "type": verification_type,
    }

    if send_otp(email, otp):
        return {"message": "OTP sent successfully", "type": verification_type}
    else:
        raise HTTPException(status_code=500, detail="Failed to send OTP")


def verify_otp_endpoint(request: OTPVerification):
    email = request.email
    user_otp = request.otp
    verification_type = request.type

    if email not in otp_storage:
        raise HTTPException(status_code=400, detail="No OTP found for this email")

    otp_data = otp_storage[email]
    if time.time() - otp_data["timestamp"] > OTP_EXPIRY_SECONDS:
        del otp_storage[email]
        raise HTTPException(status_code=400, detail="OTP expired. Request a new one.")

    if verification_type != otp_data["type"]:
        raise HTTPException(status_code=400, detail="Invalid verification type")

    if user_otp == otp_data["otp"]:
        del otp_storage[email]
        return {
            "success": True,
            "type": verification_type,
            "message": "OTP verified successfully",
        }
    else:
        return {
            "success": False,
            "type": verification_type,
            "message": "Incorrect OTP. Try again.",
        }
