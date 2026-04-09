import threading
import socket
import json
from datetime import datetime
import os


class Server:
    def __init__(self):
        self.online_users = {i[:-5]: [] for i in os.listdir(f'{os.getcwd()}\\messages')}
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('0.0.0.0', 9100))
        sock.listen(5)

        with open('users.json', 'r', encoding='utf-8') as f:
            self.users = json.load(f)

        try:
            while True:
                conn, addr = sock.accept()
                print(conn, addr)
                thread_registration = threading.Thread(target=self.handle_client, args=(conn,))
                thread_registration.start()
        except Exception as e:
            print(e)
            sock.close()

    @staticmethod
    def send_message(conn, mess: str, buff: int) -> None:
        mess = f'{mess};'.encode('utf-8')
        conn.send(mess + bytearray(buff - len(mess)))

    @staticmethod
    def get_message(conn, buff: int) -> str:
        mess = conn.recv(buff).decode('utf-8')
        mess = mess[:mess.rfind(';')]
        return mess

    def send_file(self, conn, path: str) -> None:
        print(f'sending file: {path}')
        f_name = path[path.rfind('\\'):]
        file_size = os.path.getsize(path)
        # file_name;file_size(bytes);\x00\x00\x00\x00...
        self.send_message(conn, f'{f_name};{file_size}', 512)
        with open(path, 'rb') as f:
            chunk = f.read(4096)
            while chunk:
                conn.send(chunk)
                chunk = f.read(4096)
        print('file send')

    @staticmethod
    def get_file(conn):
        f_name, f_size, buff = conn.recv(512).decode('utf-8').split(';')
        f_size = int(f_size)
        path = f'{os.getcwd()}\\server_imgs'
        with open(f'{path}\\{len(os.listdir(path))}{f_name[f_name.rfind("."):]}', 'wb') as f:
            for i in range(f_size // 4096):
                chunk = conn.recv(4096)
                f.write(chunk)
            chunk = conn.recv(f_size - f_size // 4096 * 4096)
            f.write(chunk)

    def handle_client(self, conn) -> None:
        while True:
            data = self.get_message(conn, 128)
            if data[data.rfind(';') + 1:] == 'login':
                login = data[:data.find(':')]
                password = data[data.find(':') + 1:data.find(';')]
                if login in list(self.users.keys()) and self.users[login] == password:
                    self.send_message(conn, 'SUCCESS', 128)
                    break
                else:
                    self.send_message(conn, 'FAIL;Wrong username or password', 128)
            elif data[data.rfind(';') + 1:] == 'register':
                login = data[:data.find(':')]
                password = data[data.find(':') + 1:data.find(';')]
                if 'Companion username' == login:
                    self.send_message(conn, 'FAIL;This username is already taken', 128)
                    continue
                if ';' in login:
                    self.send_message(conn, 'FAIL;Username cannot contain the character ;', 128)
                    continue
                if not login in list(self.users.keys()):
                    self.send_message(conn, 'SUCCESS', 128)
                    self.users[login] = password
                    self.online_users[login] = conn
                    with open('users.json', 'w', encoding='utf-8') as f:
                        json.dump(self.users, f)
                    with open(f'messages\\{login}.json', 'w', encoding='utf-8') as f:
                        json.dump({}, f)
                    break
                else:
                    self.send_message(conn, 'FAIL;This username is already taken', 128)
        self.send_file(conn, f'{os.getcwd()}\\messages\\{login}.json')

        while True:
            data = self.get_message(conn, 512)
            command, args = data[:data.find(';')], data[data.find(';') + 1:]
            match command:
                case 'MESSAGE':
                    from_user, message, to_user = (args[:args.find(';')],
                                                   args[args.find(';') + 1:args.rfind(';')],
                                                   args[args.rfind(';') + 1:])
                    for i in self.online_users[to_user]:
                        self.send_message(conn, to_user, 512)

                    with open(f'messages/{from_user}.json', encoding='utf-8') as f:
                        data = json.load(f)
                    if to_user not in data: data[to_user] = []
                    data[to_user].append([message, True, datetime.now().strftime('%Y.%m.%dT%H:%M:%S')])
                    with open(f'messages/{from_user}.json', 'w', encoding='utf-8') as f:
                        json.dump(data, f)

                    with open(f'messages/{to_user}.json', encoding='utf-8') as f:
                        data = json.load(f)
                    if from_user not in data: data[from_user] = []
                    data[from_user].append([message, False, datetime.now().strftime('%Y.%m.%dT%H:%M:%S')])
                    with open(f'messages/{to_user}.json', 'w', encoding='utf-8') as f:
                        json.dump(data, f)

                case 'EXIT':
                    conn.close()
                    # add deleting from self.online_users
                    break
                case _:
                    self.send_message(conn, 'FAIL;Unknown command', 512)

if __name__ == '__main__':
    server = Server()