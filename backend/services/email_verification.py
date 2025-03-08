from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import random
import time
import requests
from constants import SMTP2GO_EMAIL_SEND_URL
from config import SMTP2GO_API_KEY, SENDER_EMAIL
app = FastAPI()

# OTP Settings
OTP_EXPIRY_SECONDS = 120  # OTP valid for 120 seconds
MAX_ATTEMPTS = 3
otp_storage = {} 

class OTPRequest(BaseModel):
    email: str

class OTPVerification(BaseModel):
    email: str
    otp: str

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
    otp = generate_otp()
    otp_storage[email] = {"otp": otp, "timestamp": time.time(), "attempts": 0}
    
    if send_otp(email, otp):
        return {"message": "OTP sent successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to send OTP")

def verify_otp_endpoint(request: OTPVerification):
    email = request.email
    user_otp = request.otp

    if email not in otp_storage:
        raise HTTPException(status_code=400, detail="No OTP found for this email")

    otp_data = otp_storage[email]
    if time.time() - otp_data["timestamp"] > OTP_EXPIRY_SECONDS:
        del otp_storage[email]
        raise HTTPException(status_code=400, detail="OTP expired. Request a new one.")

    if otp_data["attempts"] >= MAX_ATTEMPTS:
        del otp_storage[email]
        raise HTTPException(status_code=400, detail="Maximum attempts reached. Request a new OTP.")

    otp_data["attempts"] += 1
    if user_otp == otp_data["otp"]:
        del otp_storage[email]
        return {"success": True, "message": "OTP verified successfully"}  # ✅ Ensure this is returned
    else:
        raise HTTPException(status_code=400, detail="Incorrect OTP. Try again.")
