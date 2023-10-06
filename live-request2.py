from websockets.sync.client import connect

with connect("ws://220.118.70.197:8000/live") as websocket:
    websocket.send("Hello world!")  