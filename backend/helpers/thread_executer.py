import asyncio
from concurrent.futures import ThreadPoolExecutor

thread_pool = ThreadPoolExecutor(max_workers=10)


async def execute_in_new_thread(function, *params):
    return await asyncio.get_event_loop().run_in_executor(
        thread_pool, lambda: function(*params)
    )
