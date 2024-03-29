import threading, asyncio, websockets, time, random

# Global stop flag
stopFlag = False

"""
DataWorker thread responsible for data generation.
"""
class DataWorker (threading.Thread):
    
    # Constructor
    def __init__(self):
        threading.Thread.__init__(self)
        self.data = 0
        self.lastData = 0
        self.inc = 0

    # Generate data
    def run(self):
        while not stopFlag:
            self.data = self.inc
            self.inc = random.randrange(2000, 7000) / 10
            time.sleep(0.05)

    # Data getter
    def get(self):
        if self.lastData is not self.data:
            self.lastData = self.data
            return self.data


"""
MessagingWorker thread responsible for sending
messages over websockets.
"""
class MessagingWorker (threading.Thread):
    
    # Constructor
    def __init__(self, interval=0.05):
        threading.Thread.__init__(self)
        self.interval = interval
        self.connected = set()

    # Send data on predefined intervals
    def run(self):
        while not stopFlag:
            data = dataWorker.get()
            if data:
                self.broadcast("|Speed|%s|Temp|%s|Odo|%s|" % (data, data, data))

            time.sleep(self.interval)

    # Websockets handler
    async def handler(self, websocket, path):
        self.connected.add(websocket)
        try:
            await websocket.recv()
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.connected.remove(websocket)

    # Broadcast to all clients
    def broadcast(self, data):
        for websocket in self.connected.copy():
            print("Sending data: %s" % data)
            coro = websocket.send(data)
            future = asyncio.run_coroutine_threadsafe(coro, loop)


if __name__ == "__main__":
    
    print('Data publisher')
    dataWorker = DataWorker()
    messagingWorker = MessagingWorker()

    try:
        # Create data and messaging threads
        dataWorker.start()
        messagingWorker.start()

        # Create server
        ws_server = websockets.serve(messagingWorker.handler, '0.0.0.0', 4545)

        # Create async loop
        loop = asyncio.get_event_loop()
        loop.run_until_complete(ws_server)
        loop.run_forever()

    except KeyboardInterrupt:
        stopFlag = True

        # Close async loop
        loop.stop()
        loop.close()
        print("Exiting program...")
