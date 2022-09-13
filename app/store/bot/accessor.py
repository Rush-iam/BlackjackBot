from app.store.telegram.accessor import TelegramAccessor
from app.store.telegram.dtos import Update
from app.web.logger import logger


class BotAccessor:
    def __init__(self, telegram: TelegramAccessor):
        self.telegram = telegram
        self.telegram.updates_handler = self.handle_updates

    async def handle_updates(self, updates: list[Update]) -> None:
        for update in updates:
            await self._handle_update(update)

    async def _handle_update(self, update: Update) -> None:
        if message := update.message:
            if message.from_:
                logger.info('%s: %s', message.from_.username, message.text)
                message = await self.telegram.send_message(
                    message.from_.id,
                    message.text or 'ok!',
                )
            _ = message
        elif query := update.callback_query:
            _ = query
            return
