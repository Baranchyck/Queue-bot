from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from app.commands import COMMANDS

router = Router()

@router.message(CommandStart())
async def start(message: types.Message):
    await message.answer("Привіт! Я бот для черги на здачу лаб.\n"
                         'Щоб почати — /help')

@router.message(Command('help'))
async def help(message: types.Message):
    text = f"\n".join(f"{i}. <code>{cmd.command}</code> — {cmd.description}" for i, cmd in enumerate(COMMANDS, 1))
    await message.answer(f'Команди: \n' \
                         f'{text}', parse_mode="HTML")    