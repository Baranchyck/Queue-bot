from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from app.db.base import SessionLocal
from app.db.models import Queue, Slot

from app.config import settings 

from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font

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
    """Сам обмін ПІСЛЯ підтвердження. Усе в одній транзакції."""
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
                .order_by(Slot.position)   # однаковий порядок блокувань, щоб не було deadlock
                .with_for_update()         # ніхто не змінить ці рядки, поки ми не закомітимось
            )
        ).scalars().all()

        by_pos = {s.position: s for s in slots}
        a, b = by_pos.get(from_pos), by_pos.get(to_pos)

        # перевірка, що обидва ДОСІ на своїх місцях
        if a is None or b is None or a.user_id != from_user or b.user_id != to_user:
            return "Черга вже змінилась, обмін скасовано"

        a_uid, a_name = a.user_id, a.user_name
        b_uid, b_name = b.user_id, b.user_name

        # крок 1: звільняємо обидва слоти
        a.user_id = a.user_name = None
        b.user_id = b.user_name = None
        await session.flush()

        # крок 2: записуємо навхрест
        a.user_id, a.user_name = b_uid, b_name
        b.user_id, b.user_name = a_uid, a_name
        await session.commit()

    return f"Готово: {a_name} тепер на місці {to_pos}, {b_name} на місці {from_pos}"

def build_xlsx(slots) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Черга"

    ws.append(["№", "Ім'я", "Telegram ID"])
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    # усі місця, включно з вільними, щоб у таблиці було видно повну чергу
    for s in slots:
        ws.append([s.position, s.user_name or "", s.user_id or ""])

    ws.column_dimensions["A"].width = 6
    ws.column_dimensions["B"].width = 30
    ws.column_dimensions["C"].width = 16

    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()