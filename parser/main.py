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


async def main():
    while True:
        tasks = set()
        #task1 = asyncio.create_task(get_lesilla())
        #tasks.add(task1)
        task2 = asyncio.create_task(get_valentino())
        tasks.add(task2)
        #task3 = asyncio.create_task(get_nike())
        #tasks.add(task3)
        L = await asyncio.gather(*tasks)
        await asyncio.sleep(600)
        

if __name__ == '__main__':
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:  # 'RuntimeError: There is no current event loop...'
        loop = None

    if loop and loop.is_running():
        print('Async event loop already running. Adding coroutine to the event loop.')
        tsk = loop.create_task(main())
        # ^-- https://docs.python.org/3/library/asyncio-task.html#task-object
        # Optionally, a callback function can be executed when the coroutine completes
        tsk.add_done_callback(
            lambda t: print(f'Task done with result={t.result()}  << return val of main()'))
    else:
        print('Starting new event loop')
        result = asyncio.run(main())
