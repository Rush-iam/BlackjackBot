from enum import Enum, auto


API_URL = 'https://api.telegram.org/bot'


class GeneratedStrEnum(str, Enum):
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name


class TelegramMethod(GeneratedStrEnum):
    getMe = auto()
    getUpdates = auto()
    sendMessage = auto()


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
