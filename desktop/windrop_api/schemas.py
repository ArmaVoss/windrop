from pydantic import BaseModel


class OtpResponse(BaseModel):
    otp: str


class Device(BaseModel):
    device_name: str
    cert_serial_number: int
