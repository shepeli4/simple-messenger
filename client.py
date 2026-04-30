import json
import os
import threading
import socket
import sys

from Demos.win32ts_logoff_disconnected import username
from PyQt6.QtWidgets import (QWidget, QApplication, QPushButton, QLabel, QLineEdit, QVBoxLayout, QMessageBox, QListWidgetItem,
                             QHBoxLayout, QListWidget, QFrame, QFileDialog)
from PyQt6.QtCore import Qt, pyqtSignal
from os import getcwd, path, listdir, remove, startfile


class MessageBubble(QWidget):
    """Виджет отдельного сообщения (бабла)"""

    def __init__(self, text, is_user=True, is_file=False):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        if is_file:
            def open_file(file_name):
                print(f'{os.getcwd()}\\data\\{file_name}')
                if file_name in listdir(f'{os.getcwd()}\\data\\'):
                    os.startfile(f'{os.getcwd()}\\data\\{file_name}')
                else:
                    print('file_not_found') # пырисылать файл

            self.btn = QPushButton(text)
            self.btn.setMaximumWidth(400)
            self.btn.clicked.connect(lambda: open_file(text))

            if is_user:
                layout.addStretch()
                layout.addWidget(self.btn)
                self.btn.setStyleSheet(f"color: #7587a6; background-color: #1b1b1b; border: 1px solid #333; border-radius: 10px; padding: 10px; text-decoration: underline;")
            else:
                layout.addWidget(self.btn)
                layout.addStretch()
                self.btn.setStyleSheet(f"color: #7587a6; background-color: #141414; border: 1px solid #dad085; border-radius: 10px; padding: 10px; text-decoration: underline;")
        else:
            self.label = QLabel(text)
            self.label.setWordWrap(True)
            self.label.setMaximumWidth(400)  # Ограничиваем ширину сообщения

            # Стили баблов: пользователь справа, собеседник слева
            if is_user:
                layout.addStretch()
                layout.addWidget(self.label)
                self.label.setStyleSheet(f"background-color: #1b1b1b; border: 1px solid #333; border-radius: 10px; padding: 10px;")
            else:
                layout.addWidget(self.label)
                layout.addStretch()
                self.label.setStyleSheet(f"background-color: #141414; border: 1px solid #dad085; border-radius: 10px; padding: 10px;")


