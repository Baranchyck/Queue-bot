# Queue-bot

Telegram-бот для управління чергою на здачу лабораторних/дисциплінарних робіт.  
Підтримує фіксовану кількість місць, запис у конкретну позицію, обмін місцями, можливість випередити іншого користувача, перегляд поточної черги та експорт результатів у Excel.

## Основні можливості

- фіксована кількість слотів у черзі;
- запис користувача на конкретне місце;
- обмін місцями між учасниками;
- можливість "пустити людину попереду";
- перегляд поточного стану черги;
- швидка перевірка черги у Telegram;
- експорт даних у Excel;
- робота з PostgreSQL через SQLAlchemy;
- запуск у Docker для локального середовища.

## Технології

- Python 3
- aiogram
- SQLAlchemy (asyncio)
- PostgreSQL
- Docker / Docker Compose
- openpyxl для експорту Excel

## Архітектура проекту

```text
Queue-bot/
├── app/
│   ├── config.py
│   ├── main.py
│   ├── db/
│   ├── handlers/
│   ├── keyboards/
│   └── services/
├── .env.example
├── .gitignore
├── docker-compose.yml
├── requirements.txt
├── test_queue.py
└── README.md
```

## Локальний запуск

```bash
cp .env.example .env        # вписати BOT_TOKEN
docker compose up -d db
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m app.main
```
