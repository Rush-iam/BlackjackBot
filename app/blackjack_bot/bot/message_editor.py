from __future__ import annotations

from app.blackjack_bot.telegram.dtos import Message

from .accessor import BotAccessor
from .inline_keyboard import InlineKeyboard


class MessageEditor:
    def __init__(self, bot: BotAccessor, message: Message, callback_prefix: str = ''):
        self.bot: BotAccessor = bot
        self.message: Message = message
        self.callback_prefix: str = callback_prefix

    async def __call__(self, text: str, keyboard: InlineKeyboard | None = None) -> None:
        if keyboard:
            keyboard.set_callback_data_prefix(self.callback_prefix)
            tg_keyboard = keyboard.to_reply_markup()
        else:
            tg_keyboard = None

        if self.message.text == text and self.message.reply_markup == tg_keyboard:
            return

        new_message = await self.bot.edit_message(
            self.message.chat.id, self.message.message_id, text, tg_keyboard
        )
        if new_message:
            self.message = new_message

    @classmethod
    async def create(
        cls, bot: BotAccessor, chat_id: int | str, text: str, callback_prefix: str = ''
    ) -> MessageEditor | None:
        message = await bot.send_message(chat_id, text)
        if message is None:
            return None
        return cls(bot, message, callback_prefix)

    async def delete(self):
        await self.bot.delete_message(self.message.chat.id, self.message.message_id)
