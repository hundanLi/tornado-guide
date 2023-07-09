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
