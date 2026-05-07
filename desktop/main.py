from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from config.config import settings
from actions.pair import enable_pairing

app = QApplication([])
app.setQuitOnLastWindowClosed(False)

icon = QIcon(str(settings.tray_icon_path))

tray = QSystemTrayIcon()
tray.setIcon(icon)
tray.setVisible(True)

menu = QMenu()
action = QAction("Pair")
menu.addAction(action)
action.triggered.connect(enable_pairing)

quit = QAction("Quit")
quit.triggered.connect(app.quit)
menu.addAction(quit)

tray.setContextMenu(menu)

app.exec()
