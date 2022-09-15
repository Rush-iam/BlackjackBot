from functools import partial

from app.blackjack_bot.bot.accessor import BotAccessor
from app.blackjack_bot.telegram.dtos import Message

from .game import Game, GameState


class Lobby:
    def __init__(self, bot: BotAccessor):
        self.bot: BotAccessor = bot
        self.active_games: dict[int, Game] = {}

    async def new_game_router(self, message: Message) -> None:
        await self.new_game(message.chat.id)

    async def new_game(self, chat_id: int) -> None:
        game = self.active_games.get(chat_id)
        if game and game.state is not GameState.finished:
            return

        game_message = await self.bot.send_message(chat_id, '🃏 ...')
        if not game_message:
            return

        game = Game(
            game_id=chat_id,
            message_editor=partial(
                self.message_editor,
                game_message.chat.id,
                game_message.message_id,
            )
        )
        self.active_games[chat_id] = game
        await game.start()

    async def callback_query_router(self, message: Message) -> None:
        ...

    async def message_editor(
        self, chat_id: int | str, message_id: int, text: str
    ) -> None:
        await self.bot.edit_message(chat_id, message_id, text)
