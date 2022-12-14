# pylint: disable=redefined-outer-name, unused-argument

import os
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config as AlembicConfig
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_utils import create_database, drop_database

from app.admin_api.web.store import Store
from app.packages.config import Config, get_config
from app.packages.postgres.database import Database
from app.packages.postgres.metadata import BaseMetadata


@pytest.fixture(scope='session')
def temp_db_config() -> Config:
    settings: Config = get_config()
    temp_db_name = f'{settings.database.database}_{uuid4()}'
    settings.database.database = temp_db_name
    os.environ['DATABASE__NAME'] = temp_db_name
    return settings


@pytest.fixture(scope='session')
def temp_db_create(temp_db_config: Config) -> None:
    create_database(temp_db_config.database_dsn_sync)
    yield
    drop_database(temp_db_config.database_dsn_sync)


@pytest.fixture(scope='session')
def alembic_cfg(temp_db_config: Config) -> AlembicConfig:
    return AlembicConfig('alembic.ini')


@pytest.fixture(scope='session', autouse=True)
def db_migrated(temp_db_create: None, alembic_cfg: AlembicConfig) -> None:
    command.upgrade(alembic_cfg, 'head')


@pytest.fixture
async def db(store: Store) -> Database:
    yield store.db
    async with store.db.engine.begin() as session:
        for table in BaseMetadata.metadata.tables:
            await session.execute(text(f'TRUNCATE {table} CASCADE'))


@pytest.fixture
async def db_session(db: Database) -> AsyncSession:
    async with db.session_maker() as session:
        yield session
