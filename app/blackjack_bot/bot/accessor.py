from typing import Awaitable, Callable

from app.blackjack_bot.telegram.accessor import TelegramAccessor
from app.blackjack_bot.telegram.constants import MessageEntityType
from app.blackjack_bot.telegram.dtos import (
    CallbackQuery,
    InlineKeyboardMarkup,
    Message,
    Update,
)
from app.packages.logger import logger


CommandHandlerCallable = Callable[[Message], Awaitable[None]]
QueryHandlerCallable = Callable[[CallbackQuery], Awaitable[str | None]]


class BotAccessor:
    def __init__(self, telegram: TelegramAccessor):
        self.telegram: TelegramAccessor = telegram
        self.telegram.register_updates_handler(self._handle_updates)
        self.commands: dict[str, CommandHandlerCallable] = {}
        self.query_handlers: dict[str, QueryHandlerCallable] = {}

    def register_command_handler(
        self, command: str, function: CommandHandlerCallable
    ) -> None:
        self.commands[command] = function

    def register_query_handler(
        self, prefix: str, function: QueryHandlerCallable
    ) -> None:
        self.query_handlers[prefix] = function

    async def run(self) -> None:
        await self.telegram.run_loop()

    async def send_message(self, chat_id: int, text: str) -> Message | None:
        return await self.telegram.send_message(chat_id, text)

    async def edit_message(
        self,
        chat_id: int | str,
        message_id: int,
        text: str,
        keyboard: InlineKeyboardMarkup | None = None,
    ) -> Message | None:
        return await self.telegram.edit_message_text(
            chat_id, message_id, text, keyboard
        )

    async def delete_message(self, chat_id: int, message_id: int) -> bool:
        return await self.telegram.delete_message(chat_id, message_id)

    async def _handle_updates(self, updates: list[Update]) -> None:
        for update in updates:
            if message := update.message:
                await self._handle_message(message)
            elif callback_query := update.callback_query:
                await self._handle_callback_query(callback_query)

    async def _handle_message(self, message: Message) -> None:
        if message.from_:
            logger.info('%s: %s', message.from_.username, message.text)
        if not message.text or not message.entities:
            return
        for entity in message.entities[:1]:
            if entity.type is MessageEntityType.bot_command:
                command = message.text[entity.offset : entity.offset + entity.length]
                command_without_mention = command.split('@')[0]
                if command_handler := self.commands.get(command_without_mention):
                    await command_handler(message)

    async def _handle_callback_query(self, callback_query: CallbackQuery) -> None:
        if not callback_query.data:
            logger.warning('cannot handle callback_query: %s', callback_query)
            return
        prefix, data = callback_query.data.split(maxsplit=1)
        if query_handler := self.query_handlers.get(prefix):
            callback_query.data = data
            answer_text = await query_handler(callback_query)
            await self.telegram.answer_callback_query(callback_query.id, answer_text)
        else:
            logger.warning('unknown callback_query data: %s %s', prefix, data)
            await self.telegram.answer_callback_query(callback_query.id)
