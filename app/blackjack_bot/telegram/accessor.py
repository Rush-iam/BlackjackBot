import os
from typing import Any, Awaitable, Callable

from aiohttp import ClientSession, ClientTimeout
from aiohttp.client import _RequestContextManager
from aiolimiter import AsyncLimiter
from pydantic import BaseModel

from app.packages.config import Config, TelegramConfig
from app.packages.logger import logger

from .constants import TelegramMethod
from .dtos import (
    AnswerCallbackQueryRequest,
    DeleteMessageRequest,
    EditMessageTextRequest,
    InlineKeyboardMarkup,
    Message,
    SendMessageRequest,
    TelegramResponse,
    Update,
    UpdateRequest,
)
from .poller import Poller
from .utils import build_query, log_error


class TelegramAccessor:
    rps_limit: int = int(os.getenv('TG_LIMITER', '3'))

    def __init__(self, config: Config):
        self._config: TelegramConfig = config.telegram
        self._session: ClientSession | None = None
        self._updates_handler: Callable[[list[Update]], Awaitable[None]] | None = None
        self.limiter: AsyncLimiter = AsyncLimiter(
            max_rate=self.rps_limit, time_period=1
        )

    def register_updates_handler(
        self, updates_handler: Callable[[list[Update]], Awaitable[None]]
    ) -> None:
        self._updates_handler = updates_handler

    async def run_loop(self) -> None:
        self._session = ClientSession()
        if self._updates_handler is None:
            raise Exception(
                f'{self.__class__.__name__}: {self.run_loop.__name__}: '
                f'updates_handler not set'
            )
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
        result = await self._request(TelegramMethod.sendMessage, request)
        return Message.parse_obj(result) if result else None

    async def edit_message_text(
        self,
        chat_id: int | str,
        message_id: int,
        text: str,
        reply_markup: InlineKeyboardMarkup | None = None,
        **kwargs: Any,
    ) -> Message | None:
        request = EditMessageTextRequest(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            reply_markup=reply_markup,
            **kwargs,
        )
        result = await self._request(TelegramMethod.editMessageText, request)
        return Message.parse_obj(result) if result else None

    async def delete_message(self, chat_id: int | str, message_id: int) -> bool:
        request = DeleteMessageRequest(
            chat_id=chat_id,
            message_id=message_id,
        )
        return await self._request(TelegramMethod.deleteMessage, request)

    async def answer_callback_query(
        self,
        callback_query_id: str,
        text: str | None = None,
        show_alert: bool | None = None,
        **kwargs: Any,
    ) -> bool:
        request = AnswerCallbackQueryRequest(
            callback_query_id=callback_query_id,
            text=text,
            show_alert=show_alert,
            **kwargs,
        )
        result = await self._request(TelegramMethod.answerCallbackQuery, request)
        return bool(result)

    async def _request(self, method: TelegramMethod, request_payload: BaseModel) -> Any:
        async with await self._request_call(method, request_payload) as response:
            tg_response = TelegramResponse(**await response.json())
            if not tg_response.ok:
                await log_error(response)
                return None
            return tg_response.result

    async def _request_call(
        self, method: TelegramMethod, request_payload: BaseModel
    ) -> _RequestContextManager:
        logger.info('%s: %s', method, request_payload.dict(exclude_none=True))
        if not self._session:
            raise Exception(
                f'{self.__class__.__name__}: {self._request_call.__name__}: no session'
            )
        async with self.limiter:  # TODO: per chat limiter, do not limit answerQuery
            return self._session.post(
                url=build_query(self._config.token, method),
                json=request_payload.dict(exclude_none=True),
                timeout=ClientTimeout(total=5),
            )
