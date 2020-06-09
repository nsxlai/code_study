import mock

class MySingleton(object):
    _instance = None

    def __new__(self):
        if not self._instance:
            self._instance = super(MySingleton, self).__new__(self)
            self.y = 10
        return self._instance


class MyConn:
    _shared_conn = None

    def __new__(cls, conn):
        if cls._shared_conn is None:
            cls._shared_conn = conn
        return cls._shared_conn


if __name__ == '__main__':
    conn = mock.MagicMock()
    a = MyConn(conn)
    print(a)
    b = MyConn(conn)
    print(b)
    c = conn
    print(c)