import asyncio
import threading
from ast import literal_eval
from configparser import ConfigParser
import websockets
import json


parser = ConfigParser()
parser.read('config.ini')


class Server:

    def __init__(self):
        self.run = False
        self.blueIsTarget = True
        self.robot = literal_eval(parser.get('robot', 'robot_id'))
        self.host = literal_eval(parser.get('websocket', 'host'))
        self.port = literal_eval(parser.get('websocket', 'port'))

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
        if self.robot in cmd["targets"]:
            if cmd["signal"] == "changeID" and self.robot != cmd["robot"]:
                self.robot = cmd["robot"]
                parser.set('robot', 'robot_id', repr(self.robot))
                with open('config.ini', "w") as f:
                    parser.write(f)

            if cmd["signal"] == "stop":
                self.run = False
            elif cmd["signal"] == "start":
                color = cmd["baskets"][cmd["targets"].index(self.robot)]
                if color == "blue":
                    self.blueIsTarget = True
                else:
                    self.blueIsTarget = False
                self.run = True

    def get_current_referee_command(self):
        return self.run, self.blueIsTarget

    def start_loop(self):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.listen())
        loop.run_forever()

    def start(self):
        t = threading.Thread(target=self.start_loop)
        t.start()
