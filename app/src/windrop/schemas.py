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