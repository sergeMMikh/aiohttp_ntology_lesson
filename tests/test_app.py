import requests

from tests.config import API_URL


def test_root():
    response = requests.get(f'{API_URL}')
    assert response.status_code == 404
