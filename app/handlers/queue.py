from html import escape

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from app.services.ser_queue import create_queue, get_queue, join_queue, leave_queue

router = Router()

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

@router.message(Command('join'))
async def cmd_join_queue(message: Message):
    try:
        position = int(message.text.split()[1])
    except (ValueError, IndexError):
        await message.answer('Вкажи коректний номер позиції, наприклад /join_queue 5')
        return

    reply = await join_queue(
        chat_id=message.chat.id,
        user_id=message.from_user.id,
        name=message.from_user.first_name,
        pos=position,
    )
    await message.answer(reply)

@router.message(Command('leave'))
async def cmd_leave_queue(message: Message):
    reply = await leave_queue(
        chat_id=message.chat.id,
        user_id=message.from_user.id,
    )
    await message.answer(reply)

