from hashlib import sha256

import pytest
from aiohttp.test_utils import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin_api.admin.dtos import Admin
from app.admin_api.admin.models import AdminModel


@pytest.fixture
async def admin(client: TestClient, db_session: AsyncSession) -> Admin:
    new_admin = AdminModel(
        email=client.app['config'].admin.email,
        password=sha256(client.app['config'].admin.password.encode()).hexdigest(),
    )
    db_session.add(new_admin)
    await db_session.commit()

    return Admin.from_orm(new_admin)
