from asyncio import Task, create_task, sleep
from typing import Awaitable, Callable

from app.blackjack_bot.bot.message_editor import MessageEditor
from app.packages.logger import logger


class Timer:
    timer_emojis: tuple[str, ...] = (
        '🕛', '🕐', '🕑', '🕒', '🕓', '🕔', '🕕', '🕖', '🕗', '🕘', '🕙', '🕚'
    )

    def __init__(self, timer_message: MessageEditor):
        self.timer_message: MessageEditor = timer_message
        self.tasks_ref: set[Task] = set()  # protects Task from garbage collector

    def run_after(
        self, function: Callable[[], Awaitable[None]], seconds: int = 12
    ) -> Task:
        task = create_task(self._run_after(function, seconds))
        self.tasks_ref.add(task)
        task.add_done_callback(self.tasks_ref.discard)
        logger.info(
            'seconds: %d, function: %s', seconds, function.__name__
        )
        return task

    async def delete(self) -> None:
        await self.timer_message.delete()

    async def _run_after(
        self, function: Callable[[], Awaitable[None]], seconds: int = 12
    ) -> None:
        while seconds:
            await self.timer_message(self._countdown_emoji(seconds))
            await sleep(1)
            seconds -= 1
        await function()

    def _countdown_emoji(self, seconds_left: int) -> str:
        emoji_index = (len(self.timer_emojis) - seconds_left) % len(self.timer_emojis)
        return self.timer_emojis[emoji_index]
