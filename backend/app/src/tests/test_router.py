import sqlite3
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from fastapi import HTTPException
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


@pytest.fixture
def enrollment_setup():
    ca_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    ca_cert = (
        x509.CertificateBuilder()
        .subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Test CA")]))
        .issuer_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Test CA")]))
        .public_key(ca_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(timezone.utc))
        .not_valid_after(datetime.now(timezone.utc) + timedelta(days=365))
        .sign(ca_key, hashes.SHA256())
    )
    ca_cert_pem = ca_cert.public_bytes(serialization.Encoding.PEM)
    ca_key_pem = ca_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption(),
    )

    client_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    csr_pem = (
        x509.CertificateSigningRequestBuilder()
        .subject_name(
            x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "test-device")])
        )
        .sign(client_key, hashes.SHA256())
        .public_bytes(serialization.Encoding.PEM)
        .decode("utf-8")
    )

    mock_cert_file = MagicMock()
    mock_cert_file.__enter__ = lambda s: s
    mock_cert_file.__exit__ = MagicMock(return_value=False)
    mock_cert_file.read.return_value = ca_cert_pem

    mock_key_file = MagicMock()
    mock_key_file.__enter__ = lambda s: s
    mock_key_file.__exit__ = MagicMock(return_value=False)
    mock_key_file.read.return_value = ca_key_pem

    return {
        "csr_pem": csr_pem,
        "mock_cert_file": mock_cert_file,
        "mock_key_file": mock_key_file,
    }


def test_otp_generation_happy():
    with patch("windrop.router.database") as mock_db:
        mock_db.execute_sql = MagicMock()
        mock_db.commit = MagicMock()

        response = client.post("/api/v1/otp/generate")

        assert response.status_code == 200
        json_response: dict = response.json()
        assert "otp" in json_response
        assert len(json_response["otp"]) == 8


def test_enrollment_endpoint_happy(enrollment_setup):
    csr_pem = enrollment_setup["csr_pem"]
    mock_cert_file = enrollment_setup["mock_cert_file"]
    mock_key_file = enrollment_setup["mock_key_file"]

    with (
        patch("windrop.router.database") as mock_db,
        patch("windrop.router.validate_otp"),
        patch("builtins.open", side_effect=[mock_cert_file, mock_key_file]),
    ):
        mock_db.execute_sql = MagicMock()
        mock_db.commit = MagicMock()

        response = client.post(
            "/api/v1/enroll",
            json={
                "signing_request": csr_pem,
                "otp": "testOTP1",
                "device_name": "test-device",
            },
        )

        assert response.status_code == 200
        json_response: dict = response.json()
        assert "ca_certificate" in json_response
        assert "client_certificate" in json_response
        assert "BEGIN CERTIFICATE" in json_response["ca_certificate"]
        assert "BEGIN CERTIFICATE" in json_response["client_certificate"]


def test_enrollment_endpoint_invalid_otp(enrollment_setup):
    csr_pem = enrollment_setup["csr_pem"]
    mock_cert_file = enrollment_setup["mock_cert_file"]
    mock_key_file = enrollment_setup["mock_key_file"]

    with (
        patch("windrop.router.validate_otp") as mock_otp,
        patch("builtins.open", side_effect=[mock_cert_file, mock_key_file]),
    ):
        mock_otp.side_effect = HTTPException(
            status_code=401, detail="Invalid one time password"
        )
        response = client.post(
            "/api/v1/enroll",
            json={
                "signing_request": csr_pem,
                "otp": "testOTP1",
                "device_name": "test-device",
            },
        )
        assert response.status_code == 401


def test_revoke_device():
    with patch("windrop.router.database") as mock_db:
        mock_db.execute_sql = MagicMock()
        mock_db.commit = MagicMock()

        response = client.patch(
            "/api/v1/device/revoke",
            json={
                "client_certificate_serial_number": "1234567",
            },
        )

        assert response.status_code == 200


def test_revoke_device_db_error():
    with patch("windrop.router.database") as mock_db:
        mock_db.execute_sql = MagicMock()
        mock_db.commit.side_effect = sqlite3.OperationalError("database is locked")

        response = client.patch(
            "/api/v1/device/revoke",
            json={
                "client_certificate_serial_number": "1234567",
            },
        )

        assert response.status_code == 500
