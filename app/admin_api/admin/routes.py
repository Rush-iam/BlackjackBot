from aiohttp import web
from aiohttp.web_routedef import RouteDef

from . import views


def routes() -> list[RouteDef]:
    return [
        web.view('/admin.login', views.AdminLoginView),
        web.view('/admin.current', views.AdminCurrentView),
    ]
