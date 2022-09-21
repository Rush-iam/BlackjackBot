from functools import partial

from app.blackjack_bot.bot.accessor import BotAccessor
from app.blackjack_bot.bot.message_editor import MessageEditor
from app.blackjack_bot.telegram.dtos import CallbackQuery, Message
from app.packages.logger import logger

from .game import Game, GameState
from .store import BlackjackStore
from .timer import Timer


class Lobby:
    prefix = 'blackjack'

    def __init__(self, bot: BotAccessor, store: BlackjackStore):
        bot.register_command_handler('/start', self.new_game_router)
        bot.register_command_handler('/my_balance', self.my_balance_router)
        bot.register_command_handler('/top', self.top_router)
        bot.register_command_handler(
            '/top_global', partial(self.top_router, top_global=True)
        )
        bot.register_query_handler(
            prefix=self.prefix, function=self.callback_query_router
        )
        self.bot: BotAccessor = bot
        self.active_games: dict[int, Game] = {}
        self.store: BlackjackStore = store

    async def new_game_router(self, message: Message) -> None:
        game = self.active_games.get(message.chat.id)
        if game and game.state is not GameState.finished:
            return  # TODO: reply with point
        await self.new_game(message.chat.id)

    async def my_balance_router(self, message: Message) -> None:
        player_id = message.from_.id
        player_name = message.from_.short_name
        player = await self.store.get_or_create_player(player_id, player_name)
        await self.bot.send_message(
            chat_id=message.chat.id,
            text=f'💰{player.name}: {player.balance}$',
        )

    async def top_router(self, message: Message, top_global: bool = False) -> None:
        chat_id = None if top_global else message.chat.id
        players = await self.store.get_top_players(chat_id=chat_id)

        title_init = f'🏆{"🌍" if top_global else "💬"} ТОП-игроки'
        title_extra = 'этой планеты' if top_global else 'этого чата'
        title = f'{title_init} {title_extra}'
        lines = '\n'.join(player.str_with_balance() for player in players)
        await self.bot.send_message(
            chat_id=message.chat.id,
            text=f'{title}\n\n{lines}',
        )

    async def new_game(self, chat_id: int) -> None:
        game_message = await MessageEditor.create(
            self.bot, chat_id, '🃏 ...', self.prefix
        )
        timer_message = await MessageEditor.create(
            self.bot, chat_id, Timer.timer_emojis[0], self.prefix
        )
        if not game_message or not timer_message:
            return

        await self.store.create_chat_if_not_exists(tg_chat_id=chat_id)
        game_id = await self.store.create_game(tg_chat_id=chat_id)
        game = Game(
            game_id=game_id,
            chat_id=chat_id,
            game_message=game_message,
            timer_message=timer_message,
            store=self.store,
        )
        self.active_games[chat_id] = game
        await game.start()

    async def callback_query_router(self, callback_query: CallbackQuery) -> str | None:
        if (
            not callback_query.data
            or not callback_query.message
            or not callback_query.message.chat
        ):
            logger.warning('cannot handle callback_query: %s', callback_query)
            return None
        game = self.active_games.get(callback_query.message.chat.id)
        if not game:
            return None
        return await game.handle_event(
            tg_player=callback_query.from_, data=callback_query.data
        )
