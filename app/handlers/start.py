from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Привіт! Я бот для черги на здачу лаб.\n\n"
        "/create — створити чергу\n"
        "/queue — показати чергу\n"
        "/join — стати на місце\n"
        "/leave — вийти з черги\n"
        "/back — пропустити наступного\n"
        "/swap — помінятись місцями\n"
        "/export — вивантажити в Excel"
    )