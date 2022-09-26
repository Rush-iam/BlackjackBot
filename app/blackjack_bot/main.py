import asyncio

from app.blackjack_bot.blackjack.lobby import Lobby
from app.blackjack_bot.blackjack.store import BlackjackStore
from app.blackjack_bot.bot.accessor import BotAccessor
from app.blackjack_bot.telegram.accessor import TelegramAccessor
from app.packages.config import get_config
from app.packages.graceful_shutdown import GracefulShutdown
from app.packages.logger import setup_logging
from app.packages.postgres.database import Database


async def run_app() -> None:
    setup_logging()
    config = get_config()
    GracefulShutdown.setup()

    db = Database(config.database_dsn)
    await db.connect()

    telegram = TelegramAccessor(config)
    bot = BotAccessor(telegram)
    blackjack_lobby = Lobby(bot, BlackjackStore(db))
    _ = blackjack_lobby

    await bot.run()


if __name__ == '__main__':
    asyncio.run(run_app())
