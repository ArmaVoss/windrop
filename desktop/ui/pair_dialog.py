import io
from typing import Callable
import qrcode
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout, QPushButton

TIME_TO_EXPIRY_SECONDS = 60


class PairDialog(QDialog):
    def __init__(self, otp: str, refresh_fn: Callable[[], str], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pair Device")
        self.setFixedSize(300, 400)
        self._refresh_fn = refresh_fn
        self._remaining = TIME_TO_EXPIRY_SECONDS

        layout = QVBoxLayout()
        layout.setSpacing(12)

        self._instruction = QLabel("Scan this code with your device to pair:")
        self._instruction.setWordWrap(True)
        layout.addWidget(self._instruction)

        self._qr_label = QLabel()
        self._qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._qr_label.setPixmap(self._make_qr_pixmap(otp, size=240))
        layout.addWidget(self._qr_label)

        self._countdown_label = QLabel(self._countdown_text())
        self._countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._countdown_label)

        self._refresh_btn = QPushButton("Refresh")
        self._refresh_btn.setVisible(False)
        self._refresh_btn.clicked.connect(self._refresh)
        layout.addWidget(self._refresh_btn)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self.setLayout(layout)

        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._tick)
        self._timer.start()

    def _tick(self):
        self._remaining -= 1
        self._countdown_label.setText(self._countdown_text())
        if self._remaining <= 0:
            self._timer.stop()
            self._on_expired()

    def _on_expired(self):
        self._qr_label.setPixmap(QPixmap())
        self._instruction.setText("QR code expired.")
        self._countdown_label.setText("Expires in 0s")
        self._refresh_btn.setVisible(True)

    def _refresh(self): 
        self._remaining = TIME_TO_EXPIRY_SECONDS
        otp = self._refresh_fn()
        self._qr_label.setPixmap(self._make_qr_pixmap(otp, size=240))
        self._instruction.setText("Scan this code with your device to pair:")
        self._refresh_btn.setVisible(False)
        self._countdown_label.setText(self._countdown_text())
        self._timer.start()

    def _countdown_text(self) -> str:
        return f"Expires in {self._remaining}s"

    def _make_qr_pixmap(self, data: str, size: int) -> QPixmap:
        img = qrcode.make(data)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        pixmap = QPixmap()
        pixmap.loadFromData(buf.getvalue(), "PNG")
        return pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
