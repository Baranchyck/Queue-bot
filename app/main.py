import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from app.config import settings
from app.handlers import get_root_router

from app.db.base import init_db

log = logging.getLogger(__name__)


def build() -> tuple[Bot, Dispatcher]:
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    dp = Dispatcher()
    dp.include_router(get_root_router())
    
    return bot, dp

async def run_polling() -> None:
    bot, dp = build()
    await init_db() 
    await bot.delete_webhook(drop_pending_updates=True)
    log.info("Starting in polling mode")
    await dp.start_polling(bot)

def run_webhook() -> None:
    bot, dp = build()
    webhook_full_url = settings.WEBHOOK_URL.rstrip("/") + settings.WEBHOOK_PATH

    async def on_startup(bot: Bot) -> None:
        await init_db() 
        await bot.set_webhook(
            webhook_full_url,
            secret_token=settings.WEBHOOK_SECRET,
            drop_pending_updates=True,
        )
        log.info("Webhook set: %s", webhook_full_url)

    async def health(_: web.Request) -> web.Response:
        # Для health-check Render і для зовнішнього пінгера (проти засинання).
        return web.Response(text="ok")

    dp.startup.register(on_startup)

    app = web.Application()
    app.router.add_get("/", health)
    SimpleRequestHandler(
        dispatcher=dp, bot=bot, secret_token=settings.WEBHOOK_SECRET
    ).register(app, path=settings.WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    web.run_app(app, host=settings.HOST, port=settings.PORT)

def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    if settings.MODE == "webhook":
        run_webhook()
    else:
        asyncio.run(run_polling())

if __name__ == "__main__":
    main()
