import uasyncio as asyncio #Used to create a asyncrounous server
from timer import Timer

def read_config(file_path="config.txt"):
    """
    Config Manager:
    read_config(file_path)

    Used to read the config.txt file. Returns the config as a dictionary for easy access.
    """
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
    """
    Config Manager:
    write_config(config, file_path)

    Used to write to config.txt using the updated config dictonary.
    """
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
    """
    Config Manager:
    update_config_section(config, section, key, value)

    Used to update a specific section of the config dictionary.

    :param section: section of the config
    :param key: the key of what is being updated
    :param value: the updated value
    """
    if section not in config:
        config[section] = {}
    config[section][key] = value


def update_output_timer(output, on_time, off_time, days, file_path="config.txt"):
    """
    Config Manager:
    update_output_timer(output, on_time, off_time, days, file_path)

    Used to update output's stored timer values.

    :param output: the output number (1-3)
    :param on_time: the new on time
    :param off_time: the new off time
    :param days: the new list of days
    """
    config = read_config(file_path)
    section = "OutputTimers"
    update_config_section(config, section, f"output_{output}_on", on_time)
    update_config_section(config, section, f"output_{output}_off", off_time)
    update_config_section(config, section, f"output_{output}_days", ",".join(days))
    write_config(config, file_path)


def update_water_sensor_threshold(threshold_time, file_path="config.txt"):
    """
    Config Manager:
    update_water_sensor_threshold(threshold_time, file_path)

    Used to update the water sensor's stored threshold value
    """
    config = read_config(file_path)
    update_config_section(config, "WaterSensor", "threshold_time", threshold_time)
    write_config(config, file_path)


def update_water_sensor_overflow(overflow_time, file_path="config.txt"):
    """
    Config Manager:
    update_water_sensor_overflow(overflow_time, file_path)

    Used to update the water sensor's stored overflow time
    """
    config = read_config(file_path)
    update_config_section(config, "WaterSensor", "fill_overflow_time", overflow_time)
    write_config(config, file_path)


def initialize_timers_from_config(file_path="config.txt"):
    """
    Config Manager:
    intialize_timers_from_config(file_path)

    Reads the config then parses the data into a format acceptable for the Timer class.
    Then creates a list of timers based on the parsed data.
    """
    config = read_config(file_path)
    timers = []
    
    # Ensure OutputTimers section exists
    output_timers = config.get("OutputTimers", None)
    if not output_timers:
        print("Error: Missing [OutputTimers] section in config file.")
        return timers  # Return an empty list

    for output in range(1, 4):  # 3 outputs
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
        elif (on_time and off_time):
            on_timer = Timer(hour=on_hour, minute=on_minute, days_of_week=None)
            off_timer = Timer(hour=off_hour, minute=off_minute, days_of_week=None)
            
            # Add to the list of timers
            timers.append((on_timer, off_timer, output))
        else:
            print(f"Warning: Missing configuration for output {output}")
    
    return timers

def intialize_float_sensor(file_path="config.txt"):
    """
    Config Manager:
    intialize_float_sensor(file_path)

    Reads the config then returns the threshold and overflow times for the water sensor.
    """
    config = read_config(file_path)
    water_sensor_config = config.get("WaterSensor", None)
    if not water_sensor_config:
        print("Error: Missing [WaterSensor] section in config file.")
        return _, _
    threshold = water_sensor_config.get("threshold_time")
    overflow = water_sensor_config.get("fill_overflow_time")
    return threshold, overflow


