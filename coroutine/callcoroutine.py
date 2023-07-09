import asyncio
import time

from tornado.ioloop import IOLoop


async def compute(x: int, y: int):
    # CPU密集型计算
    print(f"computing {x}/{y}...")
    return x / y


async def block(x: int, y: int):
    print(f"blocking {x}/{y}...")
    await asyncio.sleep(0.001)
    return x / y


async def good_call():
    result = await compute(1, 1)
    print("good_call result:", result)


if __name__ == '__main__':
    # 使用asyncio.run执行协程完毕后它将会关闭主事件循环
    asyncio.run(compute(1, 100))

    asyncio.set_event_loop(asyncio.new_event_loop())
    # Event Loop调用计算密集型协程
    asyncio.get_event_loop().run_until_complete(compute(1, 2))

    # 忽略返回值调用协程
    IOLoop.current().spawn_callback(compute, 1, 3)
    IOLoop.current().spawn_callback(good_call)

    asyncio.get_event_loop().create_task(good_call(), name='blocking')
    asyncio.get_event_loop().create_task(block(1, 4), name='blocking')
    asyncio.get_event_loop().create_task(compute(1, 5), name='computing')

    asyncio.get_event_loop().run_forever()
