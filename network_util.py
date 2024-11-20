#Network Utilities

#imports
import network #Network is needed for intializing the wireless connection
import uasyncio as asyncio #Used to create a asyncrounous server
import hw_util


"""
Variable definitions
"""
#Network
ssid = ''
password = ''

#Other Variables
html_content = ""

"""
Functions
"""

def load_html():
    global html_content
    try:
        with open('index.html', 'r') as file:
            html_content = file.read()
    except Exception as e:
        print(f"Error reading index.html: {e}")
        html_content = "<html><body><h1>Error loading page</h1></body></html>"

async def connect_wifi():
    """"""""""""""""""""
    "   connect_wifi   "
    "                  "
    " Async Function to"
    " connect to WIFI  "
    """"""""""""""""""""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    
    # Wait for the connection to establish
    while not wlan.isconnected():
        print('Connecting to WiFi...')
        await asyncio.sleep(1)  # Non-blocking wait for connection
    
    ip = wlan.ifconfig()[0]
    print(f'Connected! IP: {ip}')
    return ip

# HTML page generator
def generate_webpage():
    """
    Modify the HTML Content for updates
    """
    global html_content
    page_content = html_content
    #for i in range(1, 4):  # Adjust the range if you have more outputs
    #    page_content = page_content.replace(f'{{CURRENT_ON_TIME_{i}}}', get_current_on_time(i))
    #    page_content = page_content.replace(f'{{CURRENT_OFF_TIME_{i}}}', get_current_off_time(i))
    #    page_content = page_content.replace(f'{{STATE_{i}}}', get_state(i))
    return page_content

async def handle_client(reader, writer):
    # Read the request line
    request_line = await reader.readline()
    request_line = request_line.decode('utf-8').strip()
    print(f"Request: {request_line}")

    # Read headers and store them in a dictionary
    headers = {}
    while True:
        header_line = await reader.readline()
        if header_line == b'\r\n' or header_line == b'':
            break
        header_line = header_line.decode('utf-8').strip()
        if ':' in header_line:
            key, value = header_line.split(':', 1)
            headers[key.strip()] = value.strip()

    # Parse the request method, path, and HTTP version
    try:
        method, request_uri, http_version = request_line.split()
    except ValueError:
        # Malformed request line
        print("Malformed request line")
        await writer.wait_closed()
        return

    # Split path and query string
    if '?' in request_uri:
        path, query_string = request_uri.split('?', 1)
    else:
        path = request_uri
        query_string = ''

    # Parse parameters from query string or body
    if method == 'GET':
        params = parse_query_string(query_string)
    elif method == 'POST':
        content_length = int(headers.get('Content-Length', 0))
        body = await reader.read(content_length)
        params = parse_query_string(body.decode('utf-8'))
    else:
        params = {}

    print(f"Method: {method}")
    print(f"Path: {path}")
    print(f"Parameters: {params}")

    # Handle the request based on the path
    if path == "/enable_output1":
        print("Enabling Output 1")
        hw_util.enable_output(1)
    elif path == "/disable_output1":
        print("Disabling Output 1")
        hw_util.disable_output(1)
    elif path == "/set_output1_times":
        await handle_set_output_times(writer, params, output_number=1)
    elif path == "/enable_output2":
        print("Enabling Output 2")
        hw_util.enable_output(2)
    elif path == "/disable_output2":
        print("Disabling Output 2")
        hw_util.disable_output(2)
    elif path == "/set_output2_times":
        await handle_set_output_times(writer, params, output_number=2)
    elif path == "/enable_output3":
        print("Enabling Output 3")
        hw_util.enable_output(3)
    elif path == "/disable_output3":
        print("Disabling Output 3")
        hw_util.disable_output(3)
    elif path == "/set_output3_times":
        await handle_set_output_times(writer, params, output_number=3)
    elif path == "/set_input1_threshold":
        await handle_set_input1_threshold(writer, params)
    elif path == "/set_input1_water_fill_time":
        await handle_set_input1_water_fill_time(writer, params)
    else:
        print(f"Unknown request path: {path}")

    # Generate the webpage
    response = generate_webpage()

    # Send the HTTP response
    writer.write("HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n")
    writer.write(response)
    await writer.drain()
    await writer.wait_closed()
    print('Client disconnected')

