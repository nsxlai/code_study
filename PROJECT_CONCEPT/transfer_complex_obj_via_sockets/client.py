"""
source: https://www.youtube.com/watch?v=xtdS7flpaoA&list=WL&index=412
"""
import socket
import pickle
from datetime import datetime
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split


CONN_IP_ADDR = '127.0.0.1'
PORT = 9999


def create_sample_model_obj():
    data = load_iris()
    X, y = data.data, data.target
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5)
    model = RandomForestClassifier()
    model.fit(X_train, y_train)
    return model


if __name__ == '__main__':

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((CONN_IP_ADDR, PORT))

    sample_obj = create_sample_model_obj()
    serialized = pickle.dumps(sample_obj)
    print(f'Created the RandomForest model on {datetime.now()}')

    try:
        client.sendall(serialized)
    finally:
        client.close()
