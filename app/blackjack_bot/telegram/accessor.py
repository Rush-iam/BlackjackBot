from typing import Any, Awaitable, Callable

from aiohttp import ClientSession, ClientTimeout
from aiohttp.client import _RequestContextManager
from pydantic import BaseModel

from app.packages.config import Config, TelegramConfig

from .constants import TelegramMethod
from .dtos import (
    Message,
    SendMessageRequest,
    TelegramResponse,
    Update,
    UpdateRequest,
    EditMessageTextRequest,
)
from .poller import Poller
from .utils import build_query, log_error


class TelegramAccessor:
    def __init__(self, config: Config):
        self._config: TelegramConfig = config.telegram
        self._session: ClientSession | None = None
        self._updates_handler: Callable[[list[Update]], Awaitable[None]] | None = None

    def register_updates_handler(
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
        poll_config = UpdateRequest(
            timeout=self._config.poll_timeout,
            allowed_updates=['message', 'callback_query'],
        )
        await poller.run_loop(poll_config)
        await self._session.close()

    async def send_message(
        self, chat_id: int | str, text: str, **kwargs: Any
    ) -> Message | None:
        request = SendMessageRequest(
            chat_id=chat_id,
            text=text,
            **kwargs,
        )
        return await self._message_request(TelegramMethod.sendMessage, request)

    async def edit_message_text(
        self, chat_id: int | str, message_id: int, text: str, **kwargs: Any
    ) -> Message | None:
        request = EditMessageTextRequest(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            **kwargs,
        )
        return await self._message_request(TelegramMethod.editMessageText, request)

    async def _message_request(
        self, method: TelegramMethod, request_payload: BaseModel
    ) -> Message | None:
        if not self._session:
            raise Exception('TelegramAccessor: edit_message_text: no session')
        async with self._request(method, request_payload) as response:
            tg_response = TelegramResponse(**await response.json())
            if not tg_response.ok:
                await log_error(response)
                return None
            return Message(**tg_response.result)

    def _request(
        self, method: TelegramMethod, request_payload: BaseModel
    ) -> _RequestContextManager:
        return self._session.post(
            url=build_query(self._config.token, method),
            json=request_payload.dict(exclude_unset=True),
            timeout=ClientTimeout(total=5),
        )
