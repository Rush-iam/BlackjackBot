from typing import Callable, Awaitable

from app.blackjack_bot.telegram.accessor import TelegramAccessor
from app.blackjack_bot.telegram.constants import MessageEntityType
from app.blackjack_bot.telegram.dtos import Update, Message, CallbackQuery
from app.packages.logger import logger


class BotAccessor:
    def __init__(self, telegram: TelegramAccessor):
        self.telegram: TelegramAccessor = telegram
        self.telegram.register_updates_handler(self._handle_updates)
        self.commands: dict[str, Callable[[Message], Awaitable[None]]] = {}

    def register_command(
        self, command: str, function: Callable[[Message], Awaitable[None]]
    ) -> None:
        self.commands[command] = function

    async def run(self) -> None:
        await self.telegram.run_loop()

    async def send_message(self, chat_id: int, text: str) -> Message | None:
        return await self.telegram.send_message(chat_id, text)

    async def edit_message(
        self, chat_id: int | str, message_id: int, text: str
    ) -> Message | None:
        return await self.telegram.edit_message_text(chat_id, message_id, text)

    async def _handle_updates(self, updates: list[Update]) -> None:
        for update in updates:
            await self._handle_update(update)

    async def _handle_update(self, update: Update) -> None:
        if message := update.message:
            await self._handle_message(message)
        elif callback_query := update.callback_query:
            await self._handle_callback_query(callback_query)

    async def _handle_message(self, message: Message) -> None:
        if message.from_:
            logger.info('%s: %s', message.from_.username, message.text)
        if not message.entities:
            return
        for entity in message.entities[:1]:
            if entity.type == MessageEntityType.bot_command:
                command = message.text[entity.offset:entity.offset + entity.length]
                if command_handler := self.commands.get(command):
                    await command_handler(message)

    async def _handle_callback_query(self, callback_query: CallbackQuery) -> None:
        ...
