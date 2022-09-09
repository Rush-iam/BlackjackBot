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
        self.config: TelegramConfig = config.telegram
        self.session: ClientSession | None = None
        self.updates_handler: Callable[[list[Update]], Awaitable[None]] | None = None

    def set_updates_handler(
        self, updates_handler: Callable[[list[Update]], Awaitable[None]]
    ) -> None:
        self.updates_handler = updates_handler

    async def run_loop(self) -> None:
        self.session = ClientSession()
        if self.updates_handler is None:
            raise Exception('TelegramAccessor: connect: updates_handler not set')
        poller = Poller(
            config=self.config,
            session=self.session,
            updates_handler=self.updates_handler,
        )
        poll_config = UpdateConfig(
            timeout=self.config.poll_timeout,
            allowed_updates=['message', 'callback_query'],
        )
        await poller.run_loop(poll_config)
        await self.session.close()

    async def send_message(
        self,
        chat_id: int | str,
        text: str,
        **kwargs: Any,
    ) -> Message | None:
        if not self.session:
            raise Exception('TelegramAccessor: send_message: session not available')

        message = self._new_message(chat_id, text, **kwargs)
        send_message_request = partial(
            self.session.post,
            url=build_query(self.config.token, TelegramMethod.sendMessage),
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
