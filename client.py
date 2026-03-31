import threading
import socket
import sys
from random import choice
from PyQt6.QtWidgets import QWidget, QApplication, QPushButton, QLabel, QLineEdit, QVBoxLayout
from PyQt6.QtCore import Qt

class Client:
    def __init__(self):
        pass

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.addStretch()
        layout.addWidget(QLabel('Login:'), alignment=Qt.AlignmentFlag.AlignCenter)
        login_field = QLineEdit()
        layout.addWidget(login_field, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(QLabel('Password:'), alignment=Qt.AlignmentFlag.AlignCenter)
        password_field = QLineEdit()
        layout.addWidget(password_field, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

        self.setLayout(layout)
        self.setWindowTitle(choice(['🍗', 'Welcome']))
        self.resize(400, 200)
        self.setStyleSheet(r'background-color: #3E282C')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet('''
    QLabel {
        color: #FFEAD0;
        font-size: 12px;
    }
    ''')
    window = MainWindow()
    window.show()
    sys.exit(app.exec())