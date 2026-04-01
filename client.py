import threading
import socket
import sys
from random import choice
from PyQt6.QtWidgets import QWidget, QApplication, QPushButton, QLabel, QLineEdit, QVBoxLayout, QMessageBox, QTextEdit, QHBoxLayout, QListWidget, QFrame
from PyQt6.QtCore import Qt

class Client:
    def __init__(self):
        pass

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(('192.168.1.31', 9100))
        self.init_login_ui()

    def init_login_ui(self):
        self.layout = QVBoxLayout()

        self.layout.addStretch()

        self.layout.addWidget(QLabel('Username:'), alignment=Qt.AlignmentFlag.AlignCenter)

        self.login_field = QLineEdit()
        self.login_field.setFixedWidth(200)
        self.layout.addWidget(self.login_field, alignment=Qt.AlignmentFlag.AlignCenter)

        password_label = QLabel('Password:')
        password_label.setStyleSheet("padding: 10px 0px 0px 0px;")
        self.layout.addWidget(password_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.password_field = QLineEdit()
        self.password_field.setFixedWidth(200)
        self.password_field.setEchoMode(QLineEdit.EchoMode.Password)
        self.layout.addWidget(self.password_field, alignment=Qt.AlignmentFlag.AlignCenter)

        login_button = QPushButton('Sign in')
        login_button.setFixedWidth(170)
        login_button.clicked.connect(self.send_login_application)
        self.layout.addWidget(login_button, alignment=Qt.AlignmentFlag.AlignCenter)

        register_button = QPushButton('Create an account')
        register_button.setFixedWidth(170)
        register_button.clicked.connect(self.send_register_application)
        self.layout.addWidget(register_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.layout.addStretch()

        self.setLayout(self.layout)
        self.setWindowTitle(choice(['🍗', 'Welcome']))
        self.setStyleSheet('background-color: #141414;')
        self.setFixedSize(1200, 600)


    def send_login_application(self):
        self.send_message(f'{self.login_field.text()}:{self.password_field.text()};login', 128)
        data = self.get_message(128)
        if data != 'SUCCESS':
            QMessageBox.critical(None, 'FAIL', data)
        else:
            QMessageBox.information(None, 'SUCCESS', data)

    def send_register_application(self):
        self.send_message(f'{self.login_field.text()}:{self.password_field.text()};register', 128)
        data = self.get_message(128)
        if data != 'SUCCESS':
            QMessageBox.critical(None, 'FAIL', data)
        else:
            QMessageBox.information(None, 'SUCCESS', data)

    def send_message(self, mess: str, buff: int) -> None:
        mess = f'{mess};'.encode('utf-8')
        self.sock.send(mess + bytearray(buff - len(mess)))

    def get_message(self, buff: int) -> str:
        mess = self.sock.recv(buff).decode('utf-8')
        mess = mess[:mess.rfind(';')]
        return mess

    def init_main_ui(self): # РАЗОБРАТЬСЯ С РАБОТОСПОСОБНОСТЬЮ
        self.clear_layout(self.layout)
        # 1. Твой основной вертикальный макет (как в окне логина)

        # 2. Контейнер для содержимого мессенджера
        self.content_widget = QWidget()
        self.messenger_layout = QHBoxLayout(self.content_widget)
        self.messenger_layout.setContentsMargins(0, 0, 0, 0)
        self.messenger_layout.setSpacing(0)

        # --- ЛЕВАЯ ПАНЕЛЬ (Список чатов) ---
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(260)
        self.sidebar.addItems(["Избранное", "Павел Дуров", "Рабочий чат", "Python Dev", "Мама"])
        self.sidebar.setStyleSheet("""
                    QListWidget {
                        background-color: #ffffff;
                        border-right: 1px solid #d3d3d3;
                        outline: none;
                    }
                    QListWidget::item {
                        padding: 15px;
                        border-bottom: 1px solid #f0f0f0;
                    }
                    QListWidget::item:selected {
                        background-color: #2b5278;
                        color: white;
                    }
                """)

        # --- ПРАВАЯ ПАНЕЛЬ (Окно чата) ---
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setContentsMargins(0, 0, 0, 0)
        self.chat_layout.setSpacing(0)

        # Верхняя плашка с именем собеседника
        self.header = QLabel("Выберите чат")
        self.header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header.setFixedHeight(50)
        self.header.setStyleSheet("background-color: #ffffff; font-weight: bold; border-bottom: 1px solid #d3d3d3;")

        # Область вывода сообщений
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("border: none; background-color: #e7ebf0; padding: 10px;")

        # Нижняя панель ввода
        self.input_frame = QFrame()
        self.input_frame.setFixedHeight(60)
        self.input_frame.setStyleSheet("background-color: white; border-top: 1px solid #d3d3d3;")
        self.input_layout = QHBoxLayout(self.input_frame)

        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Написать сообщение...")
        self.message_input.setStyleSheet("border: 1px solid #ccc; border-radius: 5px; padding: 5px;")

        self.send_button = QPushButton("Отправить")
        self.send_button.setStyleSheet("background-color: #2b5278; color: white; border-radius: 5px; padding: 6px 15px;")

        self.input_layout.addWidget(self.message_input)
        self.input_layout.addWidget(self.send_button)

        # Сборка правой панели
        self.chat_layout.addWidget(self.header)
        self.chat_layout.addWidget(self.chat_display)
        self.chat_layout.addWidget(self.input_frame)

        # 3. Добавляем части в горизонтальный макет
        self.messenger_layout.addWidget(self.sidebar)
        self.messenger_layout.addWidget(self.chat_container)

        # 4. Помещаем весь мессенджер в твой основной QVBoxLayout
        self.layout.addWidget(self.content_widget)

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    # deleteLater schedules the widget for deletion
                    widget.deleteLater()
                else:
                    # Recursively clear nested layouts
                    self.clear_layout(item.layout())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet('''
    QLabel {
        color: #dad085;
        font-size: 14px;
        font-family: Consolas;
    }
    QLineEdit {
        color: #dad085;
        font-size: 12px;
        font-family: Consolas;
    }
    QPushButton {
        background-color: #141414;
        color: #dad085;
        font-size: 14px;
        font-family: Consolas;
    }
    QPushButton:hover {
        background-color: #141414;
        color: #f7f7f2;
        font-size: 14px;
        font-family: Consolas;
    }
    QPushButton:pressed {
        background-color: #3c3c57;
        color: #f8f8f8;
        font-size: 14px;
        font-family: Consolas;
    }
    ''')
    window = MainWindow()
    window.show()
    sys.exit(app.exec())