import network #Network is needed for intializing the wireless connection
import uasyncio as asyncio #Used to create a asyncrounous server
from timer import Timer
import time

def read_config(file_path="config.txt"):
    config = {}
    try:
        with open(file_path, "r") as file:
            section = None
            for line in file:
                line = line.strip()
                if not line or line.startswith("#"):  # Skip empty lines and comments
                    continue
                if line.startswith("[") and line.endswith("]"):  # Section header
                    section = line[1:-1]
                    config[section] = {}
                elif "=" in line and section:  # Key-value pair
                    key, value = line.split("=", 1)
                    config[section][key.strip()] = value.strip()
    except OSError as e:
        print(f"Error reading config file: {e}")
    return config


def write_config(config, file_path="config.txt"):
    try:
        print("Writing to Config")
        with open(file_path, "w") as file:
            for section, pairs in config.items():
                file.write(f"[{section}]\n")
                for key, value in pairs.items():
                    file.write(f"{key}={value}\n")
                file.write("\n")  # Blank line between sections
    except OSError as e:
        print(f"Error writing to config file: {e}")


def update_config_section(config, section, key, value):
    if section not in config:
        config[section] = {}
    config[section][key] = value


def update_output_timer(output, on_time, off_time, days, file_path="config.txt"):
    config = read_config(file_path)
    section = "OutputTimers"
    update_config_section(config, section, f"output_{output}_on", on_time)
    update_config_section(config, section, f"output_{output}_off", off_time)
    update_config_section(config, section, f"output_{output}_days", ",".join(days))
    write_config(config, file_path)


def update_water_sensor_threshold(threshold_time, file_path="config.txt"):
    config = read_config(file_path)
    update_config_section(config, "WaterSensor", "threshold_time", threshold_time)
    write_config(config, file_path)


def update_water_sensor_overflow(overflow_time, file_path="config.txt"):
    config = read_config(file_path)
    update_config_section(config, "WaterSensor", "fill_overflow_time", overflow_time)
    write_config(config, file_path)


def initialize_timers_from_config(file_path="config.txt"):
    config = read_config(file_path)
    timers = []
    
    # Ensure OutputTimers section exists
    output_timers = config.get("OutputTimers", None)
    if not output_timers:
        print("Error: Missing [OutputTimers] section in config file.")
        return timers  # Return an empty list

    for output in range(1, 4):  # Assuming 3 outputs
        # Safely retrieve values
        on_time = output_timers.get(f"output_{output}_on")
        off_time = output_timers.get(f"output_{output}_off")
        days = output_timers.get(f"output_{output}_days")
        
        if on_time and off_time and days:
            try:
                # Parse on_time and off_time
                on_hour, on_minute = map(int, on_time[:-3].split(":"))
                on_ampm = on_time[-2:]
                on_hour = on_hour if on_ampm == "AM" else (on_hour % 12) + 12

                off_hour, off_minute = map(int, off_time[:-3].split(":"))
                off_ampm = off_time[-2:]
                off_hour = off_hour if off_ampm == "AM" else (off_hour % 12) + 12

                # Parse days
                day_to_number = {
                    "Monday": 0,
                    "Tuesday": 1,
                    "Wednesday": 2,
                    "Thursday": 3,
                    "Friday": 4,
                    "Saturday": 5,
                    "Sunday": 6
                }
                
                days_of_week = [day_to_number[day.strip()] for day in days.split(",")]

                # Create and configure timers
                on_timer = Timer(hour=on_hour, minute=on_minute, days_of_week=days_of_week)
                off_timer = Timer(hour=off_hour, minute=off_minute, days_of_week=days_of_week)

                # Add to the list of timers
                timers.append((on_timer, off_timer, output))
            except Exception as e:
                print(f"Error parsing timer for output {output}: {e}")
        else:
            print(f"Warning: Missing configuration for output {output}")
    
    return timers

def intialize_float_sensor(file_path="config.txt"):
    config = read_config(file_path)
    water_sensor_config = config.get("WaterSensor", None)
    if not water_sensor_config:
        print("Error: Missing [WaterSensor] section in config file.")
        return _, _
    threshold = water_sensor_config.get("threshold_time")
    overflow = water_sensor_config.get("fill_overflow_time")
    return threshold, overflow


