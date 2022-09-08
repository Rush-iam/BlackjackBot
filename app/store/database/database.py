import sys
from typing import Any

from aiohttp.web_app import Application
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.web.base.base_accessor import BaseAccessor
from app.web.logger import logger


class AsyncSessionType:
    async def __aenter__(self) -> AsyncSession:
        ...

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        ...


class Database(BaseAccessor):
    def __init__(self, app: Application):
        super().__init__(app)
        self.dsn: str = app['config'].database_dsn
        self.engine: AsyncEngine = create_async_engine(
            url=self.dsn,
            future=True,  # remove after upgrading to SQLAlchemy 2.0
        )
        self.session_maker: sessionmaker = sessionmaker(  # type: ignore
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            future=True,  # remove after upgrading to SQLAlchemy 2.0
        )

    async def connect(self, _: Application) -> None:
        try:
            async with self.engine.connect():
                ...
        except ConnectionRefusedError as exc:
            logger.error(
                'Unable to connect to Database (%s): %s', self.dsn, exc.strerror
            )
            sys.exit(1)
        logger.info('Database connected')

    async def disconnect(self, _: Application) -> None:
        if self.engine:
            await self.engine.dispose()

    def session(self) -> AsyncSessionType:
        """
        Autocommit ORM session
        """
        return self.session_maker.begin()
