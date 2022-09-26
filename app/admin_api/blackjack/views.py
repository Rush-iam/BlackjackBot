from aiohttp.web_response import json_response
from aiohttp_apispec import docs, response_schema

from app.admin_api.web.base.base_view import AuthView

from .schemas import ChatListSchema, GameListSchema, PlayerListSchema


class ChatListView(AuthView):
    @docs(
        tags=['blackjack'],
        summary='List chats',
        description='Lists all chats where games are created',
    )
    @response_schema(ChatListSchema)
    async def get(self):
        chats = await self.store.blackjack.list_chats()
        return json_response(ChatListSchema().dump({'chats': chats}))


class GameListView(AuthView):
    @docs(
        tags=['blackjack'],
        summary='List games',
        description='Lists all games where games are created',
    )
    @response_schema(GameListSchema)
    async def get(self):
        games = await self.store.blackjack.list_games()
        return json_response(GameListSchema().dump({'games': games}))


class PlayerListView(AuthView):
    @docs(
        tags=['blackjack'],
        summary='List players',
        description='Lists all players where players are created',
    )
    @response_schema(PlayerListSchema)
    async def get(self):
        players = await self.store.blackjack.list_players()
        return json_response(PlayerListSchema().dump({'players': players}))
