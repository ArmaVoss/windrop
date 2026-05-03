from pydantic import BaseModel


class OtpResponse(BaseModel):
    otp: str


class EnrollRequest(BaseModel):
    signing_request: str
    otp: str
    device_name: str


class EnrollResponse(BaseModel):
    ca_certificate: str
    client_certificate: str


class DeleteTrustedDeviceRequest(BaseModel):
    client_certificate_serial_number: str


class UpdateDownloadPathRequest(BaseModel):
    download_directory_path: str
