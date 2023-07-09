from tornado import gen
import asyncio
import time


async def minute_loop():
    while True:
        print(f"executing task in {time.asctime()}")
        await execute()
        await gen.sleep(60)


async def execute():
    await gen.sleep(1)


async def accurate_min_loop():
    while True:
        # 开始计时
        nxt = gen.sleep(60)
        print(f"executing accurate task in {time.asctime()}")
        await execute()
        # 等待时钟
        await nxt


if __name__ == '__main__':
    asyncio.get_event_loop().create_task(minute_loop())
    asyncio.get_event_loop().create_task(accurate_min_loop())
    asyncio.get_event_loop().run_forever()
