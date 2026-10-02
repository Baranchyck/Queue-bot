import logging
from aiogram import BaseMiddleware

logger = logging.getLogger(__name__)

class Logging(BaseMiddleware):
    async def __call__(self, handler, event, data):
        message = event.message
        if message is None:
            return await handler(event, data)

        user_name = message.from_user.username
        id        = message.from_user.id
        text      = message.text if message.text is not None else "[non-text content]"

        logger.info(f'[ User: @{user_name} ({id}): {text} ]')

        return await handler(event, data)