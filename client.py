import json, math, time, asyncio, websockets, datetime, requests, threading
from plot import Plot

# ====================================
# CONFIGURATION
# ====================================
SERVER_URL = "ws://localhost:4545"
SPEED_URL ='https://32mo5c9zs2.execute-api.us-east-1.amazonaws.com/Prod/data'
TEMP_URL ='https://i90jji9q5j.execute-api.us-east-1.amazonaws.com/Prod/data'
ODO_URL ='https://g9eyv3jby5.execute-api.us-east-1.amazonaws.com/Prod/data'
SEND_PERIOD = 5

class Client(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

        self.loop = None
        self.temp = []
        self.odo = []
        self.speed = []
        self.lastSend = 0

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.handler())
    
    def stop(self):
        self.loop.stop()
        self.loop.close()

    def get_plot_data(self):
        if (len(self.speed) > 0):
            return self.speed[-1][1]
        else:
            return 0

    """
    Resample microsecond-sampled input data into 
    average values sampled in seconds
    """
    def resample(self, data):
        result_array = []
        temp_array = []
        for v_time, value in data:
            if len(temp_array) > 0 and int(temp_array[-1][0]) != int(v_time):
                v_times, values = list(zip(*temp_array))
                average_value = math.floor(sum(values) / len(values) * 100) / 100
                result_array.append({ "time": int(v_time), "value": average_value })
                temp_array = []
            else:
                temp_array.append((v_time, value))
        return result_array

    def flush(self):
        now = time.time()
        if abs(self.lastSend - now) > SEND_PERIOD:
            try:
                # requests.post(SPEED_URL, data=json.dumps(self.resample(self.speed)))
                # requests.post(TEMP_URL, data=json.dumps(self.resample(self.temp)))
                # requests.post(ODO_URL, data=json.dumps(self.resample(self.odo)))
                self.lastSend = now
                self.temp = []
                self.odo = [] 
                self.speed = []
                print('Data sent')
            except Exception as e:
                print(str(e))
            
    def parse_message(self, msg):
        data = msg.split('|')
        speed = float(data[1])
        temp = float(data[3])
        odo = float(data[5])
        self.speed.append((time.time(), speed))
        self.temp.append((time.time(), temp))
        self.odo.append((time.time(), odo))
        self.flush()

    async def handler(self):
        async with websockets.connect(SERVER_URL) as websocket:
            while True:
                msg = await websocket.recv()
                self.parse_message(msg)


if __name__ == "__main__":
    
    ws_client = Client()
    try:
        ws_client.start()
        plt = Plot(ws_client) # this is blocking call
    except KeyboardInterrupt:
        ws_client.stop()
        plt.stop()
        