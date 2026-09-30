from html import escape

from datetime import datetime

from aiogram import F, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import CallbackQuery, Message, BufferedInputFile

from app.keyboards.swap import swap_kb
from app.services.queue import prepare_swap, swap_slots

from app.services.queue import create_queue, get_queue, join_queue, leave_queue, prepare_swap, swap_slots, build_xlsx

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

@router.message(Command('join_queue'))
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

@router.message(Command('leave_queue'))
async def cmd_leave_queue(message: Message):
    reply = await leave_queue(
        chat_id=message.chat.id,
        user_id=message.from_user.id,
    )
    await message.answer(reply)

@router.message(Command('swap'))
async def cmd_swap(message: Message):
    try:
        pos = int(message.text.split()[1])
    except (ValueError, IndexError):
        await message.answer('Вкажи номер місця, наприклад /swap 5')
        return

    error, pair = await prepare_swap(message.chat.id, message.from_user.id, pos)
    if error:
        await message.answer(error)
        return

    me, target = pair
    await message.answer(
        f'{target.user_name}, {me.user_name} (місце {me.position}) '
        f'пропонує помінятись з твоїм місцем {target.position}. Погоджуєшся?',
        reply_markup=swap_kb(me.user_id, me.position, target.user_id, target.position),
    )


@router.callback_query(F.data.startswith('swap_'))
async def cb_swap(callback: CallbackQuery):
    action, *rest = callback.data.split(':')
    from_user, from_pos, to_user, to_pos = map(int, rest)

    if callback.from_user.id != to_user:
        await callback.answer('Цей запит не для тебе', show_alert=True)
        return

    if action == 'swap_no':
        text = 'Обмін відхилено'
    else:
        text = await swap_slots(
            callback.message.chat.id, from_user, from_pos, to_user, to_pos
        )

    await callback.message.edit_text(text) 
    await callback.answer()  

@router.message(Command('export'))
async def cmd_export(message: Message):
    data = await get_queue(message.chat.id)
    if data is None:
        await message.answer('Черги немає, створи через /create')
        return

    queue, slots = data
    file = BufferedInputFile(
        build_xlsx(slots),
        filename=f'queue_{datetime.now():%Y-%m-%d}.xlsx',
    )
    await message.answer_document(file, caption=queue.title)