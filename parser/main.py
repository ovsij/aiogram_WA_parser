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
        #await get_lesilla()
        #await get_valentino()
        #await get_nike()
        #await get_nike_outlet()
        #await get_golcegabbana()
        #await get_coach()
    while True:
        tasks = set()
        #task1 = asyncio.create_task(get_lesilla())
        #tasks.add(task1)
        #task2 = asyncio.create_task(get_valentino())
        #tasks.add(task2)
        #task3 = asyncio.create_task(get_nike())
        #tasks.add(task3)
        #task4 = asyncio.create_task(get_nike())
        #tasks.add(task4)
        #task5 = asyncio.create_task(get_golcegabbana())
        #tasks.add(task5)
        #task6 = asyncio.create_task(get_coach())
        #tasks.add(task6)
        #task7 = asyncio.create_task(get_asics())
        #tasks.add(task7)
        #task8 = asyncio.create_task(get_newbalance())
        #tasks.add(task8)
        #task9 = asyncio.create_task(get_underarmour())
        #tasks.add(task9)
        #task10 = asyncio.create_task(get_pleinoutlet())
        #tasks.add(task10)
        #task11 = asyncio.create_task(get_monnalisa())
        #tasks.add(task11)
        #task12 = asyncio.create_task(get_zwilling())
        #tasks.add(task12)
        #task13 = asyncio.create_task(get_twinset())
        #tasks.add(task13)
        #task14 = asyncio.create_task(get_hellyhansen())
        #tasks.add(task14)
        #task15 = asyncio.create_task(get_wolford())
        #tasks.add(task15)
        task16 = asyncio.create_task(get_odlo())
        tasks.add(task16)
        task17 = asyncio.create_task(get_villeroyboch())
        tasks.add(task17)
        
        
        L = await asyncio.gather(*tasks)
        await asyncio.sleep(10)
    #except Exception as ex:
    #    print(ex)

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
