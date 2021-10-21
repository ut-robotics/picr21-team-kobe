import websockets
import asyncio
import json


class Server:

    def __init__(self):
        f = open('WebsocketConfig.json', "r")
        websocketConfig = json.loads(f.read())
        self.host = websocketConfig['host']
        self.port = websocketConfig['port']

    async def send_to_client(self, websocket, path):
        while True:
            cmd = int(input("Enter a command: 1, 2 or 3"))
            print("Processing command " + str(cmd))
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
                print("Invalid command entered. Use 1, 2 or 3.")
                continue
            print("Sending message: " + str(msg))
            await websocket.send(json.dumps(msg))
            print("Message '{}' sent.".format(msg))

    async def start_server(self):
        print("Starting server...")
        async with websockets.serve(self.send_to_client, self.host, self.port):
            await asyncio.Future()


srv = Server()
asyncio.run(srv.start_server())
