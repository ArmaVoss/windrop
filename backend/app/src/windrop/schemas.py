from pydantic import BaseModel


class Device(BaseModel):
    device_name: str
    cert_serial_number: int


class OtpResponse(BaseModel):
    otp: str


class EnrollRequest(BaseModel):
    device_name: str
    signing_request: str
    otp: str


class EnrollResponse(BaseModel):
    ca_certificate: str
    client_certificate: str


class DeleteTrustedDeviceRequest(BaseModel):
    client_certificate_serial_number: str


class UpdateDownloadPathRequest(BaseModel):
    download_directory_path: str
