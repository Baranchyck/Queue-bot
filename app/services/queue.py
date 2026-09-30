from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

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

async def join_queue(chat_id: int, user_id: int, name: str, pos: int) -> str:
    data = await get_queue(chat_id)
    if data is None:
        return "Черги немає, створи через /create"
    queue, _ = data
    async with SessionLocal() as session:
        try:
            result = await session.execute(
                update(Slot)
                .where(
                    Slot.queue_id == queue.id,
                    Slot.position == pos,
                    Slot.user_id.is_(None),
                )
                .values(user_id=user_id, user_name=name)
            )
            await session.commit()
        except IntegrityError:
            await session.rollback()
            return "Ти вже стоїш у черзі"

    if result.rowcount == 0: # type: ignore
        return "Це місце зайняте (або такого немає)"
    return f"Записав на місце {pos}"

async def leave_queue(chat_id: int, user_id: int) -> str:
    data = await get_queue(chat_id)
    if data is None:
        return "Черги немає, створи через /create"
    queue, _ = data

    async with SessionLocal() as session:
        result = await session.execute(
            update(Slot)
            .where(Slot.queue_id == queue.id, Slot.user_id == user_id)
            .values(user_id=None, user_name=None)
        )
        await session.commit()

    if result.rowcount == 0:  # type: ignore
        return "Ти й так не стоїш у черзі"
    return "Тебе видалено з черги"