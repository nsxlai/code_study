"""
source: https://www.youtube.com/watch?v=xtdS7flpaoA&list=WL&index=412
"""
import socket
import pickle
from datetime import datetime

from sklearn.datasets import load_iris


CONN_IP_ADDR = '127.0.0.1'
PORT = 9999

data = load_iris()
X, y = data.data, data.target


if __name__ == '__main__':

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((CONN_IP_ADDR, PORT))  # Always use the private IP address
    server.listen(1)  # allowing 1 connection

    while True:
        print('Waiting for connection...')
        client, addr = server.accept()

        try:
            print('Connected')
            data = b''

            while True:
                chunk = client.recv(4096)  # chunk size is 4096 bytes
                if not chunk:
                    break
                data += chunk

            received_obj = pickle.loads(data)  # unpicked the serialized data
            print(f'Received: {received_obj}, Current time is {datetime.now()}')
            print(f'Accuracy: {received_obj.score(X, y)}')
        finally:
            client.close()
