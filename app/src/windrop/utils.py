from datetime import datetime, timedelta, timezone

from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.x509.oid import NameOID
from fastapi import HTTPException

from database.database import database

from .error_codes import INTERNAL_SERVER_ERROR_DESC

ISSUED_CERT_TIME_TO_EXPIRY_DAYS = 365


def validate_otp(one_time_password) -> bool:
    """
    Validate one time password

    Input:
        one_time_password: otp

    Raises:
        HTTPExcpetion: Raised with 500 status
        HTTPException: Raised with 401 status
    """
    try:
        otp_exists = database.execute_sql(
            """SELECT * 
            FROM otp 
            WHERE otp.token = ?;
            """,
            one_time_password,
        )

    except Exception:
        raise HTTPException(500, INTERNAL_SERVER_ERROR_DESC)
    otp_data = otp_exists.fetchone()
    if not otp_data:
        raise HTTPException(401, "Invalid one time password")

    expiry = datetime.fromisoformat(otp_data["expiry"])
    if datetime.now(timezone.utc) > expiry:
        raise HTTPException(401, "OTP expired")

    if otp_data["used"] == 1:
        raise HTTPException(401, "OTP already used")


def create_certificate_from_csr(ca_private_key, csr, device_name, issuer):
    device_subject = x509.Name(
        [
            x509.NameAttribute(NameOID.COMMON_NAME, device_name),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "WinDrop"),
        ]
    )

    csr = x509.load_pem_x509_csr(csr)

    return (
        x509.CertificateBuilder()
        .subject_name(device_subject)
        .issuer_name(issuer)
        .public_key(csr.public_key())
        .not_valid_before(datetime.now(timezone.utc))
        .not_valid_after(
            datetime.now(timezone.utc) + timedelta(days=ISSUED_CERT_TIME_TO_EXPIRY_DAYS)
        )
        .serial_number(x509.random_serial_number())
        .add_extension(
            x509.SubjectAlternativeName([x509.DNSName("localhost")]),
            critical=False,
        )
        .sign(ca_private_key, hashes.SHA256())
    )
