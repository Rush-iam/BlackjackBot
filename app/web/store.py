from aiohttp.web_app import Application

from app.store.admin.accessor import AdminAccessor
from app.store.bot.accessor import BotAccessor
from app.store.database.database import Database
from app.store.telegram.accessor import TelegramAccessor


class Store:
    def __init__(self, app: Application):
        self.db = Database(app)
        self.admins = AdminAccessor(self.db)
        app.on_startup.append(self.admins.create_default_admin)
        # TODO: move admin creation to migration?

        self.telegram = TelegramAccessor(app)
        self.bot = BotAccessor(self.telegram)


def setup_store(app: Application) -> None:
    app['store'] = Store(app)
