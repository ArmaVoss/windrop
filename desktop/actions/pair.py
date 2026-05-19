from windrop_api import requests
from ui.pair_dialog import PairDialog
from PyQt6.QtWidgets import QMessageBox


def enable_pairing():
    otp = requests.getQrCode()
    if not otp:
        QMessageBox.warning(
            None, "Connection Error", "Something went wrong. Please try again."
        )
        return
    dialog = PairDialog(otp, refresh_fn=requests.getQrCode)
    dialog.exec()
