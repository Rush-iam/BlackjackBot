import pytest
from aiohttp.test_utils import TestClient
from aiohttp.web_exceptions import HTTPMethodNotAllowed, HTTPOk, HTTPUnprocessableEntity

from app.admin.dtos import Admin
from app.web.config import Config


class TestAdminLoginView:
    ENDPOINT = '/admin.login'

    async def test_success(self, client: TestClient, config: Config, admin: Admin):
        response = await client.post(self.ENDPOINT, json=config.admin.dict())
        assert response.status == HTTPOk.status_code, await response.text()
        assert await response.json() == {
            'id': 1,
            'email': admin.email,
        }

    async def test_bad_method(self, client: TestClient, config: Config, admin: Admin):
        response = await client.get(self.ENDPOINT, json=config.admin.dict())
        assert response.status == HTTPMethodNotAllowed.status_code

    @pytest.mark.parametrize(
        'bad_credentials',
        [
            {'password': 'qwerty'},
            {'password': 'qwerty', 'email': 'qwerty'},
        ],
    )
    async def test_bad_credentials(self, client: TestClient, bad_credentials: dict):
        response = await client.post(self.ENDPOINT, json=bad_credentials)
        assert response.status == HTTPUnprocessableEntity.status_code
