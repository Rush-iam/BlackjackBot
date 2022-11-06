# BJBot - Blackjack Telegram Bot

## What is it?
**BJBot** - bot for Telegram, which invites to play Blackjack.

## What is inside?
### Application workflow schema
```mermaid
flowchart LR

subgraph Database [Database]
    DB[(PostgreSQL)]
end
subgraph API [App services]
  BACKEND((Admin<br/>API))
  BOT((Blackjack<br/>Bot))
end
subgraph External clients
    REST{{Administrator}}
end
subgraph External service
    TELEGRAM[Telegram<br/>API]
end

BACKEND ---|REST API| REST
DB ---|get<br/>statistics| BACKEND

BOT ---|UI<br/>messages| TELEGRAM
DB ---|store chats,<br/>games, players| BOT
```
---
_Artyom **nGragas** Kornikov. Project for KTS Python Async Backend._

---
# BJBot - Blackjack Telegram Bot

## Что это?
**BJBot** - бот для Telegram, который предложит сыграть в Blackjack.

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
---
_Артем **nGragas** Корников. Учебный проект для KTS Backend._
