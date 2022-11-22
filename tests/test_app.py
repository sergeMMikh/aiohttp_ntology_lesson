import requests
import pytest

from tests.config import API_URL
from tests import api

PASSWORD = '1234'


def test_root():
    response = requests.get(f'{API_URL}')
    assert response.status_code == 404


def test_create_user():
    new_user = api.create_user(name='some_new_user', password=PASSWORD)

    assert 'id' in new_user


def test_get_user(root_user):
    user = api.get_user(root_user['id'])
    assert user['name'] == root_user['name']


def test_user_non_existed():
    with pytest.raises(api.ApiError) as err_info:
        api.get_user(999999)

    assert err_info.value.status_code == 404
    assert err_info.value.message == {'status': 'error',
                                      'message': 'User not found'}

def test_patch_user(new_user):
    api.patch_user(new_user['id'], {'name': 'patched_name'})
    user = api.get_user(new_user['id'])
    assert new_user['name'] == 'patched_name'
