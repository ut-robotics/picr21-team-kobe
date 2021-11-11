import asyncio
import websockets
import json


class Client:

    def __init__(self):
        f = open('websocket_config.json', "r")
        websocket_config = json.loads(f.read())
        self.host = websocket_config['host']
        self.port = websocket_config['port']

    async def send(self):
        print("Connecting to Server " + str(self.host) + " on port " + str(self.port))
        uri = "ws://" + str(self.host) + ":" + str(self.port)
        async with websockets.connect(uri) as ws:
            while True:
                cmd = int(input("Enter a command: 1, 2 or 3 \n 1 - signal: start, target: blue\n "
                                "2 - signal: start, target: magenta \n 3 - signal: stop"))
                if cmd == 1:
                    msg = {
                        "signal": "start",
                        "basketTarget": "blue",
                    }
                elif cmd == 2:
                    msg = {
                        "signal": "start",
                        "basketTarget": "magenta",
                    }
                elif cmd == 3:
                    msg = {
                        "signal": "stop",
                    }
                else:
                    print("Invalid command.")
                    continue
                await ws.send(json.dumps(msg))
                msg = await ws.recv()
                print(msg)

    def start(self):
        asyncio.get_event_loop().run_until_complete(self.send())


cl = Client()
cl.start()
