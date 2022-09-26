from datetime import datetime

from app.admin_api.web.base.base_dto import DatabaseItem, OrmItem


class Chat(OrmItem):
    tg_chat_id: int


class Player(OrmItem):
    tg_user_id: int
    name: str
    balance: int
    # chats: list[Chat]


class Game(DatabaseItem):
    tg_chat_id: int
    start_time: datetime
    end_time: datetime | None = None
    players: list[Player]
