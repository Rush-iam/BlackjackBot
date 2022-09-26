from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.orm import selectinload

from app.blackjack_bot.blackjack.models import ChatModel, GameModel, PlayerModel
from app.packages.postgres.accessor import DatabaseAccessor

from .dtos import Chat, Game, Player


class BlackjackAccessor(DatabaseAccessor):
    async def list_chats(self) -> list[Chat]:
        async with self.session() as db:
            result: Result = await db.execute(select(ChatModel))
            chats = result.scalars().all()
        return [Chat.from_orm(chat) for chat in chats]

    async def list_players(self) -> list[Player]:
        async with self.session() as db:
            result: Result = await db.execute(
                select(PlayerModel).options(selectinload(PlayerModel.chats))
            )
            players = result.scalars().all()
        return [Player.from_orm(player) for player in players]

    async def list_games(self) -> list[Game]:
        async with self.session() as db:
            result: Result = await db.execute(
                select(GameModel).options(
                    selectinload(GameModel.players),
                )
            )
            games = result.scalars().all()
        return [Game.from_orm(game) for game in games]
