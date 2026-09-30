import asyncio
from app.services.ser_queue import create_queue, get_queue

async def main():
    await create_queue(1, 10, "test")
    await create_queue(1, 10, "test2")   # другий виклик не має впасти
    queue, slots = await get_queue(1)
    print(queue.title, len(slots), slots[0].position, slots[-1].position)

asyncio.run(main())