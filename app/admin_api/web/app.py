from typing import Optional

import aiohttp_session
from aiohttp.web import Application
from aiohttp_apispec import setup_aiohttp_apispec
from aiohttp_session.cookie_storage import EncryptedCookieStorage

from app.packages.config import get_config
from app.packages.logger import setup_logging

from .middlewares import setup_middlewares
from .routes import setup_routes
from .store import setup_store


def create_app(config_path: Optional[str] = None) -> Application:
    app = Application()
    config = get_config(config_path)
    app['config'] = config

    aiohttp_session.setup(
        app=app,
        storage=EncryptedCookieStorage(config.app.cookie_secret_key.encode()),
    )
    setup_logging()
    setup_routes(app)
    setup_middlewares(app)
    setup_store(app)
    setup_aiohttp_apispec(
        app=app,
        title='Blackjack TG Bot',
        swagger_path='/api/docs',
        url='/api/docs/swagger.json',
    )
    return app
