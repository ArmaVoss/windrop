from typing import List

import requests
from pydantic import TypeAdapter
from urllib.parse import urljoin
from .schemas import OtpResponse, Device

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


def getDevices() -> List[Device]:
    path = API_PATH_PREFIX + "/devices"
    full_path = urljoin(BASE_URL, path)

    try:
        response = requests.get(full_path)
        response.raise_for_status()
        adapter = TypeAdapter(List[Device])
        return adapter.validate_json(response.text)
    except requests.HTTPError as e:
        print(f"an error occured get devices {e}")
        return None
    except Exception as e:
        print(f"something went wrong: {e}")
        return None
