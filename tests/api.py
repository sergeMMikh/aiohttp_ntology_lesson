import json

import requests
from typing import Literal
from tests.config import API_URL

session = requests.Session()


class ApiError(Exception):

    def __init__(self, status_code: int, message: dict or str):
        self.status_code = status_code
        self.message = message


def basic_request(method: Literal['get', 'post', 'patch', 'delete'], path: str, **kwargs) -> dict:
    method = getattr(session, method)

    path = f'{API_URL}/{path}'

    response = method(path, **kwargs)

    if response.status_code >= 400:
        try:
            message = response.json()
        except json.JSONDecodeError:
            message = response.text
        raise ApiError(response.status_code, message)

    return response.json()


def create_user(name: str, password: str):
    return basic_request('post', 'users/', json={'name': name, 'password': password})


def get_user(user_id):
    return basic_request('get', f'users/{user_id}')


def patch_user(user_id: int, patch: dict):
    return basic_request('patch', f'users/{user_id}', json=patch)


def delete_user(user_id):
    return basic_request('delete', f'users/{user_id}')


def login(name: str, password: str):
    return basic_request('post', 'login', json={'name': name, 'password': password})
