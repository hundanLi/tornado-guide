import asyncio
from tornado.gen import multi


async def coroutine1():
    await asyncio.sleep(1)
    print("coroutine1 finished ")


async def coroutine2():
    await asyncio.sleep(1.5)
    print("coroutine2 finished ")


async def main():
    await multi([coroutine1(), coroutine2()])
    print("main finished")


if __name__ == '__main__':
    asyncio.run(main())

