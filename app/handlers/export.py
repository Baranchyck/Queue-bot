from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile
from datetime import datetime

from app.services.queue import get_queue, build_xlsx

router = Router()

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