# What is this application? 

This application is intended for testing the sending and receiving of CAN (controller area network) messages over a 
virtual bus. It is composed of two primary modules - receive_gui.py and send_obd2_gui.py, as well as related supporting
modules decode_message.py, encode_message.py, send_message.py, and receive_message.py. 

# What bus does this program interact with? 

While capable of being modified to use a real-world CAN network, this program is intended for testing the connection of 
a virtual interface setup via Linux. In order to change the bus used, the Bus object in the send_message and 
receive_message.py modules must be altered to a viable and configured alternative.

# How is the virtual bus initialized? 

In order to set up a virtual interface in Ubuntu, the following commands must be entered into the terminal: 

1. sudo modprobe vcan0
2. sudo ip link add dev vcan0 type vcan
3. sudo ip link set up vcan0

Alternatively, the setup_virtual_bus.sh bash script can be run.

# Where can this repository be located?

This repository is located at: https://github.com/GalwayK/CAN-Python-GUI

Please send a message if you require access.

