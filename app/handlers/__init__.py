from aiogram import Router

from . import start, queue, swap, export


def get_root_router() -> Router:
    root = Router()
    root.include_router(start.router)
    root.include_router(queue.router)
    root.include_router(swap.router)
    root.include_router(export.router)
    return root