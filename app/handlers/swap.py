from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from app.keyboards.swap import swap_kb
from app.services.queue import prepare_swap, swap_slots

router = Router()

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