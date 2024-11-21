#Hardware Utilities

#imports
import network #Network is needed for intializing the wireless connection
import uasyncio as asyncio #Used to create a asyncrounous server
from machine import Pin #Basic interfacing with the device
from picozero import LED #Basic interfacing with a external LED (will supply 3.3V as output)
from timer import Timer
import config_manager

"""
Variable definitions
"""

#Hardware
button = Pin(18, Pin.IN, Pin.PULL_DOWN)
OUT1 = LED(3) #RED
OUT2 = LED(4) #BLUE
OUT3 = LED(5) #YELLOW

#Timers
timers = {}


"""
Functions
"""

def intialize_timers():
    global timers
    timers = config_manager.initialize_timers_from_config("config.txt")
    for on_timer, off_timer, output in timers:
        asyncio.create_task(on_timer.start(handle_output_from_timer, output, True))
        asyncio.create_task(off_timer.start(handle_output_from_timer, output, False))

# Async function to monitor the button
async def monitor_button():
    #global state
    while True:
        if button.value():  # Button is pressed
            #light_switch()  # Toggle the LED
            #state = "ON" if led_on else "OFF"  # Update the state
            print("button")
            all_outputs_toggle()
            await asyncio.sleep(0.3)  # Debouncing with non-blocking sleep
        await asyncio.sleep(0.1)  # Non-blocking loop for button checking
        
def all_outputs_toggle():
    OUT1.toggle()
    OUT2.toggle()
    OUT3.toggle()
    
def enable_output(num):
    if (num == 1):
        OUT1.on()
    elif (num == 2):
        OUT2.on()
    elif (num == 3):
        OUT3.on()
    else:
        print("Error in enable_output")

def disable_output(num):
    if (num == 1):
        OUT1.off()
    elif (num == 2):
        OUT2.off()
    elif (num == 3):
        OUT3.off()
    else:
        print("Error in disable_output")

def set_output_times(output, on_time, off_time, days):
    index = output - 1
    day_to_number = {
        "Monday": 0,
        "Tuesday": 1,
        "Wednesday": 2,
        "Thursday": 3,
        "Friday": 4,
        "Saturday": 5,
        "Sunday": 6
    }
    days_of_week = [day_to_number[day] for day in days] 
    
    selected_timer_on, selected_timer_off, _ = timers[index]
    
    selected_timer_on.set_time(*on_time)
    selected_timer_on.set_days_of_week(days_of_week)
    
    selected_timer_off.set_time(*off_time)
    selected_timer_off.set_days_of_week(days_of_week)
    
def set_water_sensor_threshold(threshold_time):
    print("Threshold Time: " + threshold_time)

def set_water_sensor_fill_overflow(overflow_time):
    print("Water Fill Overflow Time: " + overflow_time)

async def handle_output_from_timer(output, state):
    if (state):
        enable_output(output)
    else:
        disable_output(output)

async def update_timer(output, on_time, off_time, days):
    # Update configuration
    config_manager.update_output_timer(output, on_time, off_time, days)

    # Update active timers
    on_hour, on_minute = map(int, on_time[:-3].split(":"))
    on_ampm = on_time[-2:]
    on_hour = on_hour if on_ampm == "AM" else (on_hour % 12) + 12

    off_hour, off_minute = map(int, off_time[:-3].split(":"))
    off_ampm = off_time[-2:]
    off_hour = off_hour if off_ampm == "AM" else (off_hour % 12) + 12

    days_of_week = [day.strip() for day in days.split(",")]

    # Reset timers for the output
    on_timer = Timer(hour=on_hour, minute=on_minute, days_of_week=days_of_week)
    off_timer = Timer(hour=off_hour, minute=off_minute, days_of_week=days_of_week)

    asyncio.create_task(on_timer.start(handle_output_from_timer, output, True))
    asyncio.create_task(off_timer.start(handle_output_from_timer, output, False))