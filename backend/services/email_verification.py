from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import random
import time
import requests
from constants import SMTP2GO_EMAIL_SEND_URL, OTP_EXPIRY_SECONDS
from config import SMTP2GO_API_KEY, SENDER_EMAIL
app = FastAPI()

otp_storage = {}

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
    payload = {
        "api_key": SMTP2GO_API_KEY,
        "to": [email],
        "sender": SENDER_EMAIL,
        "subject": "Your OTP for Verification",
        "text_body": f"Your OTP is: {otp}. It is valid for {OTP_EXPIRY_SECONDS // 60} minutes.",
    }
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(SMTP2GO_EMAIL_SEND_URL, json=payload, headers=headers)
        response_data = response.json()
        return response.status_code == 200 and response_data.get("data", {}).get("succeeded", False)
    except requests.exceptions.RequestException:
        return False

def send_otp_endpoint(request: OTPRequest):
    email = request.email
    verification_type = request.type
    otp = generate_otp()
    otp_storage[email] = {"otp": otp, "timestamp": time.time(), "type": verification_type}
    
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
            "message": "OTP verified successfully"
        }
    else:
        return {
            "success": False,
            "type": verification_type,
            "message": "Incorrect OTP. Try again."
        }
