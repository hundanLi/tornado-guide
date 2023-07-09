import threading

from tornado.httpclient import HTTPClient
from tornado import gen
import asyncio


def current_thread():
    name = threading.current_thread().name
    thread_id = threading.current_thread().ident
    return f"{name}-{thread_id}"


def synchronous_fetch(url) -> bytes:
    print(f"{current_thread()} sync fetch starting")
    http_client = HTTPClient()
    response = http_client.fetch(url)
    print(f"{current_thread()} sync fetch finished")
    return response.body


async def coroutine():
    print('coroutine starting')
    await gen.sleep(1)
    print('coroutine finished')


if __name__ == '__main__':
    # body = synchronous_fetch("http://127.0.0.1:8888")
    # print(body)
    loop = asyncio.get_event_loop()

    loop.run_in_executor(None, synchronous_fetch, "http://127.0.0.1:8888/sync")
    loop.create_task(coroutine())
    loop.run_forever()


