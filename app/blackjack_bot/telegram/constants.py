from enum import StrEnum, auto


API_URL = 'https://api.telegram.org/bot'


class TelegramMethod(StrEnum):
    getMe = auto()
    getUpdates = auto()
    sendMessage = auto()
    editMessageText = auto()
    deleteMessage = auto()
    answerCallbackQuery = auto()


class MessageEntityType(StrEnum):
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


class ChatType(StrEnum):
    private = auto()
    group = auto()
    supergroup = auto()
    channel = auto()
