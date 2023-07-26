import asyncio
import json
import websockets
import time

# Global variables to store the current heartbeat value and time of the polar-device
current_hr_bpm = 70
current_time = None

# Background task for receiving heartbeat from websockets server
async def connect_and_fetch_data():
    global current_hr_bpm
    global current_time
    async with websockets.connect('ws://[2a02:3033:608:9785:3fff:cc38:f41e:d205]:8919/ws/hr_json') as ws:
        try:
            message = await ws.recv()
            data = json.loads(message)
            current_hr_bpm = data.get('hr')
            current_time = data.get('time')

        except websockets.exceptions.ConnectionClosedOK:
            print("WebSocket connection closed.")
        except Exception as e:
            print(f"Error: {str(e)}")

# Main program
async def main():
    while True:
        await connect_and_fetch_data()
        print("Current heartbeat:", current_hr_bpm, "at:", current_time)
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
