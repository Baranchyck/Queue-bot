from sqlalchemy import select, update

from app.db.base import SessionLocal
from app.db.models import Queue, Slot

from app.config import settings 

async def create_queue(chat_id, owner_id, title):
    async with SessionLocal() as session, session.begin():
        await session.execute(
            update(Queue)
            .where(Queue.chat_id == chat_id, Queue.is_active)
            .values(is_active=False)
        )
        queue = Queue(chat_id=chat_id, owner_id=owner_id, title=title)
        session.add(queue)
        await session.flush()

        session.add_all([Slot(queue_id=queue.id, position=n) for n in range(1, settings.SLOTS_COUNT + 1)])
        return queue.id 

async def get_queue(chat_id):
    async with SessionLocal() as session:
        queue = (
            await session.execute(
                select(Queue).where(Queue.chat_id == chat_id, Queue.is_active)
            )
        ).scalar_one_or_none()
        if queue is None:
            return None

        slot = (
            await session.execute(
                select(Slot).where(Slot.queue_id == queue.id).order_by(Slot.position)
            )
        ).scalars().all()
        return queue, list(slot)