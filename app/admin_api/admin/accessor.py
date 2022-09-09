from hashlib import sha256

from aiohttp.web_app import Application
from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.exc import IntegrityError

from app.admin_api.admin.dtos import Admin
from app.admin_api.admin.models import AdminModel
from app.packages.config import Config
from app.packages.logger import logger
from app.packages.postgres.accessor import DatabaseAccessor


class AdminAccessor(DatabaseAccessor):
    async def create_default_admin(self, app: Application) -> None:
        try:
            config: Config = app['config']
            await self.create_admin(**config.admin.dict())
            logger.info('Default admin created: %s', config.admin.email)
        except IntegrityError:
            pass

    async def create_admin(self, email: str, password: str) -> Admin:
        async with self.session() as db:
            admin = AdminModel(
                email=email,
                password=sha256(password.encode()).hexdigest(),
            )
            db.add(admin)
        return Admin.from_orm(admin)

    async def get_by_email(self, email: str) -> Admin | None:
        async with self.session() as db:
            result: Result = await db.execute(
                select(AdminModel).where(AdminModel.email == email)
            )
            admin = result.scalars().first()
        return Admin.from_orm(admin) if admin else None
