from marshmallow import fields

from app.admin_api.web.base.base_schema import BaseSchema


class ChatSchema(BaseSchema):
    tg_chat_id = fields.Int(required=True)


class ChatListSchema(BaseSchema):
    chats = fields.List(fields.Nested(ChatSchema()))


class PlayerSchema(BaseSchema):
    tg_user_id = fields.Int(required=True)
    name = fields.Str(required=True)
    balance = fields.Int(required=True)
    # chats = fields.List(fields.Nested(ChatSchema()))


class PlayerListSchema(BaseSchema):
    players = fields.List(fields.Nested(PlayerSchema()))


class GameSchema(BaseSchema):
    id = fields.Int(required=True)
    tg_chat_id = fields.Int(required=True)
    start_time = fields.DateTime(required=True)
    end_time = fields.DateTime(required=False)
    players = fields.List(fields.Nested(PlayerSchema()))


class GameListSchema(BaseSchema):
    games = fields.List(fields.Nested(GameSchema()))
