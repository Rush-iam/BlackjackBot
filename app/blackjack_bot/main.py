import asyncio

from app.blackjack_bot.bot.accessor import BotAccessor
from app.blackjack_bot.telegram.accessor import TelegramAccessor
from app.packages.config import get_config
from app.packages.graceful_shutdown import setup_graceful_shutdown
from app.packages.logger import setup_logging


async def run_app() -> None:
    setup_graceful_shutdown()
    setup_logging()

    config = get_config()
    telegram = TelegramAccessor(config)
    bot = BotAccessor(telegram)

    await bot.run()


if __name__ == '__main__':
    asyncio.run(run_app())
