import asyncio
import json
import websockets
#import time

#current_hr_bpm = 70


async def connect_and_fetch_data():
    async with websockets.connect('ws://127.0.0.1:8919/ws/hr_json') as ws:
        prev_second = None
        while True:
            try:
                message = await ws.recv()
                data = json.loads(message)
                
                current_second = int(data['time'].split(':')[2])
                if prev_second is None or current_second != prev_second:
                    prev_second = current_second                    
                    current_hr_bpm = data.get('hr')
                    current_time = data.get('time')
                    print(current_time)
                    print(current_hr_bpm)
                    
            except websockets.exceptions.ConnectionClosedOK:
                print("WebSocket connection closed.")
                break
            except Exception as e:
                print(f"Error: {str(e)}")

asyncio.run(connect_and_fetch_data())
