#Hardware Utilities

#imports
import uasyncio as asyncio #Used to create a asyncrounous tasks
from machine import Pin #Basic interfacing with the device
from picozero import LED #Basic interfacing with a external LED (will supply 3.3V as output)
from timer import Timer
import config_manager
import time

"""
Variable definitions
"""

#Hardware
sensor = Pin(18, Pin.IN, Pin.PULL_DOWN) # Input - For Water Float Sensor
OUT1 = LED(3) # Output 1 (Can use LED as it will send a constant out signal)
OUT2 = LED(4) # Output 2 (May look into using Pin instead...)
OUT3 = LED(5) # Output 3

#Timers
timers = {}

#States
out1_state = False
out2_state = False
out3_state = False

#Float Sensor
threshold_time = -1
overflow_time = -1

#Leak Prevention
water_fill_count = 0
leak_detected = False
max_water_fill_count = 3


"""
Functions
"""

async def monitor_leak():
    """
    Hardware Utility
    monitor_leak()

    Uses the water_fill_count caused by the float sensor and if that count is
    greater than "max_water_fill_count (3)" in a day, a leak is assumed to be detected and shuts off all outputs and disables the enabling of outputs.

    IMPORTANT: When activated - device requires a restart.
    """
    global water_fill_count, leak_detected
    last_reset_time = time.time()
    while True:
        current_time = time.time()
        if (current_time - last_reset_time >= 86400): # 24 hours in seconds
            water_fill_count = 0
        if (water_fill_count > max_water_fill_count):
            OUT1.off()
            OUT2.off()
            OUT3.off()
            leak_detected = True
            print("Water Fill Count for today is greater than 3, Leak Detected")
        await asyncio.sleep(0.1)
            


def intialize_timers():
    """
    Hardware Utility
    intialize_timers()

    First thing handled on start up, reads the config and sets the threshold_time, overflow_time as well as creating the list of timers.
    Also starts the Async timers.
    """
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
    Hardware Utility
    monitor_float_sensor()

    Monitors the float sensor and when activated, starts a timer for the threshold time. Once that threshold time is crossed - enabled output 3 (the water fill), 
    which is disabled when the sensor is disabled + the overflow time.
    """
    global out3_state, threshold_time, overflow_time, sensor, water_fill_count
    timer_started = False
    timer_start_time = None

    while True:
        if sensor.value():  # Input signal detected
            if not timer_started:
                timer_started = True
                timer_start_time = time.time()  # Record the timer start time
                print("Float sensor detected input. Timer started.")

            # Check if the timer has exceeded the threshold time
            elapsed_time = (time.time() - timer_start_time) / 60
            if elapsed_time >= threshold_time and not out3_state:
                enable_output(3)
                water_fill_count += 1
                print("Threshold time reached. OUT3 enabled.")

        else:  # Input signal not detected
            if timer_started:
                timer_started = False
                if out3_state:
                    print(f"Input signal lost. OUT3 will remain ON for {overflow_time} minutes.")
                    await asyncio.sleep(overflow_time * 60)
                    disable_output(3)
                    print("Overflow time elapsed. OUT3 disabled.")

        await asyncio.sleep(0.1)
        
def all_outputs_toggle():
    OUT1.toggle()
    OUT2.toggle()
    OUT3.toggle()
    
def enable_output(num):
    """
    Hardware Utility
    enable_output(num)

    Simple function which intakes the output number (1-3) and enables them accordingly.
    """
    global out1_state, out2_state, out3_state, water_fill_count
    if (leak_detected):
        return
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
    """
    Hardware Utility
    disable_output(num)

    Simple function which intakes the output number (1-3) and disables them accordingly.
    """
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
    """
    Hardware Utility
    set_output_timers(output, on_time, off_time, days)

    Accesses the current list of timers and sets the respective outputs timer's On Time, Off Time, and Days to the new parameters.
    """
    index = output - 1 # Since list is 0 indexed, the index is the output number - 1
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
    """
    Hardware Utility
    set_water_sensor_threshold(_threshold_time)

    Sets the threshold_time to the new value in the hw and config.
    """
    global threshold_time
    threshold_time = _threshold_time
    config_manager.update_water_sensor_threshold(threshold_time, "config.txt")

def set_water_sensor_fill_overflow(_overflow_time):
    """
    Hardware Utility
    set_water_sensor_fill_oiverflow(_overflow_time)

    Sets the overflow_time to the new value in the hw and config.
    """
    overflow_time = _overflow_time
    config_manager.update_water_sensor_overflow(overflow_time, "config.txt")

async def handle_output_from_timer(output, state):
    """
    Hardware Utility
    handle_output_from_timer(output, state)

    Based on the current state of the output, will enable or disable the output. Used by the timer to interact with the hw outputs.
    """
    if (state):
        enable_output(output)
    else:
        disable_output(output)
