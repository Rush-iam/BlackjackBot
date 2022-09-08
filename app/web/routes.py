import itertools

from aiohttp.web_app import Application

from app.admin import routes as admin_routes


def setup_routes(app: Application) -> None:
    routes = itertools.chain(
        admin_routes.routes(),
    )
    app.add_routes(routes)
