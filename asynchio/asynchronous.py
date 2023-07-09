from tornado.httpclient import AsyncHTTPClient
import asyncio


async def asynchronous_fetch(url) -> bytes:
    http_client = AsyncHTTPClient()
    response = await http_client.fetch(url)
    print("do something when waiting response...")
    return response.body


if __name__ == '__main__':
    body = asyncio.run(asynchronous_fetch("http://127.0.0.1:8888"))
    print(body)
