from aiohttp.web_app import Application

from app.admin_api.admin.accessor import AdminAccessor
from app.admin_api.blackjack.accessor import BlackjackAccessor
from app.packages.postgres.database import Database


class Store:
    def __init__(self, app: Application):
        self.db = Database(app['config'].database_dsn)
        app.on_startup.append(self.db.connect)
        app.on_cleanup.append(self.db.disconnect)

        self.admins = AdminAccessor(self.db)
        app.on_startup.append(self.admins.create_default_admin)
        # TODO: move admin creation to migration?
        self.blackjack = BlackjackAccessor(self.db)


def setup_store(app: Application) -> None:
    app['store'] = Store(app)
