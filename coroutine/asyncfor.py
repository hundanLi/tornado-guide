import asyncio


async def my_coroutine():
    await asyncio.sleep(1)  # 模拟一个异步操作
    yield "Hello"
    await asyncio.sleep(1)  # 模拟一个异步操作
    yield "World"


async def main():
    # 创建一个异步可迭代对象
    async for item in my_coroutine():
        print(item)


if __name__ == '__main__':
    # 运行主协程
    asyncio.run(main())
