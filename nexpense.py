import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QProgressBar
from googleapiclient.discovery import build
from main_window import MainWindow

app = QApplication(sys.argv)
mainWindow = MainWindow()
mainWindow.show()
sys.exit(app.exec())