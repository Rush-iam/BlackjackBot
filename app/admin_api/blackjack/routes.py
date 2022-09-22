from aiohttp import web
from aiohttp.web_routedef import RouteDef

from . import views


def routes() -> list[RouteDef]:
    return [
        web.view('/blackjack/chats', views.ChatListView),
        web.view('/blackjack/games', views.GameListView),
        web.view('/blackjack/players', views.PlayerListView),
    ]