def parse_query_string(query_string):
    """
    Parse the query string or body into a dictionary.
    Handles URL decoding and multiple parameters with the same key.
    """
    params = {}
    if query_string:
        pairs = query_string.split('&')
        for pair in pairs:
            if '=' in pair:
                key, value = pair.split('=', 1)
                key = url_decode(key.strip())
                value = url_decode(value.strip())
                # Handle multiple values for the same key (e.g., checkboxes)
                if key in params:
                    if isinstance(params[key], list):
                        params[key].append(value)
                    else:
                        params[key] = [params[key], value]
                else:
                    params[key] = value
    return params

def url_decode(s):
    """
    Decode a URL-encoded string.
    """
    import ure as re  # Use 'ure' for MicroPython
    hex_pattern = re.compile('%([0-9A-Fa-f]{2})')
    return hex_pattern.sub(lambda m: chr(int(m.group(1), 16)), s.replace('+', ' '))

def convert_to_24h(hours, ampm):
    """
    Convert 12-hour time to 24-hour time.
    """
    if ampm.upper() == 'PM' and hours != 12:
        hours += 12
    elif ampm.upper() == 'AM' and hours == 12:
        hours = 0
    return hours

async def handle_set_output_times(writer, params, output_number):
    """
    Handle setting the on/off times and days for an output.
    """
    print(f"Setting Output {output_number} Times")

    # Extract parameters with default values
    on_hours = params.get('on-hours', '0')
    on_minutes = params.get('on-minutes', '0')
    on_ampm = params.get('on-ampm', 'AM')
    off_hours = params.get('off-hours', '0')
    off_minutes = params.get('off-minutes', '0')
    off_ampm = params.get('off-ampm', 'AM')
    days = params.get('days', [])

    # Ensure 'days' is always a list
    if not isinstance(days, list):
        days = [days]

    # Convert hours and minutes to integers
    try:
        on_hours = int(on_hours)
        on_minutes = int(on_minutes)
        off_hours = int(off_hours)
        off_minutes = int(off_minutes)
    except ValueError:
        # Handle invalid input
        print("Invalid time input")
        # Send error response
        response = "<html><body><h1>Invalid time input</h1></body></html>"
        writer.write("HTTP/1.0 400 Bad Request\r\nContent-Type: text/html\r\n\r\n")
        writer.write(response)
        await writer.drain()
        await writer.wait_closed()
        return

    # Validate the time values
    if not (1 <= on_hours <= 12 and 0 <= on_minutes <= 59 and
            1 <= off_hours <= 12 and 0 <= off_minutes <= 59):
        print("Time values out of range")
        response = "<html><body><h1>Time values out of range</h1></body></html>"
        writer.write("HTTP/1.0 400 Bad Request\r\nContent-Type: text/html\r\n\r\n")
        writer.write(response)
        await writer.drain()
        await writer.wait_closed()
        return

    # Convert to 24-hour format
    on_hours = convert_to_24h(on_hours, on_ampm)
    off_hours = convert_to_24h(off_hours, off_ampm)

    # Set the output times using your hardware utility functions
    hw_util.set_output_times(
        output=output_number,
        on_time=(on_hours, on_minutes),
        off_time=(off_hours, off_minutes),
        days=days
    )
    #print(f"Output {output_number} times set to on: {on_hours}:{on_minutes}, "f"off: {off_hours}:{off_minutes} on days {days}")

async def handle_set_input1_threshold(writer, params):
    """
    Handle setting the threshold time for Input 1.
    """
    print("Setting Input 1 Threshold Time")
    threshold_time = params.get('threshold-time', '0')
    try:
        threshold_time = int(threshold_time)
    except ValueError:
        print("Invalid threshold time input")
        response = "<html><body><h1>Invalid threshold time input</h1></body></html>"
        writer.write("HTTP/1.0 400 Bad Request\r\nContent-Type: text/html\r\n\r\n")
        writer.write(response)
        await writer.drain()
        await writer.wait_closed()
        return

    hw_util.set_water_sensor_threshold(threshold_time)
    print(f"Input 1 threshold time set to {threshold_time} minutes")

async def handle_set_input1_water_fill_time(writer, params):
    """
    Handle setting the water fill extended time for Input 1.
    """
    print("Setting Input 1 Water Fill Extended Time")
    water_fill_time = params.get('water-fill-time', '0')
    try:
        water_fill_time = int(water_fill_time)
    except ValueError:
        print("Invalid water fill time input")
        response = "<html><body><h1>Invalid water fill time input</h1></body></html>"
        writer.write("HTTP/1.0 400 Bad Request\r\nContent-Type: text/html\r\n\r\n")
        writer.write(response)
        await writer.drain()
        await writer.wait_closed()
        return

    hw_util.set_water_sensor_fill_overflow(water_fill_time)
    print(f"Input 1 water fill extended time set to {water_fill_time} minutes")