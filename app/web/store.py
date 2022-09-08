from aiohttp.web_app import Application

from app.store.admin.accessor import AdminAccessor
from app.store.database.database import Database


class Store:
    def __init__(self, app: Application):
        self.db = Database(app)
        self.admins = AdminAccessor(self.db)
        app.on_startup.append(self.admins.create_default_admin)
        # TODO: move admin creation to migration?


def setup_store(app: Application) -> None:
    app['store'] = Store(app)