class MainWindow(QWidget):
    # SIGNALS FOR THREADING
    display_message_signal = pyqtSignal(str, bool, bool)

    def __init__(self):
        super().__init__()
        self.username = ''
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(('192.168.1.188', 9100)) # CHANGE IP
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

        register_button = QPushButton('Sign up')
        register_button.setFixedWidth(170)
        register_button.clicked.connect(lambda: self.send_login_application(True))
        self.layout.addWidget(register_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.layout.addStretch()

        self.setLayout(self.layout)
        self.setWindowTitle('🍗')
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

        self.mini_panel = QFrame()
        self.mini_panel.setFixedHeight(80)
        self.mini_panel.setStyleSheet('border-right: none; border-bottom: 1px solid #333;')
        self.mini_layout = QHBoxLayout(self.mini_panel)

        self.find_user_input = QLineEdit()
        self.find_user_input.setPlaceholderText('Enter username')
        self.find_user_input.setStyleSheet('border: 1px solid #333; border-radius: 10px; padding: 10px; background: #1b1b1b;')
        self.mini_layout.addWidget(self.find_user_input)

        self.find_btn = QPushButton('Find')
        self.find_btn.setFixedSize(60, 40)
        self.find_btn.setStyleSheet('background-color: #1b1b1b; border: 1px solid #333; border-radius: 8px;')
        self.find_btn.clicked.connect(self.find_user)
        self.mini_layout.addWidget(self.find_btn)

        self.contacts = QListWidget()
        self.contacts.addItems(list(self.messages.keys()))
        self.contacts.setStyleSheet('''
                    QListWidget { border: none; outline: none; }
                    QListWidget::item { height: 60px; padding-left: 15px; border-bottom: 1px solid #222; }
                    QListWidget::item:selected { background-color: #1b1b1b; color: #dad085; }
                ''')
        self.contacts.itemSelectionChanged.connect(self.change_companion)

        self.left_layout.addWidget(self.mini_panel)
        # self.left_layout.addWidget(self.settings_btn)
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

        # ДОДЕЛАТЬ ФАЙЛЫ
        self.file_btn = QPushButton('File')
        self.file_btn.setFixedSize(50, 40)
        self.file_btn.setStyleSheet('background-color: #1b1b1b; border: 1px solid #333; border-radius: 8px;')
        self.file_btn.clicked.connect(lambda: self.send_file_to_companion(self.chat_header.text()))

        self.msg_input = QLineEdit()
        self.msg_input.setPlaceholderText('Enter your message...')
        self.msg_input.setStyleSheet('border: 1px solid #333; border-radius: 10px; padding: 10px; background: #1b1b1b;')

        # ОБРАБОТКА ENTER
        self.msg_input.returnPressed.connect(lambda: self.send_message(self.msg_input.text(), self.chat_header.text()))

        self.send_btn = QPushButton('Send')
        self.send_btn.setFixedSize(110, 40)
        self.send_btn.setStyleSheet('background-color: #1b1b1b; border: 1px solid #333; border-radius: 8px;')
        self.send_btn.clicked.connect(lambda: self.send_message(self.msg_input.text(), self.chat_header.text()))

        self.input_layout.addWidget(self.file_btn)
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
        if len(login) > 32 or len(password) > 32 or len(login) == 0 or len(password) == 0:
            QMessageBox.critical(None, 'FAIL', 'Username and password must be between 1 and 32 characters.')
            return
        self.send_inform_to_server(f'{login}:{password};{"register" if new_account else "login"}', 128)
        data = self.get_inform_form_server(128)
        if data == 'SUCCESS':
            # QMessageBox.information(None, 'SUCCESS', data)
            self.username = login
            self.launch()
        else:
            QMessageBox.critical(None, 'FAIL', data[data.find(';'):])

    def launch(self):
        self.setWindowTitle(self.username)
        self.get_file()
        with open(f'data/{self.username}.json', encoding='utf-8') as f:
            self.messages = json.load(f)
        self.display_message_signal.connect(self.display_message)
        self.getting_cycle_bool = True
        self.BREAK_ALL = False
        self.getting_cycle_thread = threading.Thread(target=self.getting_cycle, args=())
        self.getting_cycle_thread.start()
        self.init_main_ui()

    def change_companion(self):
        self.chat_list.clear()
        if self.contacts.currentItem().text() in self.messages:
            for i in self.messages[self.contacts.currentItem().text()]:
                self.display_message(i[0], i[1], i[2])
        self.chat_header.setText(self.contacts.currentItem().text())

    def send_inform_to_server(self, mess: str, buff: int) -> None:
        mess = f'{mess};'.encode('utf-8')
        self.sock.send(mess + bytearray(buff - len(mess)))

    def get_inform_form_server(self, buff: int) -> str:
        mess = self.sock.recv(buff).decode('utf-8')
        mess = mess[:mess.rfind(';')]
        return mess

    def get_file(self, file_name: str = None) -> None:
        '''
        Getting a file from the server.
        :param file_name: file name with its extension <data.json>
        :return:
        '''
        f_name, f_size = self.get_inform_form_server(512).split(';')
        f_size = int(f_size)
        if file_name: f_name = file_name
        with open(f'{getcwd()}\\data\\{f_name}', 'wb') as f:
            for i in range(f_size // 1_048_576):
                # print(i, f_size, f_size // 4096)
                chunk = self.sock.recv(1_048_576)
                f.write(chunk)
            chunk = self.sock.recv(f_size - f_size // 1_048_576 * 1_048_576)
            f.write(chunk)

    def send_file(self, file_path):
        f_name = file_path[file_path.rfind('/'):]
        file_size = path.getsize(file_path)
        # file_name;file_size(bytes);\x00\x00\x00\x00...
        self.send_inform_to_server(f'{f_name};{file_size}', 512)
        with open(file_path, 'rb') as f:
            chunk = f.read(1_048_576)
            while chunk:
                self.sock.send(chunk)
                chunk = f.read(1_048_576)

    def create_bubble(self, text, is_user=True, is_file=False):
        bubble = QWidget()
        layout = QHBoxLayout(bubble)
        layout.setContentsMargins(10, 5, 10, 5)

        if is_file:
            def open_file(file_name):
                print(f'{os.getcwd()}\\data\\{file_name}')
                if file_name in listdir(f'{os.getcwd()}\\data\\'):
                    os.startfile(f'{os.getcwd()}\\data\\{file_name}')
                else:
                    self.getting_cycle_bool = False
                    self.send_inform_to_server(f'GET_FILE;{file_name}', 512)
                    data = self.get_inform_form_server(128)
                    if data == 'NONE':
                        data = self.get_inform_form_server(128)

                    if data == 'SUCCESS':
                        self.get_file()
                        os.startfile(f'{os.getcwd()}\\data\\{file_name}')
                    else:
                        QMessageBox.critical(None, 'FAIL', data[data.find(';') + 1:])
                    self.getting_cycle_bool = True

            btn = QPushButton(text)
            btn.setMaximumWidth(400)
            btn.clicked.connect(lambda: open_file(text))

            if is_user:
                layout.addStretch()
                layout.addWidget(btn)
                btn.setStyleSheet(
                    f"color: #7587a6; background-color: #1b1b1b; border: 1px solid #333; border-radius: 10px; padding: 10px; text-decoration: underline;")
            else:
                layout.addWidget(btn)
                layout.addStretch()
                btn.setStyleSheet(
                    f"color: #7587a6; background-color: #141414; border: 1px solid #dad085; border-radius: 10px; padding: 10px; text-decoration: underline;")
        else:
            label = QLabel(text)
            label.setWordWrap(True)
            label.setMaximumWidth(400)  # Ограничиваем ширину сообщения

            # Стили баблов: пользователь справа, собеседник слева
            if is_user:
                layout.addStretch()
                layout.addWidget(label)
                label.setStyleSheet(
                    f"background-color: #1b1b1b; border: 1px solid #333; border-radius: 10px; padding: 10px;")
            else:
                layout.addWidget(label)
                layout.addStretch()
                label.setStyleSheet(
                    f"background-color: #141414; border: 1px solid #dad085; border-radius: 10px; padding: 10px;")
        return bubble

    def display_message(self, text, is_user=True, is_file=False):
        if is_user: self.msg_input.clear()
        item = QListWidgetItem(self.chat_list)
        bubble = self.create_bubble(text, is_user, is_file)
        # Устанавливаем размер ячейки под размер виджета
        item.setSizeHint(bubble.sizeHint())
        self.chat_list.addItem(item)
        self.chat_list.setItemWidget(item, bubble)
        self.chat_list.scrollToBottom()

    '''def display_message(self, text, is_user=True, is_file=False):
        if is_user: self.msg_input.clear()
        item = QListWidgetItem(self.chat_list)
        bubble = MessageBubble(text, is_user, is_file)
        # Устанавливаем размер ячейки под размер виджета
        item.setSizeHint(bubble.sizeHint())
        self.chat_list.addItem(item)
        self.chat_list.setItemWidget(item, bubble)
        self.chat_list.scrollToBottom()'''

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

    def send_message(self, message: str, to_user: str):
        if to_user == 'Companion username':
            return
        if len(message.encode('utf-8')) > 256:
            QMessageBox.critical(None, 'FAIL', 'The message length cannot be more 256 bytes')
            return
        if to_user not in self.messages:
            self.messages[to_user] = []
        self.messages[to_user].append([message, True, False])
        self.send_inform_to_server(f'MESSAGE;{self.username};{message};{to_user}', 512)
        self.display_message(message)

    def send_file_to_companion(self, companion_name: str):
        if companion_name == 'Companion username':
            return
        filepath = QFileDialog.getOpenFileName()[0]
        self.send_inform_to_server(f'FILE;{self.username};{companion_name}', 512)
        self.send_file(filepath)

    def find_user(self):
        if not self.find_user_input.text():
            QMessageBox.critical(None, 'FAIL', 'User "" does not exist')
            return
        if self.find_user_input.text() in [self.contacts.item(i).text() for i in range(self.contacts.count())]:
            for i in range(self.contacts.count()):
                print(self.contacts.item(i).text())
                if self.contacts.item(i).text() == self.find_user_input.text():
                    self.contacts.setCurrentItem(self.contacts.item(i))
            self.change_companion()
            self.find_user_input.setText('')
            return
        self.getting_cycle_bool = False
        self.send_inform_to_server(f'FIND_USER;{self.find_user_input.text()}', 512)
        data = self.get_inform_form_server(512)
        if data == 'NONE':
            data = self.get_inform_form_server(512)
        if data == 'SUCCESS':
            self.contacts.addItem(self.find_user_input.text())
            self.contacts.scrollToBottom()
            for i in range(self.contacts.count()):
                if self.contacts.item(i).text() == self.find_user_input.text():
                    self.contacts.setCurrentItem(self.contacts.item(i))
            self.change_companion()
            self.find_user_input.setText('')
        else:
            QMessageBox.critical(None, 'FAIL', data[data.find(';') + 1:])
        self.getting_cycle_bool = True


    def closeEvent(self, e):
        if self.username:
            self.send_inform_to_server(f'EXIT;{self.username}', 512)
            self.getting_cycle_bool = False
            self.BREAK_ALL = True
            folder_path = getcwd() + '\\data'
            '''
            for item in listdir(folder_path):
                item_path = path.join(folder_path, item)
                if not path.isdir(item_path):
                    remove(item_path)
            '''
        e.accept()

    def getting_cycle(self):
        while True:
            if self.BREAK_ALL:
                break
            while self.getting_cycle_bool:
                data = self.get_inform_form_server(512)
                print(data)
                command, args = data[:data.find(';')], data[data.find(';') + 1:]
                match command:
                    case 'MESSAGE':
                        from_user, message, to_user = (args[:args.find(';')],
                                                       args[args.find(';') + 1:args.rfind(';')],
                                                       args[args.rfind(';') + 1:])
                        if self.username != from_user:
                            if from_user not in self.messages and from_user != self.username:
                                self.messages[from_user] = []
                                self.contacts.addItem(from_user)
                            self.messages[from_user].append([message, False, False])
                            if self.chat_header.text() == from_user:
                                self.display_message_signal.emit(message, False, False)
                        else:
                            self.messages[to_user].append([message, True, False])
                            if self.chat_header.text() == to_user:
                                self.display_message_signal.emit(message, True, False)

                    case 'FILE':
                        from_user, message, to_user = (args[:args.find(';')],
                                                       args[args.find(';') + 1:args.rfind(';')],
                                                       args[args.rfind(';') + 1:])
                        if self.username != from_user:
                            if from_user not in self.messages and from_user != self.username:
                                self.messages[from_user] = []
                                self.contacts.addItem(from_user)
                            self.messages[from_user].append([message, False, False])
                            if self.chat_header.text() == from_user:
                                self.display_message_signal.emit(message, False, True)
                        else:
                            if to_user not in self.messages:
                                self.messages[to_user] = []
                            self.messages[to_user].append([message, True, False])
                            if self.chat_header.text() == to_user:
                                self.display_message_signal.emit(message, True, True)

                    case 'NONE':
                        pass

                    case 'FAIL':
                        QMessageBox.critical(None, 'FAIL', args)


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