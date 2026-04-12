from pydantic import BaseModel

class OtpResponse(BaseModel):
    otp: str