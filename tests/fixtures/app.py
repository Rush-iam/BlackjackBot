# pylint: disable=redefined-outer-name, unused-argument

import pytest
from aiohttp.test_utils import TestClient
from aiohttp.web_app import Application

from app.admin.dtos import Admin
from app.web.app import create_app
from app.web.config import Config
from app.web.store import Store


@pytest.fixture
def app() -> Application:
    app = create_app()
    app.on_startup.clear()
    app.on_shutdown.clear()

    app.on_startup.append(app['store'].db.connect)
    app.on_shutdown.append(app['store'].db.disconnect)

    return app


@pytest.fixture
async def client(aiohttp_client, app: Application) -> TestClient:
    return await aiohttp_client(app)


@pytest.fixture
async def auth_client(client: TestClient, admin: Admin) -> TestClient:
    await client.post(
        '/admin.login',
        json={
            'email': client.app['config'].admin.email,
            'password': client.app['config'].admin.password,
        },
    )
    return client


@pytest.fixture
def config(client: TestClient) -> Config:
    return client.app['config']


@pytest.fixture
def store(client: TestClient) -> Store:
    return client.app['store']
