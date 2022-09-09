from .constants import API_URL, TelegramMethod


def build_query(token: str, method: TelegramMethod) -> str:
    return f'{API_URL}{token}/{method}'
