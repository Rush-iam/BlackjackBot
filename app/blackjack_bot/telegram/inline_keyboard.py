from collections import defaultdict
from typing import Annotated

from pydantic import BaseModel, conbytes

from app.blackjack_bot.telegram.dtos import InlineKeyboardMarkup, InlineKeyboardButton


class InlineButton(BaseModel):
    text: str
    url: str | None = None
    callback_data: str | None = Annotated[str, conbytes(min_length=1, max_length=64)]


class InlineKeyboard:
    def __init__(self, callback_data_prefix: str = ''):
        self._buttons: dict[int, dict[int, InlineButton]] = defaultdict(dict)
        self._callback_data_prefix: str = callback_data_prefix

    def __getitem__(self, row_index: int) -> dict[int, InlineButton] | None:
        return self._buttons[row_index]

    def set_callback_data_prefix(self, prefix: str) -> None:
        self._callback_data_prefix = prefix

    def to_reply_markup(self) -> InlineKeyboardMarkup:
        tg_buttons_list: list[list[InlineKeyboardButton]] = []
        for row in range(len(self._buttons)):
            row_dict = self._buttons.get(row)
            if not row_dict:
                raise Exception('InlineKeyboard: missing element in button row')
            tg_buttons_list.append(list())
            for column in range(len(row_dict)):
                button = row_dict.get(column)
                if not button:
                    raise Exception('InlineKeyboard: missing element in button column')
                if button.callback_data:
                    button.callback_data = (
                        f'{self._callback_data_prefix} {button.callback_data}'
                    )
                tg_button = InlineKeyboardButton(**button.dict())
                tg_buttons_list[row].append(tg_button)

        return InlineKeyboardMarkup(inline_keyboard=tg_buttons_list)
