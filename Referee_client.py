import asyncio
import websockets
import json


class Client:

    def __init__(self):
        f = open('websocket_config.json', "r")
        websocket_config = json.loads(f.read())
        self.host = websocket_config['host']
        self.port = websocket_config['port']
        self.robot = "Kobe"

    async def send(self, ws, path):
        while True:
            cmd = int(input(
                "Enter a command: 1, 2, 3 or 4 \n 1 - signal: start, targets: ['Io', " + self.robot +
                "], baskets: ['magenta', 'blue']\n 2 - signal: start, targets: ['Io', " + self.robot +
                "'], baskets: ['blue', 'magenta'] \n 3 - signal: stop, targets: ['Io', " + self.robot +
                "] \n 4 - Change ID"))
            if cmd == 1:
                msg = {
                    "signal": "start",
                    "targets": ["Io", self.robot],
                    "baskets": ["magenta", "blue"]
                }
            elif cmd == 2:
                msg = {
                    "signal": "start",
                    "targets": ["Io", self.robot],
                    "baskets": ["blue", "magenta"]
                }
            elif cmd == 3:
                msg = {
                    "signal": "stop",
                    "targets": ["Io", self.robot]
                }
            elif cmd == 4:
                self.robot = ""
                while self.robot == "":
                    self.robot = str(input("Enter an ID..."))
                msg = {
                    "signal": "changeID",
                    "robot": self.robot,
                }
            else:
                print("Invalid command.")
                continue
            await ws.send(json.dumps(msg))
            msg = await ws.recv()
            print(msg)

    def start(self):
        loop = asyncio.new_event_loop()
        server = websockets.serve(self.send, self.host, self.port, loop=loop, ping_interval=None, ping_timeout=None)
        loop.run_until_complete(server)
        loop.run_forever()


cl = Client()
cl.start()
