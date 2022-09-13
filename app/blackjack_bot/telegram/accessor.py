from functools import partial
from typing import Any, Awaitable, Callable, cast

from aiohttp import ClientSession, ClientTimeout

from app.packages.config import Config, TelegramConfig

from .constants import TelegramMethod
from .dtos import Message, MessageConfig, TelegramResponse, Update, UpdateConfig
from .poller import Poller
from .utils import build_query


class TelegramAccessor:
    def __init__(self, config: Config):
        self._config: TelegramConfig = config.telegram
        self._session: ClientSession | None = None
        self._updates_handler: Callable[[list[Update]], Awaitable[None]] | None = None

    @property
    def updates_handler(self) -> Callable[[list[Update]], Awaitable[None]] | None:
        return self._updates_handler

    @updates_handler.setter
    def updates_handler(
        self, updates_handler: Callable[[list[Update]], Awaitable[None]]
    ) -> None:
        self._updates_handler = updates_handler

    async def run_loop(self) -> None:
        self._session = ClientSession()
        if self._updates_handler is None:
            raise Exception('TelegramAccessor: connect: updates_handler not set')
        poller = Poller(
            config=self._config,
            session=self._session,
            updates_handler=self._updates_handler,
        )
        poll_config = UpdateConfig(
            timeout=self._config.poll_timeout,
            allowed_updates=['message', 'callback_query'],
        )
        await poller.run_loop(poll_config)
        await self._session.close()

    async def send_message(
        self,
        chat_id: int | str,
        text: str,
        **kwargs: Any,
    ) -> Message | None:
        if not self._session:
            raise Exception('TelegramAccessor: send_message: session not available')

        message = self._new_message(chat_id, text, **kwargs)
        send_message_request = partial(
            self._session.post,
            url=build_query(self._config.token, TelegramMethod.sendMessage),
            json=message.dict(exclude_unset=True),
            timeout=ClientTimeout(total=5),
        )
        async with send_message_request() as response:
            tg_response = TelegramResponse(**await response.json())
            if not tg_response.ok:
                return None
            return cast(Message, tg_response.result)

    @staticmethod
    def _new_message(chat_id: int | str, text: str, **kwargs: Any) -> MessageConfig:
        return MessageConfig(
            chat_id=chat_id,
            text=text,
            **kwargs,
        )
