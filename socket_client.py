import asyncio
import websockets
import json


class Client:

    def __init__(self):
        self.run = None
        self.blueIsTarget = True
        self.host = "localhost"
        self.port = 8765

    async def listen_to_server(self):
        print("Starting client...")
        uri = "ws://" + self.host + ":" + str(self.port)
        async with websockets.connect(uri) as websocket:
            while True:
                print("Listening to server...")
                msg = await websocket.recv()
                cmd = json.loads(msg)
                print("Received message " + str(cmd))
                self.process_command(cmd)

    def process_command(self, cmd):
        print("Processing command " + str(cmd))
        if cmd["signal"] == "stop":
            self.run = False
            self.blueIsTarget = None
        elif cmd["signal"] == "start":
            if cmd["basketTarget"] == "blue":
                self.blueIsTarget = True
            elif cmd["basketTarget"] == "magenta":
                self.blueIsTarget = False
            self.run = True

    def get_current_referee_command(self):
        return self.run, self.blueIsTarget


cl = Client()
asyncio.get_event_loop().run_until_complete(cl.listen_to_server())
