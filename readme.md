# Tornado开发指南

## 0.背景

### 0.1为什么使用Tornado?

在AI日渐火热的趋势下，人人都有自己构建AI服务的冲动，而构建AI服务无疑会使用到python和深度学习框架，很多开源的AI模型都是使用python实现，并且大多使用pytorch，tensorflow这种提供python接口的框架来实现、训练神经网络以及进行模型推理。但是这还不具备对外提供服务的能力，因为在互联网时代，用户往往都是通过网络请求来获取AI服务，或通过HTTP，或通过GRPC等协议。因此需要在深度学习框架推理的基础上封装一层Web服务，向用户提供AI服务。而Tornado就是一个基于python的异步web框架，相比于流行的Django框架，它简洁易用；而对比Flask框架，它提供了良好的异步支持，性能良好。



## 1.快速入门

### 1.1准备环境

#### 1.1.1安装miniconda

本文基于Windows WSL2系统环境，系统版本为ubuntu18.04。

你可以使用python3 venv模块创建，这里推荐使用miniconda来管理虚拟环境。你可以到[官方下载页面](https://docs.conda.io/en/latest/miniconda.html)下载安装脚本。

```bash
curl -o install.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash install.sh
```

安装过程中你可以自定义安装目录。安装完成后可以还做一些个性化设置，如设置进入Bash环境不激活conda基础环境`~/.condarc`:

```yaml
auto_activate_base: false
```



#### 1.1.2创建虚拟环境

安装完成后重新打开Bash终端，创建一个虚拟环境：

```bash
conda create -n tornado python=3.9
```

这会创建一个名称为tornado的虚拟环境，并且python版本为3.9。

默认情况下虚拟环境所有的文件会被放在conda安装目录下的envs子目录下，你可以通过env list命令查看所有环境：

```bash
conda env list
```

激活环境：

```bash
conda activate tornado
```



#### 1.1.3安装依赖库

毫无疑问需要安装Tornado库：

```bash
pip install tornado==6.3.1
```



### 1.2第一个web程序

按照coding界的惯例，首先来一个Hello world示例：

编写以下代码：

```python
import asyncio
import tornado

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

async def main():
    app = make_app()
    app.listen(8888)
    shutdown_event = asyncio.Event()
    await shutdown_event.wait()

if __name__ == "__main__":
    asyncio.run(main())
```

保存为app.py文件中。

启动服务：

```bash
python app.py
```

然后使用curl程序验证服务是否正常：

```bash
curl http://127.0.0.1:8888
```

恭喜你，完成了Tornado的第一个web程序！

#### 1.2.1Main协程

启动一个Tornado服务的方法是调用 [`asyncio.run`](https://docs.python.org/3/library/asyncio-runner.html#asyncio.run) 函数创建一个main协程，它初始化服务，并且等待asyncio.Event()事件，因为该事件的set()函数不会被调用，这样web服务将可以永久执行，当然你也可以手动调用set()函数终止程序运行作为优雅关闭的一部分。

#### 1.2.2Applicaton对象

Application对象负责全局配置，包括路由表：映射请求到请求处理器。

路由表中包含一个个元组（URLSpec对象），元组中可含有正则格式的路径，RequestHandler类，以及用于初始化RequestHandler对象的Dict对象，以及路由名称。

```python
class MainHandler(RequestHandler):
    def get(self):
        self.write('<a href="%s">link to story 1</a>' %
                   self.reverse_url("story", "1"))

class StoryHandler(RequestHandler):
    def initialize(self, db):
        self.db = db

    def get(self, story_id):
        self.write("this is story %s" % story_id)

app = Application([
    url(r"/", MainHandler),
    url(r"/story/([0-9]+)", StoryHandler, dict(db=db), name="story")
    ])
```



#### 1.2.3RequestHandler类

一般情况下，请求最终都会由RequestHandler的子类去处理，对于每种HTTP请求方法，RequestHandler类中都定义了对应的同名方法，如get()，post()，分别用于处理请求。你可以调用render()或者write()方法向客户端写回响应。render()会加载模板并填充参数，而write()可以写入字节，字符串，Dict对象（序列化成JSON字符串）。

#### 1.2.4处理请求数据

在RequestHandler中，你可以通过访问self.request对象（HTTPServerRequest类）获取当前请求的信息，如请求头，请求体等内容。

对于表单参数，你可以通过self.request的get_query_argument()方法获取查询参数，调用get_body_argument()方法获取表单参数。

对于文件上传请求，如果content-type=multipart/form-data，那么可以通过self.request.files字典对象中，其中key表示`<input type="file" name="filename">` 表单字段中的name属性，value表示对应的文件列表；否则，原始的上传数据可以从self.request.body中获取。

默认请求下，文件会全部缓存在内存中，如果处理大文件，你需要使用 `stream_request_body` 装饰器。

Tornado框架不会解析请求体为JSON串，如果你想接收JSON，需要自己解析，你可以在prepare方法中统一处理：

```python
def prepare(self):
    if self.request.headers.get("Content-Type", "").startswith("application/json"):
        self.json_args = json.loads(self.request.body)
    else:
        self.json_args = None
```

#### 1.2.5覆写RequestHandler的方法

除了get(),post()方法之外，你还可以覆盖其他方法。对于每个请求，RequestHandler中的每个方法都会按照以下顺序被执行：

1. 当一个请求进来时，新的RequestHandler对象被创建
2. 传入Application配置的初始化参数调用initialize()方法
3. 调用prepare()方法，可以调用finish()或者redirect()结束请求
4. 调用get()，post()或者put()方法
5. 调用on_finish()方法

RequestHandler中可以被覆盖的一些通用方法包括：

- write_error: 输出错误页面
- on_connection_close: 当客户端断开连接时被调用
- get_current_user: 获取用户信息
- get_user_locale: 返回Locale对象
- set_default_headers: 用于给响应中设置额外的响应头



#### 1.2.6错误处理

如果RequestHandler中发生异常，那么Tornado会调用write_error方法生成异常页面，默认情况下会返回500错误码。

#### 1.2.7重定向

有两种方法可以重定向用户请求：RequestHandler.redirect() 方法或者 RedirectHandler类。

在RequestHandler中，你可以调用self.redirect()方法中重定向到任意地方。而RediretHandler类，则要在Application路由表中配置：

```python
app = tornado.web.Application([
    url(r"/app", tornado.web.RedirectHandler,
        dict(url="http://itunes.apple.com/my-app-id")),
    ])
```

你可以配置重定向url为绝对或者相对路径。



#### 1.2.8异步处理器

某些Handler方法（prepare,get,post）可以被重写为协程使得Handler异步化。

以下是使用协程的例子：

```python
class MainHandler(tornado.web.RequestHandler):
    async def get(self):
        http = tornado.httpclient.AsyncHTTPClient()
        response = await http.fetch("http://friendfeed-api.com/v2/feed/bret")
        json = tornado.escape.json_decode(response.body)
        self.write("Fetched " + str(len(json["entries"])) + " entries "
                   "from the FriendFeed API")
```



参考资料：[Tornado Guide](https://www.tornadoweb.org/en/stable/guide/structure.html)



## 2.异步非阻塞IO

实时Web应用的特性是每个用户持有一个长期处于空闲状态的连接。在传统的同步web服务器中，意味着需要为每个用户分配一个线程处理请求，这是一项非常昂贵的资源消耗。

为了最小化并发连接的成本，Tornado使用单线程事件轮询，这意味着应用程序代码都应该设计为异步和非阻塞的，因为某一时刻只能有一个操作处于活跃状态。

### 2.1阻塞IO

当函数需要等待某件事情发生才能返回时，那么它就是阻塞的。一个函数可能因为很多原因阻塞，如：网络IO，磁盘IO，互斥等等。严格意义上，所有函数都会阻塞，因为它至少会占用CPU时间片执行代码指令，比如使用bcrypt算法对密码进行加密时，耗时将会比较长。

一个函数可以在某些方面时阻塞的，而在其他方面时非阻塞的，在Tornado中，通常说的是网络IO阻塞。

以下是一个阻塞函数的例子：

```python
from tornado.httpclient import HTTPClient


def synchronous_fetch(url) -> bytes:
    http_client = HTTPClient()
    response = http_client.fetch(url)
    return response.body


if __name__ == '__main__':
    body = synchronous_fetch("http://127.0.0.1:8888")
    print(body)

```



### 2.2异步IO

异步函数是在完成工作之前就返回，并且通常会导致在触发应用程序中的某个未来操作之前在后台执行一些工作。

异步接口有多种风格：

- 回调参数
- 返回占位符（Future、Promise、Deferred）
- 传送到队列
- 回调注册表（例如 POSIX 信号）

Tornado中的异步操作通常会返回Future，例外的是IOLoop使用回调函数。可以使用await或yield关键字从Future中获取结果。

以下是使用协程将阻塞函数改写为异步的形式：

```python
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

```

如果需要兼容旧版本的python，可以使用tornado.gen模块：

```python
import functools

from tornado.httpclient import AsyncHTTPClient
from tornado import gen
from tornado.ioloop import IOLoop


@gen.coroutine
def async_fetch_gen(url):
    http_client = AsyncHTTPClient()
    response = yield http_client.fetch(url)
    print("do something when waiting response...")
    raise gen.Return(response.body)


if __name__ == '__main__':
    body = IOLoop.current().run_sync(func=functools.partial(async_fetch_gen, "http://127.0.0.1:8888"))
    print(body)

```

你可能觉得协程看起来有点魔幻，但是你可以内部实现视为如下过程：

```python
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

```



## 3.协程Coroutines

Tornado中推荐使用协程的方式编写异步代码。

Python3.5引进了async和await关键字，可以使用 `async` 关键字定义协程，以及`await` 关键字暂停协程或者恢复执行协程。

### 3.1定义协程

以下是定义协程的示例：

```python
from tornado.httpclient import AsyncHTTPClient


# 定义协程
async def fetch_coroutine(url):
    http_client = AsyncHTTPClient()
    response = await http_client.fetch(url)
    return response.body

```

如果需要兼容旧版本的Python，那么你可以借助 [`tornado.gen.coroutine`](https://www.tornadoweb.org/en/stable/gen.html#tornado.gen.coroutine) 装饰器来使用基于yield的装饰协程。

两种形式可以等价转换，如下所示：

```python
# Decorated:                    # Native:

# Normal function declaration
# with decorator                # "async def" keywords
@gen.coroutine
def a():                        async def a():
    # "yield" all async funcs       # "await" all async funcs
    b = yield c()                   b = await c()
    # "return" and "yield"
    # cannot be mixed in
    # Python 2, so raise a
    # special exception.            # Return normally
    raise gen.Return(b)             return b
```



### 3.2调用协程

几乎在所有情况下，任何调用协程的函数本身都必须是协程，并在调用中使用await 或yield 关键字。*存疑：值得注意的是，只有当await或者yield出现时，协程才会执行，否则永远不会执行。*

以下是调用协程的例子：

```python
async def compute(x: int, y: int):
    # CPU密集型计算
    print(f"computing {x}/{y}...")
    return x / y


async def block(x: int, y: int):
    print(f"blocking {x}/{y}...")
    await asyncio.sleep(0.001)
    return x / y

# 在另一个协程中调用block协程
async def good_call():
    result = await block(1, 2)
    print("result:", result)

```

如何驱动协程执行呢，你可以使用asyncio库：

**asyncio.run()**

```python
if __name__ == '__main__':
    # 使用asyncio.run执行协程完毕后它将会关闭主事件循环
    asyncio.run(good_call())
```

这里需要注意的是，使用asyncio.run调用协程执行完毕后，它将会关闭主事件循环，所以后续如果再使用`asyncio.get_event_loop()` 调用协程将会出现异常：

```bash
RuntimeError: There is no current event loop in thread 'MainThread'.
```

由于这个原因，asyncio.run()函数一般用于执行程序的main函数（协程）。



**asyncio.get_event_loop().create_task()**

除了run函数之外，还可以使用主事件循环的create_task()函数来调度协程执行：

```python
if __name__ == '__main__':
    # 可以手动新建事件循环
    asyncio.set_event_loop(asyncio.new_event_loop())
    asyncio.get_event_loop().create_task(good_call(), name='blocking')
    asyncio.get_event_loop().create_task(block(1, 4), name='blocking')
    asyncio.get_event_loop().create_task(compute(1, 5), name='computing')
```

值得一提的是，无论是CPU密集型计算，还是阻塞型IO操作，都可以使用这种方式调度协程来执行任务，当然也可以在线程池中执行。

当然，对于CPU密集型计算的协程（即没有await的协程）在执行过程中不会让出CPU给其他协程使用，实际上可以使用同步函数。



### 3.3线程/进程池

默认情况下，Tornado使用单线程进行事件轮询和协程执行任务，但是有些情况下阻塞函数无法直接改写为异步函数，并且不希望这个函数调用阻塞主线程的时候，可以使用线程池来执行阻塞函数，并且可以封装为协程：

```python
async def call_blocking():
    await asyncio.get_running_loop().run_in_executor(None, blocking_func, args)
```

以下是一个完成的例子：

```python
import asyncio
import concurrent.futures
import time
import threading
import multiprocessing


def current_thread():
    name = threading.current_thread().name
    thread_id = threading.current_thread().ident
    return f"{name}-{thread_id}"


def current_process():
    process_name = multiprocessing.current_process().name
    pid = multiprocessing.current_process().pid
    return f"{process_name}-{pid}"


def blocking_io():
    # File operations (such as logging) can block the
    # event loop: run them in a thread pool.
    time.sleep(5)
    print("blocking-io: ", current_thread())
    with open('/dev/urandom', 'rb') as f:
        return f.read(100)


def cpu_bound():
    # CPU-bound operations will block the event loop:
    # in general it is preferable to run them in a
    # process pool.
    print("cpu-bound: ", current_thread())
    return sum(i * i for i in range(10 ** 7))


async def main():
    loop = asyncio.get_running_loop()

    # Tips: directly call blocking function will cause the MainThread blocking,
    #  so that the other coroutine on MainThread also blocking
    blocking_io()

    # TIPS: if running in executor, the current coroutine is hangup and then
    #  yield cpu to other coroutine on the MainThread
    # Options:

    # 1. Run in the default loop's executor:
    result = await loop.run_in_executor(
        None, blocking_io)
    print('default thread pool', current_thread())

    # 2. Run in a custom thread pool:
    with concurrent.futures.ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(
            pool, blocking_io)
        print('custom thread pool: ', current_thread())

    print("custom thread pool finish: ", current_thread())

    # 3. Run in a custom process pool:
    with concurrent.futures.ProcessPoolExecutor() as pool:
        result = await loop.run_in_executor(
            pool, cpu_bound)
        print('custom process pool', current_thread())


async def secondary():
    await asyncio.sleep(0.1)
    print("secondary hello: ", current_thread())


if __name__ == '__main__':
    asyncio.gather(main(), secondary())
    asyncio.get_event_loop().run_forever()
    print("main: hello")

```

最佳实践总结为如下几点：

- 阻塞式IO：无法改写为异步时，使用await和线程池，这样才不会阻塞主线程
- CPU计算：使用await和进程池，这样就不会阻塞主进程，并且可以利用多核CPU的能力，免受GIL锁的限制



### 3.4并行化等待

有时候可能一个操作依赖于多个任务完成后方能继续进行，这种情况下可以使用 tornado.gen.multi 函数和await关键字进行并行化等待。multi函数的参数可以是list或者dict对象。

示例如下：

```python
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


```



### 3.5定时任务

对于后台执行的定时任务，可以使用协程，并配合while True循环和tornado.gen.sleep()函数实现：

```python

async def minute_loop():
    while True:
        print(f"executing task in {time.asctime()}")
        await execute()
        await gen.sleep(60)

```

这个例子中，实际的任务执行周期是（60+N）秒，N代表任务执行耗时。

如果要精确控制执行周期为60秒，那么需要配合交错模式使用，这使得我们可以不用立即让出CPU，而是先完成其他事情：

```python

async def accurate_min_loop():
    while True:
        # 开始计时
        nxt = gen.sleep(60)
        print(f"executing accurate task in {time.asctime()}")
        await execute()
        # 等待时钟
        await nxt
```

完整的示例如下：

```python
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

```



### 3.6异步循环

在异步生成器的场景中，可以使用async for来迭代遍历获取异步生成器的结果。如下所示：

```python
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

```

