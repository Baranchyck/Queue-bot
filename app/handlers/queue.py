from html import escape

from aiogram import Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import Message

from app.services.queue import create_queue, get_queue

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


@router.message(Command("create"))
async def cmd_create(message: Message, command: CommandObject) -> None:
    title = (command.args or "").strip()
    if not title:
        await message.answer("Використання: /create &lt;назва&gt;")
        return
    if len(title) > 200:
        await message.answer("Назва задовга, максимум 200 символів.")
        return
    if message.from_user is None:
        return

    await create_queue(
        chat_id=message.chat.id,
        owner_id=message.from_user.id,
        title=title,
    )
    await message.answer(f"Черга <b>{escape(title)}</b> створена.")


@router.message(Command("queue"))
async def cmd_queue(message: Message) -> None:
    result = await get_queue(message.chat.id)
    if result is None:
        await message.answer("Черги ще нема. Створи її: /create &lt;назва&gt;")
        return

    queue, slots = result
    lines = [
        f"{s.position:>2}. {escape(s.user_name) if s.user_name else '—'}"
        for s in slots
    ]
    await message.answer(
        f"<b>{escape(queue.title)}</b>\n<pre>" + "\n".join(lines) + "</pre>"
    )