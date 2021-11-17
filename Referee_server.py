import asyncio
import threading
import websockets
import json


class Server:

    def __init__(self):
        self.run = False
        self.blueIsTarget = True
        self.robot_id = "Kobe"
        f = open('websocket_config.json', "r")
        websocket_config = json.loads(f.read())
        self.host = websocket_config['host']
        self.port = websocket_config['port']

    def get_host(self):
        return self.host

    def get_port(self):
        return self.port

    async def listen(self, websocket, path):
        print("A client connected to " + str(self.host) + " on port " + str(self.port))
        try:
            async for message in websocket:
                cmd = json.loads(message)
                print("Received message from client: " + str(cmd))
                self.process_command(cmd)
                await websocket.send("Server received message: " + str(message))
        except websockets.exceptions.ConnectionClosed as e:
            print("A client disconnected")

    def process_command(self, cmd):
        if cmd["signal"] == "changeID" and self.robot_id != cmd["robot_id"]:
            self.robot_id = cmd["robot_id"]
        elif cmd["robot_id"] == self.robot_id:
            if cmd["signal"] == "stop":
                self.run = False
            elif cmd["signal"] == "start":
                if cmd["basketTarget"] == "blue":
                    self.blueIsTarget = True
                elif cmd["basketTarget"] == "magenta":
                    self.blueIsTarget = False
                self.run = True
        else:
            pass

    def get_current_referee_command(self):
        return self.run, self.blueIsTarget

    def start_loop(self, loop, server):
        loop.run_until_complete(server)
        loop.run_forever()

    def start(self):
        new_loop = asyncio.new_event_loop()
        server = websockets.serve(self.listen, self.get_host(), self.get_port(), loop=new_loop, ping_interval=None, ping_timeout=None)
        t = threading.Thread(target=self.start_loop, args=(new_loop, server))
        t.start()
