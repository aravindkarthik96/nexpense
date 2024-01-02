import sys
from PyQt6.QtWidgets import QApplication
from googleapiclient.discovery import build

from main.ui.main_window import MainWindow

app = QApplication(sys.argv)
mainWindow = MainWindow()
mainWindow.show()
sys.exit(app.exec())