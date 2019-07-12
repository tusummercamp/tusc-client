import json, math, time, asyncio, websockets

server_uri = "ws://localhost:4545"
temp = []
odo = []
speed = []
lastSend = 0

def flush():
    global lastSend, temp, odo, speed
    now = time.time()

    if abs(lastSend - now) > 5:
        print("Should send data to {}: {}".format('https://temp', json.dumps(temp)))
        print("Should send data to {}: {}".format('https://odo', json.dumps(odo)))
        print("Should send data to {}: {}".format('https://speed', json.dumps(speed)))
        lastSend = now
        temp = []
        odo = []
        speed = []
        
def parse_message(msg):
    data = list(map(lambda entry : entry.split(':'), msg.split('|')))
    for entry in data:
        metric, value = entry
        if metric == 'Speed':
            speed.append({ 'time': int(time.time()), 'value': float(value) })
        elif metric == 'Temp':
            temp.append({ 'time': int(time.time()), 'value': float(value) })
        elif metric == 'Odo':
            temp.append({ 'time': int(time.time()), 'value': float(value) })
    flush()

async def handler():
    global server_uri
    async with websockets.connect(server_uri) as websocket:
        while True:
            msg = await websocket.recv()
            parse_message(msg)

asyncio.get_event_loop().run_until_complete(handler())
