import websockets
import asyncio

async def listenServer():
    url = "ws://localhost:8111"

    async with websockets.connect(url) as websocket:
        while True:
            msg = await websocket.recv()
            print(msg)

asyncio.get_event_loop().run_until_complete(listenServer())