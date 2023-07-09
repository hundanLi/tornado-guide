import asyncio
import multiprocessing
from typing import Optional, Awaitable
import concurrent.futures
import tornado


def current_process():
    process_name = multiprocessing.current_process().name
    pid = multiprocessing.current_process().pid
    return f"{process_name}-{pid}"


def compute():
    print(f"computing on process: {current_process()}")
    return sum(i * i for i in range(10 ** 7))


class AsyncHandler(tornado.web.RequestHandler):
    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass

    async def get(self):
        await asyncio.get_event_loop().run_in_executor(process_pool, compute)
        self.write("Hello, world\n")


class MultiThreadHandler(tornado.web.RequestHandler):
    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass

    async def get(self):
        await asyncio.get_event_loop().run_in_executor(thread_pool, compute)
        self.write("Hello, world\n")


class SyncHandler(tornado.web.RequestHandler):
    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass

    def get(self):
        compute()
        self.write("Hello, world\n")


def make_app():
    return tornado.web.Application([
        (r"/async/process", AsyncHandler),
        (r"/sync", SyncHandler),
        (r"/async/thread", MultiThreadHandler),
    ])


async def main():
    app = make_app()
    app.listen(8888)
    shutdown_event = asyncio.Event()
    await shutdown_event.wait()


if __name__ == "__main__":
    process_pool = concurrent.futures.ProcessPoolExecutor(max_workers=4)
    thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=4)
    asyncio.run(main())
