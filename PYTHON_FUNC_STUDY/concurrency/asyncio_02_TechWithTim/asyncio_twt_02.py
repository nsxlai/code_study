# source: Tech with Tim Youtube video
import asyncio


async def fetch_data():
    print('start fetching')
    await asyncio.sleep(2)
    print('done fetching')
    return {'data': 1}


async def print_numbers():
    for i in range(10):
        print(i)
        await asyncio.sleep(0.25)


async def main():
    task1 = asyncio.create_task(fetch_data())  # create task adds the function in the event loop, but not starting it.
    task2 = asyncio.create_task(print_numbers())
    value = await task1  # await start the function
    print(value)
    # without await task2, as soon task1 is done, the program will terminate. task 2 will missing print '9'
    await task2


if __name__ == '__main__':
    asyncio.run(main())
