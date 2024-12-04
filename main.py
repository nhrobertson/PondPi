#Pond Fountain Controller - Main
#Created By Noah Robertson

"""
Pond Fountain Controller

This simple Raspberry Pi Pico W controller was designed to control our backyard pond. The circuit will be displayed in
the README.md and is using Solid State Relays (Not very practical) but we had some on hand. 

Requirements:
    Inputs:
    - Float Switch
    
    Outputs:
    - Pump 1
    - Pump 2
    - Water Fill
    
    Functionality:
    - Internal Timer
        - 24 Hour Adjustable
        - Date Controller
        
I/O is handled through the timers and controlled through a local network. IP address and Port for your device will be displayed on start up.

Please feel free to take and modify this - was fun little project :)
"""

#imports
import network #Network is needed for intializing the wireless connection
import uasyncio as asyncio #Used to create a asyncrounous server
from network_util import connect_wifi, handle_client, load_html
from hw_util import monitor_float_sensor, intialize_timers, monitor_leak

"""
Variable definitions
"""

"""
Functions
"""

async def main():
    #Uses hw_util to set up the timers from config.txt to begin logic
    intialize_timers()

    #Needed to get the webpage loaded
    load_html()
    ip = await connect_wifi()
    
    #Setups up the server
    print("Setting up server")
    server = await asyncio.start_server(handle_client, ip, 80)
    print(f"Server running on http://{ip}:80")

    #Async tasks for monitoring hw inputs
    asyncio.create_task(monitor_float_sensor())
    asyncio.create_task(monitor_leak())

    await server.wait_closed()
    
try:
    asyncio.run(main())
except Exception as e:
    print(f"Error in main: {e}")
except KeyboardInterrupt:
    print("Keyboard Interrupt")


