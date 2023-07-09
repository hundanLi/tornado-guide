import functools

from tornado.httpclient import AsyncHTTPClient
from tornado import gen
from tornado.ioloop import Future, IOLoop


@gen.coroutine
def async_fetch_gen(url):
    http_client = AsyncHTTPClient()
    response = yield http_client.fetch(url)
    print("do something when waiting response...")
    raise gen.Return(response.body)


def callback(f: Future):
    print(f"result: {f.result()}")


if __name__ == '__main__':
    body = IOLoop.current().run_sync(func=functools.partial(async_fetch_gen, "http://127.0.0.1:8888"))
    print(body)

