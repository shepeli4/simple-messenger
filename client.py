import json
import threading
import socket
import sys
from random import choice
from PyQt6.QtWidgets import QWidget, QApplication, QPushButton, QLabel, QLineEdit, QVBoxLayout, QMessageBox, QListWidgetItem, QHBoxLayout, QListWidget, QFrame
from PyQt6.QtCore import Qt
from os import getcwd, path


class MessageBubble(QWidget):
    """Виджет отдельного сообщения (бабла)"""

    def __init__(self, text, is_user=True):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        self.label = QLabel(text)
        self.label.setWordWrap(True)
        self.label.setMaximumWidth(400)  # Ограничиваем ширину сообщения

        # Стили баблов: пользователь справа, собеседник слева
        if is_user:
            bg_color = "#1b1b1b"  # Чуть светлее фона
            layout.addStretch()
            layout.addWidget(self.label)
            self.label.setStyleSheet(f"background-color: {bg_color}; border: 1px solid #333; border-radius: 10px; padding: 10px;")
        else:
            bg_color = "#141414"
            layout.addWidget(self.label)
            layout.addStretch()
            self.label.setStyleSheet(f"background-color: {bg_color}; border: 1px solid #dad085; border-radius: 10px; padding: 10px;")


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
        register_button.clicked.connect(lambda: self.send_login_application(True))
        self.layout.addWidget(register_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.layout.addStretch()

        self.setLayout(self.layout)
        self.setWindowTitle(choice(['🍗', 'Welcome']))
        self.setStyleSheet('background-color: #141414;')
        self.setFixedSize(1200, 600)


    def init_main_ui(self):
        self.clear_layout(self.layout)
        # Контент мессенджера
        self.content_widget = QWidget()
        self.content_layout = QHBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)

        # --- ЛЕВАЯ ПАНЕЛЬ ---
        self.left_panel = QFrame()
        self.left_panel.setFixedWidth(260)
        self.left_panel.setStyleSheet('border-right: 1px solid #333;')
        self.left_layout = QVBoxLayout(self.left_panel)

        self.settings_btn = QPushButton('Settings')
        self.settings_btn.setFixedHeight(45)
        self.settings_btn.setStyleSheet('QPushButton { border: 1px solid #333; margin: 5px; border-radius: 5px; } QPushButton:hover { background-color: #1b1b1b; }')
        # self.settings_btn.clicked.connect(lambda: self.receive_message(self.msg_input.text().strip()))

        self.contacts = QListWidget()
        self.contacts.addItems(list(self.messages.keys()))
        self.contacts.setStyleSheet('''
                    QListWidget { border: none; outline: none; }
                    QListWidget::item { height: 60px; padding-left: 15px; border-bottom: 1px solid #222; }
                    QListWidget::item:selected { background-color: #1b1b1b; color: #dad085; }
                ''')
        self.contacts.itemSelectionChanged.connect(self.change_companion)

        self.left_layout.addWidget(self.settings_btn)
        self.left_layout.addWidget(self.contacts)

        # --- ПРАВАЯ ПАНЕЛЬ ---
        self.right_panel = QFrame()
        self.right_layout = QVBoxLayout(self.right_panel)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(0)

        self.chat_header = QLabel('Companion username')
        self.chat_header.setFixedHeight(50)
        self.chat_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.chat_header.setStyleSheet('border-bottom: 1px solid #333; font-weight: bold;')

        self.chat_list = QListWidget()
        self.chat_list.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        self.chat_list.setStyleSheet('border: none; background-color: #141414; outline: none;')
        self.chat_list.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)

        # Панель ввода
        self.input_area = QFrame()
        self.input_area.setFixedHeight(80)
        self.input_area.setStyleSheet('border-top: 1px solid #333;')
        self.input_layout = QHBoxLayout(self.input_area)

        self.msg_input = QLineEdit()
        self.msg_input.setPlaceholderText('Enter your message...')
        self.msg_input.setStyleSheet('border: 1px solid #333; border-radius: 10px; padding: 10px; background: #1b1b1b;')

        # ОБРАБОТКА ENTER
        self.msg_input.returnPressed.connect(self.display_message)

        self.send_btn = QPushButton('Send')
        self.send_btn.setFixedSize(110, 40)
        self.send_btn.setStyleSheet('background-color: #1b1b1b; border: 1px solid #333; border-radius: 8px;')
        self.send_btn.clicked.connect(self.display_message)

        self.input_layout.addWidget(self.msg_input)
        self.input_layout.addWidget(self.send_btn)

        self.right_layout.addWidget(self.chat_header)
        self.right_layout.addWidget(self.chat_list)
        self.right_layout.addWidget(self.input_area)

        # Сборка
        self.content_layout.addWidget(self.left_panel)
        self.content_layout.addWidget(self.right_panel)
        self.layout.addWidget(self.content_widget)

    def send_login_application(self, new_account: bool = False):
        login, password = self.login_field.text(), self.password_field.text()
        print(login, password)
        if len(login) > 32 or len(password) > 32 or len(login) == 0 or len(password) == 0:
            QMessageBox.critical(None, 'FAIL', 'Username and password must be between 1 and 32 characters.')
            return
        self.send_message(f'{login}:{password};{'register' if new_account else 'login'}', 128)
        data = self.get_message(128)
        if data == 'SUCCESS':
            # QMessageBox.information(None, 'SUCCESS', data)
            self.launch()
        else:
            QMessageBox.critical(None, 'FAIL', data[data.find(';'):])

    def launch(self):
        self.get_file('data.json')
        with open('data/data.json', encoding='utf-8') as f:
            self.messages = json.load(f)
        self.init_main_ui()

    def change_companion(self):
        self.chat_list.clear()
        for i in self.messages[self.contacts.currentItem().text()]:
            self.display_message(i[0], i[1])
        self.chat_header.setText(self.contacts.currentItem().text())

    def send_message(self, mess: str, buff: int) -> None:
        mess = f'{mess};'.encode('utf-8')
        self.sock.send(mess + bytearray(buff - len(mess)))

    def get_message(self, buff: int) -> str:
        mess = self.sock.recv(buff).decode('utf-8')
        mess = mess[:mess.rfind(';')]
        return mess

    def get_file(self, file_name: str = None) -> None:
        '''
        Getting a file from the server.
        :param file_name: file name with its extension <data.json>
        :return:
        '''
        f_name, f_size = self.get_message(512).split(';')
        f_size = int(f_size)
        if file_name: f_name = file_name
        with open(f'{getcwd()}\\data\\{f_name}', 'wb') as f:
            for i in range(f_size // 4096):
                chunk = self.sock.recv(4096)
                f.write(chunk)
            chunk = self.sock.recv(f_size - f_size // 4096 * 4096)
            f.write(chunk)

    def send_file(self, file_path):
        f_name = file_path[file_path.rfind('/'):]
        file_size = path.getsize(file_path)
        # file_name;file_size(bytes);\x00\x00\x00\x00...
        self.send_message(f'{f_name};{file_size}', 512)
        with open(file_path, 'rb') as f:
            chunk = f.read(4096)
            while chunk:
                self.sock.send(chunk)
                chunk = f.read(4096)

    def display_message(self, text, is_user=True):
        if is_user: self.msg_input.clear()
        item = QListWidgetItem(self.chat_list)
        bubble = MessageBubble(text, is_user)
        # Устанавливаем размер ячейки под размер виджета
        item.setSizeHint(bubble.sizeHint())
        self.chat_list.addItem(item)
        self.chat_list.setItemWidget(item, bubble)
        self.chat_list.scrollToBottom()

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
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
        color: #dad085;
        font-size: 14px;
        font-family: Consolas;
        border: 1px solid #5f5a60;
        border-radius: 5px;
    }
    QPushButton:hover {
        color: #f7f7f2;
        font-size: 14px;
        font-family: Consolas;
    }
    QPushButton:pressed {
        background-color: #141414;
        color: #f8f8f8;
        font-size: 14px;
        font-family: Consolas;
    }
    QFrame {
        background-color: #141414;
        color: #dad085;
        font-size: 14px;
        font-family: Consolas;
    }
    QMessageBox {
        background-color: #141414;
    }
    ''')
    window = MainWindow()
    window.show()
    sys.exit(app.exec())