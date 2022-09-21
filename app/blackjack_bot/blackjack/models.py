from datetime import datetime

from sqlalchemy import Column, Integer, Table, ForeignKey, func, Text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship

from app.packages.postgres.metadata import BaseMetadata


players_chats = Table(
    'players_chats',
    BaseMetadata.metadata,
    Column('tg_user_id', ForeignKey('players.tg_user_id'), nullable=False),
    Column('tg_chat_id', ForeignKey('chats.tg_chat_id'), nullable=False),
)

players_games = Table(
    'players_games',
    BaseMetadata.metadata,
    Column('tg_user_id', ForeignKey('players.tg_user_id'), nullable=False),
    Column('game_id', ForeignKey('games.id'), nullable=False),
)


class PlayerModel(BaseMetadata):
    __tablename__ = 'players'

    tg_user_id: int = Column(Integer(), primary_key=True)
    name: str = Column(Text(), nullable=False)
    balance: int = Column(Integer(), default=1000, nullable=False)  # TODO: to config

    chats: list['ChatModel'] = relationship(
        'ChatModel', secondary=players_chats, back_populates='players'
    )
    games: list['GameModel'] = relationship(
        'GameModel', secondary=players_games, back_populates='players'
    )


class ChatModel(BaseMetadata):
    __tablename__ = 'chats'

    tg_chat_id: int = Column(Integer(), primary_key=True)

    players: list['PlayerModel'] = relationship(
        'PlayerModel', secondary=players_chats, back_populates='chats'
    )
    games: list['GameModel'] = relationship('GameModel', back_populates='chat')


class GameModel(BaseMetadata):
    __tablename__ = 'games'

    id: int = Column(Integer(), primary_key=True)
    tg_chat_id: int = Column(ForeignKey('chats.tg_chat_id'), nullable=False)
    start_time: datetime = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    end_time: datetime | None = Column(TIMESTAMP(timezone=True))

    players: list['PlayerModel'] = relationship(
        'PlayerModel', secondary=players_games, back_populates='games'
    )
    chat: 'ChatModel' = relationship('ChatModel', back_populates='games')
