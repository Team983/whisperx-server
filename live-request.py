from websockets.sync.client import connect

with connect("ws://localhost:8081/live") as websocket:
    websocket.send("Space the final")
    while True:
        received = websocket.recv()
        if received == "<<Response Finished>>":
            break
        print(received, end="")
    print("\n")

    websocket.send(" These are the voyages")
    while True:
        received = websocket.recv()
        if received == "<<Response Finished>>":
            break
        print(received, end="")
    print("\n")

