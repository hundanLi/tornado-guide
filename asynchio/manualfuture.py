import asyncio

from tornado.concurrent import Future
from tornado.httpclient import AsyncHTTPClient


def async_fetch_manual(url):
    http_client = AsyncHTTPClient()
    my_future = Future()
    fetch_future = http_client.fetch(url)

    def on_fetch(f):
        my_future.set_result(f.result().body)

    fetch_future.add_done_callback(on_fetch)
    print("do something when waiting response...")
    return my_future


def callback(f: Future):
    print("fetch result: %s" % f.result())


if __name__ == '__main__':
    future = async_fetch_manual("http://127.0.0.1:8888")
    future = asyncio.wrap_future(future)
    future.add_done_callback(callback)
    asyncio.get_event_loop().run_until_complete(future)
