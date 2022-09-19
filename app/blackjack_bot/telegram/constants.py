from enum import auto

from app.packages.enum_generator import GeneratedStrEnum


API_URL = 'https://api.telegram.org/bot'


class TelegramMethod(GeneratedStrEnum):
    getMe = auto()
    getUpdates = auto()
    sendMessage = auto()
    editMessageText = auto()
    answerCallbackQuery = auto()


class MessageEntityType(GeneratedStrEnum):
    mention = auto()
    hashtag = auto()
    cashtag = auto()
    bot_command = auto()
    url = auto()
    phone_number = auto()
    bold = auto()
    italic = auto()
    underline = auto()
    strikethrough = auto()
    spoiler = auto()
    code = auto()
    pre = auto()
    text_link = auto()
    text_mention = auto()
    custom_emoji = auto()
