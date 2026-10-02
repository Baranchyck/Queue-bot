# Queue-bot

Telegram-бот для управління чергою на здачу лабораторних/дисциплінарних робіт. Підтримує фіксовану кількість місць, запис на конкретну позицію, обмін місцями, можливість випередити іншого користувача, перегляд стану черги та експорт результатів у Excel.

## Основні можливості

- фіксована кількість слотів у черзі;
- запис користувача на конкретне місце;
- обмін місцями між учасниками;
- можливість "пустити людину попереду";
- перегляд поточного стану черги;
- швидка перевірка черги в Telegram;
- експорт даних у Excel;
- робота з PostgreSQL через SQLAlchemy;
- запуск у Docker для локального середовища;
- підтримка режимів polling та webhook.

## Технології

- Python 3.11+
- aiogram 3
- SQLAlchemy 2 (asyncio)
- asyncpg
- PostgreSQL 16
- Docker / Docker Compose
- openpyxl
- pydantic-settings

## Структура проекту

```text
Queue-bot/
├── app/
│   ├── __init__.py
│   ├── commands.py
│   ├── config.py
│   ├── logging_config.py
│   ├── main.py
│   ├── db/
│   ├── handlers/
│   ├── keyboards/
│   └── services/
├── middleware/
│   └── mid_logging.py
├── .env.example
├── .gitignore
├── docker-compose.yml
├── requirements.txt
├── README.md
└── .venv/
```

## Команди бота

Бот реєструє такі команди:

- `/start` — запустити бота;
- `/help` — список команд;
- `/create` — створити чергу: `/create назва`;
- `/queue` — показати чергу;
- `/join` — стати на місце: `/join номер`;
- `/leave` — вийти з черги;
- `/swap` — помінятися місцями: `/swap номер`;
- `/export` — вивантажити в Excel.

## Конфігурація

Скопіюйте `.env.example` у `.env` та заповніть значення:

```bash
cp .env.example .env
```

Приклад конфігурації:

```dotenv
BOT_TOKEN=123456:replace-me
DATABASE_URL=postgresql+asyncpg://queue:queue@localhost:5432/queue
MODE=polling
WEBHOOK_URL=https://your-service.onrender.com
WEBHOOK_SECRET=change-me-long-random-string
PORT=8080
SLOTS_COUNT=19
```

### Параметри

- `BOT_TOKEN` — токен Telegram-бота;
- `DATABASE_URL` — підключення до PostgreSQL;
- `MODE` — режим роботи: `polling` або `webhook`;
- `WEBHOOK_URL` — URL для webhook (потрібен при `MODE=webhook`);
- `WEBHOOK_SECRET` — секретний токен для webhook;
- `PORT` — порт сервера;
- `SLOTS_COUNT` — кількість місць у черзі.

## Локальний запуск

### 1) Запуск PostgreSQL через Docker

```bash
docker compose up -d db
```

### 2) Створення віртуального середовища та встановлення залежностей

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3) Запуск бота

```bash
python -m app.main
```

## Режим webhook

Для розгортання на сервісі (наприклад, Render) використовуйте режим `webhook`:

```dotenv
MODE=webhook
WEBHOOK_URL=https://your-service.onrender.com
WEBHOOK_SECRET=change-me-long-random-string
PORT=8080
```

У цьому режимі бот налаштовує webhook і працює через HTTP endpoint.

## Docker Compose

Файл `docker-compose.yml` запускає лише базу даних PostgreSQL:

```yaml
services:
  db:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_USER: queue
      POSTGRES_PASSWORD: queue
      POSTGRES_DB: queue
    ports:
      - "55432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
```

## Розробка

- основна логіка бота знаходиться в `app/`;
- middleware-логування — в `middleware/mid_logging.py`;
- конфігурація через `app/config.py` та `.env`;
- база даних ініціалізується під час запуску через `init_db()`.

## Ліцензія

Проєкт використовується в навчальних/внутрішніх цілях і може бути адаптований під ваші задачі.

## Примітка

README оновлено для відображення поточного стану проекту, включаючи підтримку webhook, PostgreSQL, aiogram 3 та актуальну структуру директорій.
