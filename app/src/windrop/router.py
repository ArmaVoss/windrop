import secrets 
import string 
import aiofiles

from pathlib import Path 
from .utils import validate_otp, create_certificate_from_csr
from fastapi import APIRouter, HTTPException, File, UploadFile
from datetime import datetime, timezone, timedelta
from database.database import database
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from .schemas import OtpResponse, EnrollRequest, EnrollResponse, DeleteTrustedDeviceRequest
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
    expiry = (datetime.now(timezone.utc) + timedelta(seconds=TIME_TO_EXPIRY_SECONDS)).isoformat()

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
    certficate_signing_request = request_to_enroll.signing_request 
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

    client_cert = create_certificate_from_csr(
        ca_private_key,
        certficate_signing_request,
        device_name,
        ca_cert.subject,
    )

    try:
        database.execute_sql(
            "INSERT into trusted_devices (cert_serial_number, device_name, revoked) values (?, ?, ?)",
            params=(client_cert.serial_number, device_name, False)
        )
        database.commit()
    except Exception as e:
        raise HTTPException(500, INTERNAL_SERVER_ERROR_DESC)
    
    return EnrollResponse(
        ca_certificate=ca_cert.public_bytes(serialization.Encoding.PEM).decode("utf-8"),
        client_certificate=client_cert.public_bytes(serialization.Encoding.PEM).decode("utf-8")
    )

@router.patch("/device/revoke")
async def revoke_device(delete_device_request: DeleteTrustedDeviceRequest):
    """
    Revoke a device from trusted devices

    Raises:
        HTTPException: Raised with 500 status 
    """

    try:
        database.execute_sql(
            "UPDATE trusted_devices SET revoked = TRUE WHERE cert_serial_number = ?;",
            params=(delete_device_request.client_certificate_serial_number,)
        )
        database.commit()
    except Exception as e:
        raise HTTPException(500, INTERNAL_SERVER_ERROR_DESC)

@router.post("/upload")
async def upload_files(files: list[UploadFile]):
    for file in files:
        if not file.filename:
            raise HTTPException(400, "File must have a name")

        file_name = Path(file.filename).name
        dest = settings.default_download_directory / file_name

        if not dest.resolve().is_relative_to(settings.default_download_directory.resolve()):
            raise HTTPException(400, "Invalid filename")

        async with aiofiles.open(dest, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):  # 1MB chunks
                await buffer.write(chunk)