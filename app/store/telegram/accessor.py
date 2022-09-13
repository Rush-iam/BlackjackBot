from functools import partial
from typing import Any, Awaitable, Callable, cast

from aiohttp import ClientSession, ClientTimeout
from aiohttp.web_app import Application

from app.web.base.base_accessor import BaseAccessor
from app.web.config import TelegramConfig

from .constants import TelegramMethod
from .dtos import Message, MessageConfig, TelegramResponse, Update
from .poller import Poller
from .utils import build_query


class TelegramAccessor(BaseAccessor):
    def __init__(self, app: Application):
        super().__init__(app)
        self._config: TelegramConfig = app['config'].telegram
        self._session: ClientSession | None = None
        self._poller: Poller | None = None
        self._updates_handler: Callable[[list[Update]], Awaitable[None]] | None = None

    @property
    def updates_handler(self) -> Callable[[list[Update]], Awaitable[None]] | None:
        return self._updates_handler

    @updates_handler.setter
    def updates_handler(
        self, updates_handler: Callable[[list[Update]], Awaitable[None]]
    ) -> None:
        self._updates_handler = updates_handler

    async def connect(self, _: Application) -> None:
        self._session = ClientSession()
        if self._updates_handler is None:
            raise Exception('TelegramAccessor: connect: updates_handler not set')
        self._poller = Poller(
            config=self._config,
            session=self._session,
            updates_handler=self._updates_handler,
        )
        await self._poller.start()

    async def disconnect(self, app: Application) -> None:
        if self._poller:
            await self._poller.stop()
        if self._session and not self._session.closed:
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
