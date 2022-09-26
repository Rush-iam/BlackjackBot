from datetime import datetime

from sqlalchemy import desc, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.blackjack_bot.blackjack.models import ChatModel, GameModel, PlayerModel
from app.blackjack_bot.blackjack.player import Player
from app.packages.postgres.accessor import DatabaseAccessor


class BlackjackStore(DatabaseAccessor):
    async def create_chat_if_not_exists(self, tg_chat_id: int) -> None:
        try:
            async with self.session() as db:
                db.add(ChatModel(tg_chat_id=tg_chat_id))
                await db.commit()
        except IntegrityError:
            pass

    async def create_game(self, tg_chat_id: int) -> int:
        async with self.session() as db:
            game = GameModel(tg_chat_id=tg_chat_id)
            db.add(game)
            await db.commit()
            return game.id

    async def get_or_create_player(self, tg_user_id: int, name: str) -> Player:
        async with self.session() as db:
            try:
                player = PlayerModel(tg_user_id=tg_user_id, name=name)
                db.add(player)
                await db.commit()
            except IntegrityError:
                await db.rollback()
                player = await db.get(PlayerModel, tg_user_id)
                if player.name != name:
                    player.name = name
                    db.add(player)
                    await db.commit()
        return Player(player_id=tg_user_id, name=name, balance=player.balance)

    async def add_players_to_game_and_chat(
        self, game_id: int, chat_id: int, player_ids: list[int]
    ) -> None:
        async with self.session() as db:
            game = await db.get(GameModel, game_id)
            chat = await db.get(ChatModel, chat_id)
            for player_id in player_ids:
                player = await db.get(
                    entity=PlayerModel,
                    ident=player_id,
                    options=[
                        selectinload(PlayerModel.games),
                        selectinload(PlayerModel.chats),
                    ],
                )
                player.games.append(game)
                player.chats.append(chat)
            await db.commit()

    async def finish_game(self, game_id: int, players: list[Player]) -> None:
        async with self.session() as db:
            await db.execute(
                update(GameModel)
                .where(GameModel.id == game_id)
                .values(end_time=datetime.now())
            )
            for player in players:
                db_player: PlayerModel = await db.get(PlayerModel, player.id)
                db_player.balance = player.balance
                db.add(db_player)
            await db.commit()

    async def get_top_players(
        self, chat_id: int | None = None, limit: int = 10
    ) -> list[Player]:
        async with self.session() as db:
            if chat_id is None:
                result = await db.execute(
                    select(PlayerModel).order_by(desc(PlayerModel.balance)).limit(limit)
                )
                players = result.scalars().all()
            else:
                chat = await db.get(
                    ChatModel, chat_id, [selectinload(ChatModel.players)]
                )
                players = chat.players

            return sorted(
                (
                    Player(player.tg_user_id, player.name, player.balance)
                    for player in players
                ),
                key=lambda player: player.balance,
                reverse=True,
            )
