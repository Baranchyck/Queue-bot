# Queue-bot

Telegram-бот для черги на здачу лабораторних.

## Локальний запуск

```bash
cp .env.example .env        # вписати BOT_TOKEN
docker compose up -d db
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m app.main
```
