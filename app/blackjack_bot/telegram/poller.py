from asyncio import CancelledError, shield, sleep
from functools import partial
from json import JSONDecodeError
from typing import Any, Awaitable, Callable, cast

from aiohttp import ClientResponse, ClientSession, ClientTimeout, ContentTypeError
from aiohttp.web_exceptions import HTTPOk

from app.packages.config import TelegramConfig
from app.packages.logger import logger

from .constants import TelegramMethod
from .dtos import TelegramResponse, Update, UpdateConfig
from .utils import build_query


class Poller:
    def __init__(
        self,
        config: TelegramConfig,
        session: ClientSession,
        updates_handler: Callable[[list[Update]], Awaitable[None]],
    ):
        self.config: TelegramConfig = config
        self.session: ClientSession = session
        self.handler: Callable[[list[Update]], Awaitable[None]] = updates_handler

    async def run_loop(self, poll_config: UpdateConfig) -> None:
        config = poll_config.dict(exclude_unset=True)
        get_updates_request = partial(
            self.session.get,
            url=build_query(self.config.token, TelegramMethod.getUpdates),
            params=config,
            timeout=ClientTimeout(total=self.config.poll_timeout * 2),
        )
        errors_count = 0
        logger.info('Telegram Poller started')
        while True:
            try:
                async with get_updates_request() as response:
                    last_update_id = await shield(self._handle_response(response))
                    if last_update_id:
                        config['offset'] = last_update_id + 1
                errors_count = 0
            except CancelledError:
                break
            except Exception as exc:  # pylint: disable=W0703
                logger.exception(exc)
                errors_count += 1
                if errors_count >= 5:
                    raise
                await sleep(5)
        logger.info('Telegram Poller stopped')

    async def _handle_response(self, response: ClientResponse) -> int | None:
        if response.status != HTTPOk.status_code:
            await self._log_error(response)
            return None

        tg_response = TelegramResponse(**await response.json())
        if tg_response.result:
            update_dicts = cast(list[dict[str, Any]], tg_response.result)
            updates = [Update(**update_dict) for update_dict in update_dicts]
            await self.handler(updates)
            last_update_id = updates[-1].update_id
            return last_update_id
        return None

    @staticmethod
    async def _log_error(response: ClientResponse) -> None:
        try:
            data = await response.json()
            error = TelegramResponse(**data)
            logger.error(
                '%d %s (extra: %s)',
                error.error_code,
                error.description,
                error.parameters,
            )
        except (ContentTypeError, JSONDecodeError) as exc:
            data = await response.text()
            logger.error('%s, %s', exc, data)
            await sleep(1)
