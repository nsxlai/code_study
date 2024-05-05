"""
source: https://medium.com/@mr.stucknet/streamline-your-python-workflow-with-cached-property-9518b50940c8
"""
from functools import cached_property
from time import sleep


class Client:
    def __init__(self):
        print("Setting up the client...")

    def query(self, **kwargs):
        print(f"Performing a query: {kwargs}")


class Manager:
    @property
    def client(self):
        return Client()

    def perform_query(self, **kwargs):
        return self.client.query(**kwargs)  # Calling client every time and will see "Performing a query" print out


class ManualCacheManager:
    """
    Create a singleton instance and use it as caching pattern
    """
    @property
    def client(self):
        if not hasattr(self, '_client'):
            self._client = Client()
        return self._client

    def client_delete(self):
        self._client = None

    def perform_query(self, **kwargs):
        return self.client.query(**kwargs)


class CachedPropertyManager:

    @cached_property
    def client(self):
        return Client()

    def client_delete(self):
        self._client = None

    def perform_query(self, **kwargs):
        return self.client.query(**kwargs)


if __name__ == '__main__':
    print(' Using Property '.center(60, '='))
    m1 = Manager()
    m1.perform_query(object_id=42)
    m1.perform_query(name_ilike='%Python%')

    print(' Manual Caching '.center(60, '='))
    m2 = ManualCacheManager()
    m2.perform_query(object_id=52)
    m2.perform_query(name_ilike='%Python%')
    m2.client_delete()
    try:
        m2.perform_query(age=18)
    except AttributeError as e:
        print(e, '. The client method needs to be reinstantiated...')

    print(' Using caching_property '.center(60, '='))
    m3 = CachedPropertyManager()
    m3.perform_query(object_id=42)
    m3.perform_query(name_ilike='%Python%')
    print(f'{m3.client = }')
    del m3.client
    print(f'{m3.client = }')
    sleep(3)
    m3.perform_query(age=18)
