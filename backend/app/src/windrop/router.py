import json
import secrets
import string
from datetime import datetime, timedelta, timezone
from pathlib import Path

import aiofiles
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from fastapi import APIRouter, HTTPException, UploadFile

from config.config import settings
from database.database import database

from .error_codes import INTERNAL_SERVER_ERROR_DESC
from .schemas import (
    DeleteTrustedDeviceRequest,
    EnrollRequest,
    EnrollResponse,
    OtpResponse,
    UpdateDownloadPathRequest,
)
from .utils import create_certificate_from_csr, validate_otp

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

    one_time_password = "".join(
        secrets.choice(ALLOWED_OTP_CHARACTERS) for i in range(8)
    )
    expiry = (
        datetime.now(timezone.utc) + timedelta(seconds=TIME_TO_EXPIRY_SECONDS)
    ).isoformat()

    try:
        database.execute_sql(
            "INSERT INTO otp (token, expiry, used) VALUES (?, ?, ?);",
            params=(one_time_password, expiry, False),
        )
        database.commit()
    except Exception as e:
        print("An error occured with the database", e)
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR_DESC)

    return OtpResponse(otp=one_time_password)


@router.post("/enroll", response_model=EnrollResponse)
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
            params=(client_cert.serial_number, device_name, False),
        )
        database.commit()
    except Exception:
        raise HTTPException(500, INTERNAL_SERVER_ERROR_DESC)

    return EnrollResponse(
        ca_certificate=ca_cert.public_bytes(serialization.Encoding.PEM).decode("utf-8"),
        client_certificate=client_cert.public_bytes(serialization.Encoding.PEM).decode(
            "utf-8"
        ),
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
            params=(delete_device_request.client_certificate_serial_number,),
        )
        database.commit()
    except Exception:
        raise HTTPException(500, INTERNAL_SERVER_ERROR_DESC)


@router.patch("/path/update")
async def update_default_download_dir(
    update_download_path_request: UpdateDownloadPathRequest,
):
    """
    Update the path for uploaded files to save to

    Raises:
        HTTPException: Raises 400 status on bad path requested
    """

    new_download_path = update_download_path_request.download_directory_path
    new_download_path = Path(new_download_path)
    if not new_download_path.exists():
        raise HTTPException(400, "Invalid directory path")

    settings.download_directory = new_download_path
    with open(settings.config_path, "r") as f:
        data = json.load(f)

    data["download_path"] = str(new_download_path)
    with open(settings.config_path, "w") as f:
        json.dump(data, f, indent=4)

    return {"message": "Download directory updated", "path": str(new_download_path)}


@router.post("/upload")
async def upload_files(files: list[UploadFile]):
    """
    Revoke a device from trusted devices

    Returns:
        Response: 200 on success

    Raises:
        HTTPException: Raised with 400 status
    """

    for file in files:
        if not file.filename:
            raise HTTPException(400, "File must have a name")

        file_name = Path(file.filename).name
        dest = settings.download_directory / file_name

        if not dest.resolve().is_relative_to(settings.download_directory.resolve()):
            raise HTTPException(400, "Invalid filename")

        async with aiofiles.open(dest, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):  # 1MB chunks
                await buffer.write(chunk)

    return {"message": "Successfully received all uploaded files"}
