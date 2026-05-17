import requests
from urllib.parse import urljoin
from .schemas import OtpResponse

BASE_URL = "http://localhost:8000"
API_PATH_PREFIX = "api/v1/"


def getQrCode() -> str:
    path = API_PATH_PREFIX + "/otp/generate"
    full_path = urljoin(BASE_URL, path)

    try:
        response = requests.post(full_path)
        response.raise_for_status()
        otp_response = OtpResponse.model_validate_json(response.text)
        return otp_response.otp
    except requests.HTTPError as e:
        print(f"an error occurred getting qr code {e}")
        return None
    except Exception as e:
        print(f"something went wrong: {e}")
        return None
