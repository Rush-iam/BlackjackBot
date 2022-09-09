import asyncio
import sys
from signal import SIGINT, SIGTERM, signal, strsignal
from types import FrameType

from app.packages.logger import logger


def setup_graceful_shutdown() -> None:
    signal(SIGINT, signal_handler)
    signal(SIGTERM, signal_handler)


def signal_handler(signum: int, _: FrameType | None) -> None:
    logger.debug('Got signal: %s [%d]', strsignal(signum), signum)
    asyncio.get_event_loop().stop()
    sys.exit(0)
