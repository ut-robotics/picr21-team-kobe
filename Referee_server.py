import asyncio
import threading
import websockets
import json


class Server:

    def __init__(self):
        self.run = False
        self.blueIsTarget = True
        self.robot = "Kobe"
        f = open('websocket_config.json', "r")
        websocket_config = json.loads(f.read())
        self.host = websocket_config['host']
        self.port = websocket_config['port']

    async def listen(self):
        print("Connecting to " + str(self.host) + " on port " + str(self.port))
        uri = "ws://" + str(self.host) + ":" + str(self.port)
        async with websockets.connect(uri) as ws:
            while True:
                msg = await ws.recv()
                cmd = json.loads(msg)
                print("Received message from client: " + str(cmd))
                self.process_command(cmd)
                await ws.send("Server received message: " + str(msg))

    def process_command(self, cmd):
        if cmd["signal"] == "changeID" and self.robot != cmd["robot"]:
            self.robot = cmd["robot"]
        elif self.robot in cmd["targets"]:
            if cmd["signal"] == "stop":
                self.run = False
            elif cmd["signal"] == "start":
                color = cmd["baskets"][cmd["targets"].index(self.robot)]
                if color == "blue":
                    self.blueIsTarget = True
                else:
                    self.blueIsTarget = False
                self.run = True
        else:
            pass

    def get_current_referee_command(self):
        return self.run, self.blueIsTarget

    def start_loop(self):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.listen())
        loop.run_forever()

    def start(self):
        t = threading.Thread(target=self.start_loop)
        t.start()
