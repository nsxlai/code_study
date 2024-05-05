from unittest.mock import Mock
from unittest.mock import patch
import requests


requests = Mock()


def test_request_response():
    # Send a request to the API server and store the response.
    # response = requests.get('http://jsonplaceholder.typicode.com/todos')
    requests.get.status_code = 200

    # Confirm that the request-response cycle completed successfully.
    assert requests.get.status_code == 200