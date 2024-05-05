"""
source: Tech with Tim Youtube video
Whenever we create an asynchronous function, we also need to define async event-loop
"""
import asyncio


async def main():
    """ Turn this main func into coroutine by adding async keyword """
    print('About to start')
    # await foo('executing...')  # await will block the execution of the next line
    task1 = asyncio.create_task((foo('Executing...')))
    # await task1
    await asyncio.sleep(0.5)
    print('Finished!')


async def foo(text: str):
    print(text)
    await asyncio.sleep(3)  # await keyword can only exist inside a coroutine (inside the async function)


if __name__ == '__main__':
    asyncio.run(main())
