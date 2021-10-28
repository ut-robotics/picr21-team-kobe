import asyncio
import websockets
import json


class Server:

    def __init__(self):
        self.run = False
        self.blueIsTarget = True
        f = open('./websocket_config.json', "r")
        websocket_config = json.loads(f.read())
        self.host = websocket_config['host']
        self.port = websocket_config['port']

    def get_host(self):
        return self.host

    def get_port(self):
        return self.port

    async def listen(self, websocket, path):
        print("A client connected")
        try:
            async for message in websocket:
                cmd = json.loads(message)
                print("Received message from client: " + str(cmd))
                self.process_command(cmd)
                await websocket.send("Server received message: " + str(message))
        except websockets.exceptions.ConnectionClosed as e:
            print("A client disconnected")

    def process_command(self, cmd):
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

    def start(self):
        start_server = websockets.serve(self.listen, self.get_host(), self.get_port())
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()


srv = Server()
srv.start()
