#Pond Fountain Controller

"""
The Pond Fountain Controller will be located away from the pond.
We are targetting to be able to handle this through physical switches
and local online ones.

Requirements:
    Inputs:
    - Float Switch
    
    Output:
    - Pump 1
    - Pump 2
    - Water Fill
    
    Functionality:
    - Internal Timer
        - 24 Hour Adjustable
        - Date Controller
        
I/O will need to be handled both locally and through the network where
the timer is going to be controlled networkly. I am planning on using a
storage file to store the settings of the contoller.
"""

#imports
import network #Network is needed for intializing the wireless connection
import uasyncio as asyncio #Used to create a asyncrounous server
from network_util import connect_wifi, handle_client, load_html
from hw_util import monitor_button, handle_output_from_timer
from timer import Timer
import time
import config_manager

"""
Variable definitions
"""

#Global Variables
pump_1_bool = False
pump_2_bool = False
water_fill_bool = False

#Test Vars
state = "OFF"
led_on = False

"""
Functions
"""

async def main():
    timers = config_manager.initialize_timers_from_config("config.txt")

    for on_timer, off_timer, output in timers:
        asyncio.create_task(on_timer.start(handle_output_from_timer, output, True))
        asyncio.create_task(off_timer.start(handle_output_from_timer, output, False))

    #Setup timers that are linked to the hardware (timers should be accessable in hw_util)

    load_html()
    ip = await connect_wifi()
    
    print("Setting up server")
    server = await asyncio.start_server(handle_client, ip, 80)
    print(f"Server running on http://{ip}:80")
    
    asyncio.create_task(monitor_button())
    #TODO
    #Create Task to Monitor Physical Inputs which Output to Pumps amd Water Fill
    #Those Physcial Functions will need to call control functions that use the timer
    await server.wait_closed()
    
try:
    asyncio.run(main())
except Exception as e:
    print(f"Error in main: {e}")
except KeyboardInterrupt:
    print("Keyboard Interrupt")


