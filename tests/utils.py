from sqlalchemy import inspect
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine

from app.packages.postgres.database import Database


def use_inspector(connection: Connection) -> list[str]:
    return inspect(connection).get_table_names()


async def get_db_table_names(db: Database) -> list[str]:
    engine: AsyncEngine = db.engine
    async with engine.begin() as conn:
        table_names = await conn.run_sync(use_inspector)
    return table_names
