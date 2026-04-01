import threading
import socket
import json

class Server:
    def __init__(self):
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
                    self.send_message(conn, 'FAIL;Wrong name or password', 128)
            else:
                login = data[:data.find(':')]
                password = data[data.find(':') + 1:data.find(';')]
                if not login in list(self.users.keys()):
                    self.send_message(conn, 'SUCCESS', 128)
                    self.users[login] = password
                    with open('users.json', 'w', encoding='utf-8') as f:
                        json.dump(self.users, f)
                    break
                else:
                    self.send_message(conn, 'FAIL;This user is already taken', 128)

if __name__ == '__main__':
    server = Server()
