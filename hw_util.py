#Hardware Utilities

#imports
import network #Network is needed for intializing the wireless connection
import uasyncio as asyncio #Used to create a asyncrounous server
from machine import Pin #Basic interfacing with the device
from picozero import LED #Basic interfacing with a external LED (will supply 3.3V as output)
from timer import Timer
import config_manager
import time

"""
Variable definitions
"""

#Hardware
sensor = Pin(18, Pin.IN, Pin.PULL_DOWN)
OUT1 = LED(3) #RED
OUT2 = LED(4) #BLUE
OUT3 = LED(5) #YELLOW

#Timers
timers = {}

#States
out1_state = False
out2_state = False
out3_state = False

#Float Sensor
threshold_time = -1
overflow_time = -1



"""
Functions
"""

def intialize_timers():
    global timers, threshold_time, overflow_time
    threshold_time, overflow_time = config_manager.intialize_float_sensor("config.txt")
    threshold_time = float(threshold_time)
    overflow_time = float(overflow_time)
    timers = config_manager.initialize_timers_from_config("config.txt")
    for on_timer, off_timer, output in timers:
        asyncio.create_task(on_timer.start(handle_output_from_timer, output, True))
        asyncio.create_task(off_timer.start(handle_output_from_timer, output, False))

async def monitor_float_sensor():
    """
    Monitors the float sensor and manages OUT3 based on the input signal and timers.
    """
    global out3_state, threshold_time, overflow_time, sensor
    timer_started = False
    timer_start_time = None

    while True:
        if sensor.value():  # Input signal detected
            if not timer_started:
                timer_started = True
                timer_start_time = time.time()  # Record the timer start time
                print("Float sensor detected input. Timer started.")

            # Check if the timer has exceeded the threshold time
            elapsed_time = (time.time() - timer_start_time) / 60  # Convert seconds to minutes
            if elapsed_time >= threshold_time and not out3_state:
                enable_output(3)  # Turn on OUT3
                print("Threshold time reached. OUT3 enabled.")

        else:  # Input signal not detected
            if timer_started:
                timer_started = False
                if out3_state:
                    print(f"Input signal lost. OUT3 will remain ON for {overflow_time} minutes.")
                    await asyncio.sleep(overflow_time * 60)  # Wait for the overflow time
                    disable_output(3)  # Turn off OUT3
                    print("Overflow time elapsed. OUT3 disabled.")

        await asyncio.sleep(0.1)  # Non-blocking delay for sensor polling
        
def all_outputs_toggle():
    OUT1.toggle()
    OUT2.toggle()
    OUT3.toggle()
    
def enable_output(num):
    global out1_state, out2_state, out3_state
    if (num == 1):
        OUT1.on()
        out1_state = True
    elif (num == 2):
        OUT2.on()
        out2_state = True
    elif (num == 3):
        OUT3.on()
        out3_state = True
    else:
        print("Error in enable_output")

def disable_output(num):
    global out1_state, out2_state, out3_state
    if (num == 1):
        OUT1.off()
        out1_state = False
    elif (num == 2):
        OUT2.off()
        out2_state = False
    elif (num == 3):
        OUT3.off()
        out3_state = False
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
    
def set_water_sensor_threshold(_threshold_time):
    global threshold_time
    threshold_time = _threshold_time
    config_manager.update_water_sensor_threshold(threshold_time, "config.txt")

def set_water_sensor_fill_overflow(_overflow_time):
    overflow_time = _overflow_time
    config_manager.update_water_sensor_overflow(overflow_time, "config.txt")

async def handle_output_from_timer(output, state):
    if (state):
        enable_output(output)
    else:
        disable_output(output)

def get_current_on_time(num):
    index = num - 1
    selected_timer_on, selected_timer_off, _ = timers[index]
    timer_on_hour = selected_timer_on.hour
    timer_on_minute = selected_timer_on.minute
    days = selected_timer_on.days_of_week
    
    num_to_days = {
        0 : "M",
        1 : "T",
        2 : "W",
        3 : "TH",
        4 : "F",
        5 : "SAT",
        6 : "SUN"
    }
    
    timer_on_days = [num_to_days[day] for day in days]
    
    if (timer_on_minute < 10):
        timer_on_minute = f"0{timer_on_minute}"
    
    return f"{timer_on_hour}:{timer_on_minute}, {timer_on_days}"

def get_current_off_time(num):
    index = num - 1
    selected_timer_on, selected_timer_off, _ = timers[index]
    timer_off_hour = selected_timer_off.hour
    timer_off_minute = selected_timer_off.minute
    days = selected_timer_off.days_of_week
    
    num_to_days = {
        0 : "M",
        1 : "T",
        2 : "W",
        3 : "TH",
        4 : "F",
        5 : "SAT",
        6 : "SUN"
    }
    
    timer_off_days = [num_to_days[day] for day in days]
    
    if (timer_off_minute < 10):
        timer_off_minute = f"0{timer_off_minute}"
    
    return f"{timer_off_hour}:{timer_off_minute}, {timer_off_days}"

def get_current_state(num):
    if (num == 1):
        if (out1_state):
            return "ON"
        else:
            return "OFF"
    if (num == 2):
        if (out2_state):
            return "ON"
        else:
            return "OFF"
    if (num == 3):
        if (out3_state):
            return "ON"
        else:
            return "OFF"

