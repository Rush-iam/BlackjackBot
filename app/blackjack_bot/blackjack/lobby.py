from functools import partial
from typing import cast, Callable, Awaitable

from app.blackjack_bot.bot.accessor import BotAccessor
from app.blackjack_bot.telegram.dtos import Message, CallbackQuery
from app.blackjack_bot.telegram.inline_keyboard import InlineKeyboard

from .game import Game, GameState


class Lobby:
    name = 'blackjack'

    def __init__(self, bot: BotAccessor):
        bot.register_command_handler('/start', self.new_game_router)
        bot.register_query_handler(
            prefix=self.name, function=self.callback_query_router
        )
        self.bot: BotAccessor = bot
        self.active_games: dict[int, Game] = {}

    async def new_game_router(self, message: Message) -> None:
        game = self.active_games.get(message.chat.id)
        if game and game.state is not GameState.finished:
            return
        await self.new_game(message.chat.id)

    async def new_game(self, chat_id: int) -> None:
        game_message = await self.bot.send_message(chat_id, '🃏 ...')
        if not game_message:
            return

        message_editor = cast(
            Callable[[str, InlineKeyboard | None], Awaitable[None]],
            partial(self.message_editor, game_message.chat.id, game_message.message_id)
        )
        game = Game(game_id=chat_id, message_editor=message_editor)
        self.active_games[chat_id] = game
        await game.start()

    async def callback_query_router(self, callback_query: CallbackQuery) -> str | None:
        game = self.active_games.get(callback_query.message.chat.id)
        if not game:
            return
        return await game.handle_event(
            player_id=callback_query.from_.id, data=callback_query.data
        )

    async def message_editor(
        self,
        chat_id: int | str,
        message_id: int,
        text: str,
        keyboard: InlineKeyboard | None = None,
    ) -> None:
        if keyboard:
            keyboard.set_callback_data_prefix(self.name)
        await self.bot.edit_message(chat_id, message_id, text, keyboard)
