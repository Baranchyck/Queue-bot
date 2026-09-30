from sqlalchemy import select

from app.db.base import SessionLocal
from app.db.models import Slot
from app.services.ser_queue import get_queue

async def prepare_swap(chat_id: int, user_id: int, target_pos: int):
    """Перевірка ПЕРЕД відправкою запиту.
    Повертає (помилка, None) або (None, (мій_слот, слот_цілі))."""
    data = await get_queue(chat_id)
    if data is None:
        return "Черги немає, створи через /create", None
    _, slots = data

    me = next((s for s in slots if s.user_id == user_id), None)
    target = next((s for s in slots if s.position == target_pos), None)

    if me is None:
        return "Ти не стоїш у черзі", None
    if target is None:
        return "Такого місця немає", None
    if target.user_id is None:
        return "Це місце вільне, просто зроби /leave_queue і /join_queue", None
    if target.user_id == user_id:
        return "Це твоє місце", None

    return None, (me, target)


async def swap_slots(
    chat_id: int, from_user: int, from_pos: int, to_user: int, to_pos: int
) -> str:
    data = await get_queue(chat_id)
    if data is None:
        return "Черги вже немає"
    queue, _ = data

    async with SessionLocal() as session:
        slots = (
            await session.execute(
                select(Slot)
                .where(
                    Slot.queue_id == queue.id,
                    Slot.position.in_([from_pos, to_pos]),
                )
                .order_by(Slot.position)   
                .with_for_update()         
            )
        ).scalars().all()

        by_pos = {s.position: s for s in slots}
        a, b = by_pos.get(from_pos), by_pos.get(to_pos)

        if a is None or b is None or a.user_id != from_user or b.user_id != to_user:
            return "Черга вже змінилась, обмін скасовано"

        a_uid, a_name = a.user_id, a.user_name
        b_uid, b_name = b.user_id, b.user_name

        a.user_id = a.user_name = None
        b.user_id = b.user_name = None
        await session.flush()

        a.user_id, a.user_name = b_uid, b_name
        b.user_id, b.user_name = a_uid, a_name
        await session.commit()

    return f"Готово: {a_name} тепер на місці {to_pos}, {b_name} на місці {from_pos}"