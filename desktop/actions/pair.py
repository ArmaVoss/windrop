from windrop_api import requests
from ui.pair_dialog import PairDialog


def enable_pairing():
    otp = requests.getQrCode()
    dialog = PairDialog(otp, refresh_fn=requests.getQrCode)
    dialog.exec()
