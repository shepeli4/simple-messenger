import threading
import socket
import json
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
    def get_file(conn) -> str:
        def to_base62(n):
            if n == 0:
                return '0'
            base62_chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
            result = []
            while n > 0:
                n, rem = divmod(n, 62)
                result.append(base62_chars[rem])
            return ''.join(reversed(result))

        f_name, f_size, buff = conn.recv(512).decode('utf-8').split(';')
        f_size = int(f_size)
        path = f'{os.getcwd()}\\files'
        with open(f'{path}\\{to_base62(len(os.listdir(path)))}{f_name[f_name.rfind("."):]}', 'wb') as f:
            for i in range(f_size // 4096):
                chunk = conn.recv(4096)
                f.write(chunk)
            chunk = conn.recv(f_size - f_size // 4096 * 4096)
            f.write(chunk)
        return to_base62(len(os.listdir(path)))

    def handle_client(self, conn) -> None:
        while True:
            data = self.get_message(conn, 128)
            if data[data.rfind(';') + 1:] == 'login':
                login = data[:data.find(':')]
                password = data[data.find(':') + 1:data.find(';')]
                if login in list(self.users.keys()) and self.users[login] == password:
                    self.online_users[login].append(conn)
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
                    self.online_users[login] = [conn]
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
                        self.send_message(i, data, 512)
                    for i in self.online_users[from_user]:
                        if i != conn:
                            self.send_message(i, data, 512)

                    with open(f'messages/{from_user}.json', encoding='utf-8') as f:
                        data = json.load(f)
                    if to_user not in data: data[to_user] = []
                    data[to_user].append([message, True, False])
                    with open(f'messages/{from_user}.json', 'w', encoding='utf-8') as f:
                        json.dump(data, f)

                    with open(f'messages/{to_user}.json', encoding='utf-8') as f:
                        data = json.load(f)
                    if from_user not in data: data[from_user] = []
                    data[from_user].append([message, False, False])
                    with open(f'messages/{to_user}.json', 'w', encoding='utf-8') as f:
                        json.dump(data, f)

                case 'FILE':
                    from_user, to_user = args.split(';')
                    file_name = self.get_file(conn)

                    for i in self.online_users[to_user]:
                        self.send_message(i, f'FILE;{from_user};{file_name};{to_user}', 512)
                    for i in self.online_users[from_user]:
                        if i != conn:
                            self.send_message(i, f'FILE;{from_user};{file_name};{to_user}', 512)

                    with open(f'messages/{from_user}.json', encoding='utf-8') as f:
                        data = json.load(f)
                    if to_user not in data: data[to_user] = []
                    data[to_user].append([file_name, True, True])
                    with open(f'messages/{from_user}.json', 'w', encoding='utf-8') as f:
                        json.dump(data, f)

                    with open(f'messages/{to_user}.json', encoding='utf-8') as f:
                        data = json.load(f)
                    if from_user not in data: data[from_user] = []
                    data[from_user].append([file_name, False, True])
                    with open(f'messages/{to_user}.json', 'w', encoding='utf-8') as f:
                        json.dump(data, f)

                case 'EXIT':
                    print(self.online_users)
                    self.send_message(conn, 'NONE;', 512)
                    self.online_users[args].remove(conn)
                    conn.close()
                    print(self.online_users)
                    break

                case 'FIND_USER':
                    self.send_message(conn, 'NONE', 512)
                    if args in self.users:
                        self.send_message(conn, 'SUCCESS', 512)
                    else:
                        self.send_message(conn, 'FAIL;This user does not exist', 512)

                case _:
                    self.send_message(conn, 'FAIL;Unknown command', 512)

if __name__ == '__main__':
    server = Server()