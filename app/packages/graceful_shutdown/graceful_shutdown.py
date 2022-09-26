import asyncio
import sys
from signal import SIGINT, SIGTERM, signal, strsignal
from types import FrameType
from typing import Awaitable, Callable

from app.packages.logger import logger


class GracefulShutdown:
    _on_shutdown_fn: Callable[[], Awaitable] | None = None

    @classmethod
    def setup(cls, on_shutdown_fn: Callable[[], Awaitable] | None = None) -> None:
        cls._on_shutdown_fn = on_shutdown_fn
        signal(SIGINT, cls._signal_handler)
        signal(SIGTERM, cls._signal_handler)

    @classmethod
    def _signal_handler(cls, signum: int, _: FrameType | None) -> None:
        logger.debug('Got signal: %s [%d]', strsignal(signum), signum)
        asyncio.get_event_loop().stop()
        if cls._on_shutdown_fn:
            cls._on_shutdown_fn()
        sys.exit(0)
