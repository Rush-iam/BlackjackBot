# BJBot - Blackjack Telegram Bot

## Что это?
**BJBot** - бот для Telegram, который предложит сыграть в Blackjack.


## Как им пользоваться?


## Как устроен внутри?
### Схема работы приложения
```mermaid
flowchart LR

subgraph Database [База Данных]
    DB[(PostgreSQL)]
end
subgraph API [Сервисы приложения]
  BACKEND((Admin<br/>API))
  BOT((Blackjack<br/>Bot))
end
subgraph Внешние клиенты
    REST{{Администратор}}
end
subgraph Внешний сервис
    TELEGRAM[Telegram<br/>API]
end

BACKEND ---|REST API| REST
DB ---|получение<br/>статистики| BACKEND

BOT ---|работа<br/>UI| TELEGRAM
DB ---|запись чатов,<br/>игр, игроков| BOT
```
## Как запустить самостоятельно?

### Локальный запуск

### Запуск в Docker Compose

---
_Артем **nGragas** Корников. Учебный проект для KTS Backend._
