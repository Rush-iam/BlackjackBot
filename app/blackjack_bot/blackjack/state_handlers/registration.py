from app.blackjack_bot.blackjack.player import PlayerState
from app.blackjack_bot.bot.inline_keyboard import InlineButton, InlineKeyboard
from app.blackjack_bot.telegram.dtos import User

from .base import StateHandler


class RegistrationHandler(StateHandler):
    title: str = 'Регистрация игроков'
    query_commands: list[str] = ['add', 'remove']

    async def start(self) -> None:
        self.game.timer.run_after(self.finish)
        await self.game.render_message()

    async def finish(self):
        if self.game.players:
            await self.game.store.add_players_to_game_and_chat(
                game_id=self.game.id,
                chat_id=self.game.chat_id,
                player_ids=[player.id for player in self.game.players],
            )
            await self.game.next_state_transition()
        else:
            await self.game.finish_game()

    async def handle(self, tg_player: User, data: str) -> tuple[bool, str | None]:
        found_player = self.game.player_find(tg_player.id)

        if data == 'add' and not found_player:
            player = await self.game.store.get_or_create_player(
                tg_player.id, tg_player.short_name
            )
            if player.state == PlayerState.idle:
                player.state = PlayerState.waiting
                self.game.players.append(player)
                return True, 'Добро пожаловать!'
        elif data == 'remove' and found_player:
            self.game.players.pop(self.game.players.index(found_player))
            found_player.state = PlayerState.idle
            return True, 'Уже уходите?'
        return False, 'Не тыкай дважды! :)'

    def render_lines(self) -> list[str]:
        return [player.str_with_balance_v2() for player in self.game.players]

    @staticmethod
    def render_keyboard() -> InlineKeyboard:
        keyboard = InlineKeyboard()
        keyboard[0][0] = InlineButton(text='☑', callback_data='remove')
        keyboard[0][1] = InlineButton(text='✅', callback_data='add')
        return keyboard
