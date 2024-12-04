# PondPi: Pond Fountain Controller

A lightweight and simple open-source controller for your backyard pond, powered by the Raspberry Pi Pico W. PondPi allows you to manage your pond's pumps and water fill system using a local network interface.

This is my first project using Raspberry Pi so expect bugs, unoptimized code, and other such occurences but from my testing works pretty good.
Will be adding pictures for how to set up if anyone else would like to use this for a backyard pond. 


---

## Features

- **Timer-Based Control**
  - Adjustable 24-hour timer for automated operation.
  - Day-specific control for enhanced scheduling flexibility.

- **Input and Output Handling**
  - **Inputs:**
    - Float Switch: Monitor water levels in the pond.
  - **Outputs:**
    - Pump 1: Primary pond pump.
    - Pump 2: Secondary pond pump or auxiliary system.
    - Water Fill: Automatic water refilling system.

- **Local Network Interface**
  - Device IP address and port are displayed on startup.
  - Control and configure your system via your local network. (Requires modification of network_util.py)

---

## Requirements

### Hardware

- **Raspberry Pi Pico W**
- **Solid State Relays (SSRs)**
  - Used for controlling the pumps and water fill system.
  - Note: Not the most practical solution but suitable for this project.
- **Float Switch**
  - For monitoring water levels in the pond.

### Software

- **MicroPython**
  - Ensure your Raspberry Pi Pico W is set up with MicroPython.

---

## Circuit Diagram

Below is the circuit setup used for PondPi:

```
             +-----------------------+
             |    Raspberry Pi Pico  |
             +-----------------------+
  GPIO Pins: |                       |
    Float  --> [ Input ]             |
    Pump 1 --> [ Output ] -- SSR --> Pump 1
    Pump 2 --> [ Output ] -- SSR --> Pump 2
 Water Fill --> [ Output ] -- SSR --> Valve
             +-----------------------+
```

## Installation

1. **Set Up MicroPython**  
   Flash your Raspberry Pi Pico W with MicroPython. Instructions can be found [here](https://micropython.org/).

2. **Upload the Code**  
   Copy the `main.py` and all other files to your Raspberry Pi Pico W using an IDE like Thonny.

3. **Connect the Hardware**  
   Wire the float switch, pumps, and water fill system to the Raspberry Pi Pico W GPIO pins through the Solid State Relays.

4. **Run the Controller**  
   Power up the Raspberry Pi Pico W. The IP address and port for the device will be displayed on startup.

---

## Configuration

- Adjust the 24-hour timer and date-specific scheduling through the local network interface.
- Access the web interface using the IP and port displayed at startup.

---

## Contribution

This project is open-source! Feel free to fork, modify, and contribute to the development of PondPi. Share your ideas and improvements.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

Enjoy your automated pond system! 🌊

---

For more details or support, visit [nhrobertson.com](https://nhrobertson.com/).
