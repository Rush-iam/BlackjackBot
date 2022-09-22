import itertools

from aiohttp.web_app import Application

from app.admin_api.admin import routes as admin_routes
from app.admin_api.blackjack import routes as blackjack_routes


def setup_routes(app: Application) -> None:
    routes = itertools.chain(
        admin_routes.routes(),
        blackjack_routes.routes(),
    )
    app.add_routes(routes)
