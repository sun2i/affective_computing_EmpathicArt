import asyncio
import json
import websockets

# Global variables to store the current heartbeat value and time of the polar-device
current_hr_bpm = None
current_time = None

#Background task for receiving heartbeat from websockets server
async def connect_and_fetch_data():
    global current_hr_bpm
    global current_time

    async with websockets.connect('ws://127.0.0.1:8919/ws/hr_json') as ws:
        prev_second = None
        while True:
            try:
                message = await ws.recv()
                data = json.loads(message)

                #heartbeat is updated once every second not with every tick
                current_second = int(data['time'].split(':')[2])
                if prev_second is None or current_second != prev_second:
                    prev_second = current_second
                    current_hr_bpm = data.get('hr')
                    current_time = data.get('time')
                    #print(current_time)
                    #print(current_hr_bpm)

            except websockets.exceptions.ConnectionClosedOK:
                print("WebSocket connection closed.")
                break
            except Exception as e:
                print(f"Error: {str(e)}")


# Main program
async def main():
    global current_hr_bpm
    global current_time
    
    #just for display > normal code here
    while True:
        print("Current heartbeat:", current_hr_bpm, "at: ", current_time)
        await asyncio.sleep(1)




# Create and run the event loop to await the coroutine > very bottom
loop = asyncio.get_event_loop()
loop.create_task(connect_and_fetch_data())
loop.run_until_complete(main())
