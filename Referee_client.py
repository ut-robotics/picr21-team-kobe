import asyncio
import websockets
import json


class Client:

    def __init__(self):
        f = open('websocket_config.json', "r")
        websocket_config = json.loads(f.read())
        self.host = websocket_config['host']
        self.port = websocket_config['port']
        self.robot_id = "Kobe"

    async def send(self):
        print("Connecting to Server " + str(self.host) + " on port " + str(self.port))
        uri = "ws://" + str(self.host) + ":" + str(self.port)
        async with websockets.connect(uri) as ws:
            while True:
                cmd = int(input("Enter a command: 1, 2, 3 or 4 \n 1 - signal: start, target: blue\n "
                                "2 - signal: start, target: magenta \n 3 - signal: stop \n 4 - Change ID"))
                if cmd == 1:
                    msg = {
                        "signal": "start",
                        "basketTarget": "blue",
                        "robot_id": self.robot_id
                    }
                elif cmd == 2:
                    msg = {
                        "signal": "start",
                        "basketTarget": "magenta",
                        "robot_id": self.robot_id
                    }
                elif cmd == 3:
                    msg = {
                        "signal": "stop",
                        "robot_id": self.robot_id
                    }
                elif cmd == 4:
                    self.robot_id = ""
                    while self.robot_id == "":
                        self.robot_id = str(input("Enter an ID..."))
                    msg = {
                        "signal": "changeID",
                        "robot_id": self.robot_id,
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
