from asyncio import CancelledError, Task, create_task, shield, sleep, wait_for
from functools import partial
from json import JSONDecodeError
from typing import Any, Awaitable, Callable, cast

from aiohttp import ClientResponse, ClientSession, ClientTimeout, ContentTypeError
from aiohttp.web_exceptions import HTTPOk

from app.web.config import TelegramConfig
from app.web.logger import logger

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
        self.poll_task: Task[None] | None = None

    async def start(self) -> None:
        poll_config = UpdateConfig(
            timeout=self.config.poll_timeout,
            allowed_updates=['message', 'callback_query'],
        )
        self.poll_task = create_task(self._poll_task_loop(poll_config))

    async def stop(self) -> None:
        if self.poll_task:
            self.poll_task.cancel()
            await wait_for(self.poll_task, 5)
            self.poll_task = None

    async def _poll_task_loop(self, poll_config: UpdateConfig) -> None:
        config = poll_config.dict(exclude_unset=True)
        get_updates_request = partial(
            self.session.get,
            url=build_query(self.config.token, TelegramMethod.getUpdates),
            params=config,
            timeout=ClientTimeout(total=self.config.poll_timeout * 2),
        )
        logger.info('Poller task started')
        while True:
            try:
                async with get_updates_request() as response:
                    last_update_id = await shield(self._handle_response(response))
                    if last_update_id:
                        config['offset'] = last_update_id + 1
            except CancelledError:
                logger.info('Got Cancel signal')
                break
            except Exception as exc:  # pylint: disable=W0703
                logger.exception(exc)
                await sleep(5)
        logger.info('Poller task stopped')

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
