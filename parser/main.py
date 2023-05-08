import asyncio


import os
import sys
PROJECT_ROOT = os.path.abspath(os.path.join(
                  os.path.dirname(__file__), 
                  os.pardir)
)

sys.path.append(PROJECT_ROOT)


from database.crud import *
from parser import *

logging.basicConfig(level=logging.INFO)

async def main():
    tasks = set()
    task1 = asyncio.create_task(get_lesilla())
    tasks.add(task1)
    task2 = asyncio.create_task(get_valentino())
    tasks.add(task2)
    task3 = asyncio.create_task(get_nike())
    tasks.add(task3)
    task4 = asyncio.create_task(get_golcegabbana())
    tasks.add(task4)
    L = await asyncio.gather(*tasks)
    await asyncio.sleep(10)

if __name__ == '__main__':
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:  # 'RuntimeError: There is no current event loop...'
        loop = None

    if loop and loop.is_running():
        print('Async event loop already running. Adding coroutine to the event loop.')
        tsk = loop.create_task(main())
    else:
        print('Starting new event loop')
        result = asyncio.run(main())
