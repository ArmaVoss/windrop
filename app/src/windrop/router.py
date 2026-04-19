import secrets 
import string 
import database

from .utils import validate_otp, create_certificate_from_csr
from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone, timedelta
from database.database import database
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from .schemas import OtpResponse, EnrollRequest, EnrollResponse
from .error_codes import INTERNAL_SERVER_ERROR_DESC
from config.config import settings

ALLOWED_OTP_CHARACTERS = string.ascii_letters + string.digits
TIME_TO_EXPIRY_SECONDS = 60.0
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
    expiry = (datetime.now(timezone.utc) + timedelta(seconds=60)).isoformat()

    try:
        database.execute_sql(
            "INSERT INTO otp (token, expiry, used) VALUES (?, ?, ?);",
            params=(one_time_password, expiry , False)
        )
        database.commit()
    except Exception as e:
        print("An error occured with the database", e)
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR_DESC)

    return OtpResponse(otp=one_time_password)

@router.post(
    "/enroll",
    response_model=EnrollResponse
)
async def enroll(request_to_enroll: EnrollRequest):
    """
    Enroll a device to connect with our service

    Returns:
        EnrollResponse: cert
    
    Raises:
        HTTPExcpetion: Raised with 500 status 
        HTTPException: Raised with 401 status
    """
    certfiicate_signing_request = request_to_enroll.signing_request 
    one_time_password = request_to_enroll.otp
    device_name = request_to_enroll.device_name

    try:
        validate_otp(one_time_password)
    except HTTPException:
        raise
    
    with open(settings.certificate_authority.ca_cert_path, "rb") as f:
        cert_data = f.read()

    ca_cert = x509.load_pem_x509_certificate(cert_data)
    
    with open(settings.certificate_authority.ca_key_path, "rb") as f:
        ca_private_key = serialization.load_pem_private_key(f.read(), password=None)


    # create cert use csr, and sign it using our ca private key
    # add device to list of trusted devices 
    client_cert = create_certificate_from_csr(
        ca_private_key,
        certfiicate_signing_request,
        device_name,
        ca_cert.issuer,
    )

    return EnrollResponse(
        ca_certificate=ca_cert,
        client_certificate=client_cert
    )

@router.post("/upload")
async def upload():
    return None