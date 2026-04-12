import secrets 
import string 
import database

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone, timedelta
from database.database import database
from .schemas import OtpResponse

ALLOWED_OTP_CHARACTERS = string.ascii_letters + string.digits
TIME_TO_EXPIRY_SECONDS = 60.0
INTERAL_SERVER_ERROR_DESC = "Internal Server Error"
router = APIRouter(prefix="/api/v1")

@router.post(
    "/otp/generate",
    response_model=OtpResponse,
)
async def generate_otp():
    """
    Generate a OTP for pairing

    Returns:
        OtpResponse: Otp object generated 

    Raises:
        HTTPException: Raised with status 500 
    """

    one_time_password = ''.join(secrets.choice(ALLOWED_OTP_CHARACTERS) for i in range(8))
    expiry = datetime.now(timezone.utc) + timedelta(seconds=TIME_TO_EXPIRY_SECONDS)
    expiry = expiry.strftime("%Y-%m-%d %H:%M:%S") 

    try:
        database.execute_sql(
            "INSERT INTO otp (token, expiry, used) VALUES (?, ?, ?)",
            params=(one_time_password, expiry , False)
        )
    except Exception as e:
        print("An error occured with the database", e)
        raise HTTPException(status_code=500, detail=INTERAL_SERVER_ERROR_DESC)

    return OtpResponse(otp=one_time_password)

@router.get("/enroll")
async def enroll():
    return None

@router.post("/upload")
async def upload():
    return None