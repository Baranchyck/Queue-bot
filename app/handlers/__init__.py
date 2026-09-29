from aiogram import Router

from . import queue


def get_root_router() -> Router:
    root = Router()
    root.include_router(queue.router)
    return root