import asyncio
from json import JSONDecodeError

from aiohttp import ClientResponse, ContentTypeError

from app.packages.logger import logger

from .constants import API_URL, TelegramMethod
from .dtos import TelegramResponse


def build_query(token: str, method: TelegramMethod) -> str:
    return f'{API_URL}{token}/{method}'


async def log_error(response: ClientResponse) -> None:
    try:
        data = await response.json()
        error = TelegramResponse(**data)
        logger.error(
            '%d %s (extra: %s, %s)',
            error.error_code,
            error.description,
            error.parameters,
            response.real_url,
        )
    except (ContentTypeError, JSONDecodeError) as exc:
        data = await response.text()
        logger.error('%s, %s, %s', exc, data, response.real_url)
        await asyncio.sleep(1)
