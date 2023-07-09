from tornado.httpclient import AsyncHTTPClient


# 定义协程
async def fetch_coroutine(url):
    http_client = AsyncHTTPClient()
    response = await http_client.fetch(url)
    return response.body
