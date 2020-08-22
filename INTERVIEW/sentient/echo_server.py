import socket

HOST = 'localhost'  # Standard loopback interface address (localhost)
PORT = 5050         # Port to listen on (non-privileged ports are > 1023)


def server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                conn.sendall(data)


if __name__ == '__main__':
    server()
