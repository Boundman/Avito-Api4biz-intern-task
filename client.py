import aiohttp
import asyncio


HOST = '127.0.0.1'
PORT = '8000'
METHOD = 'add_company'

NAME = 'Tesla'


async def fetch(session, url):
    param = {'name': NAME}
    async with session.post(url=url, params=param) as response:
        return await response.text()


async def main():
    async with aiohttp.ClientSession() as sess:
        url = 'http://{}:{}/{}'.format(HOST, PORT, METHOD)
        response = await fetch(sess, url)
        print(response)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
