# What is this application? 

This application is the software component for an in-vehicle data logging device intended for real-time collection of 
On-board Diagnostics II data. This application is intended to be run on a machine running either Ubuntu or another 
debian based operating system. In practice, it has been tested for use on a Raspberry Pi running Debian and a Linux
Virtual Machine running Ubuntu. 

This application is written in Python, and used numerous modules to connect to the related MongoDB database located in 
the cloud using MongoDB atlas. It can directly connect to this database through the pymongo library, or use 
the requests library to connect to the database through a Backend API server. A practical application of this device
should use the APIs for database access, for security purposes. 

# What are the modules for this application?

This application is composed of many different modules.

<ol> 
<li> Main.py: The central module for running the application and creating the main diagnostic recorder object. </li>

<li> CAN_Encoder_Decoder: This module contains the class necessary for encoding and decoding CAN messages. </li> 

<li> CAN_Receiver_Sender: This module contains the class necessary for sending and receiving CAN messages through the 
CAN bus. </li> 

<li> DBC_Loader: This module is used to load a DBC for using with decoding and encoding CAN messages, and iterating 
through CAN signals. The DBC file used in this application is a standard OBD2 DBC file for 11 bit ID messages. </li>

<li> GPS_Reader: This module is used to read a USB GPS Receiver to obtain the latitude and longitude from NMEA 
sentences and append these coordinates to the collected diagnostic data documents. </li>

<li> Read_Supported_PIDS: This module is used to scan a connected vehicle to obtain a list of OBD2 parameters 
which are supported by the vehicle. </li>

<li> Repository: This module contains the functions for accessing the cloud database through either direct access 
with pymongo or the backend API server endpoints with requests. </li>

<li> Configuration: This module contains all the configuration settings and default variables. It is used to cut down 
on redundant code and instantiate values in one place which are used throughout the application. </li>

<li> Send_Dummy_OBD2_Data: This module sends fake OBD2 responses through the CAN bus. It is intended for testing 
purposes only, and is never called during the application's main logical loop. </li>

</ol>

# How Do I Install the Necessary Python Packages? 

It is recommended to create a new virtual environment for this application. To do so, run the following command: 

"python -m venv env"

Afterwards, run the following command to activate the virtual environment: 

"source env/bin/activate"

To install the necessary Python packages into this virtual environment, use the following command: 

"pip install -r requirements.txt"

# How Do I Set Up This Application?

Running this application requires that a channel to the CAN bus be created using the built-in Linux CAN drivers, 
SocketCAN. To do this, attach the PCAN-USB device to a USB port of the machine, and run the setup_physical_bus.sh 
script in the misc folder with sudo privileges. 

"sudo bash misc/setup_virtual_bus.sh"

A virtual bus can be set up instead by running the setup_virtual_bus.sh 
script with sudo privileges. A virtual bus is fully functionally, but can only communicate between software on the host 
machine.

"sudo bash misc/setup_virtual_bus.sh"

For the connected GPS device to be read, the user of this script must have privileges to read the serial port file for
the receiver located in /dev/ttyACM0. To do so, run the setup_gps_device.sh script in the misc folder. 

"sudo bash misc/setup_gps_device.sh"

# How Do I Run This Application on Boot?

The logger is intended to boot up on launch on the host machine. As a result, it has no GUI for launching. 

To launch 
this application on boot, the user must add a line to their crontab with the crontab command to point to the obd2.sh 
file in the misc folder, which is the launch 
script of the application. The path for this script might be different on different host machines, and may require 
modification of the boot script. 

To configure this application to run on boot, the following command may be used: 

"sudo crontab -e"

The user must then add a new line to the bottom of their crontab file. 

"@REBOOT sudo bash PATH_TO_APPLICATION/OBD2_Live_Monitor/misc/obd2.sh"

# How Do I Set Up This Application On a Raspberry Pi?

Running this application on a Raspberry Pi requires additional configuration, as Raspian lacks the default support for 
CAN. To configure this application on a Raspian Pi, run the following commands: 

<ul>

<li> "sudo apt get update" </li>

<li> "sudo apt get upgrade" </li>

<li> "reboot" (this will reboot the machine) </li>

<li> "sudo apt-get install raspberrypi-kernel-headers" </li>

<li> "sudo apt-get install libpopt-dev" </li>

</ul>

Next, download the PCAN-USB drivers from the PCAN website. Use cd to change into the location of these drivers. 

<ul> 

<li> "tar -xzf peak-linux-driver-8.9.0.tar.gz" </li>

<li> "cd peak-linux-driver-8.9.0" </li>

<li> "make clean" </li>

<li> "make PCC=NO PCI=NO ISA=NO DNG=NO NET=NETDEV_SUPPORT" </li>

<li> "sudo make install" </li>

<li> "sudo modprobe pcan" </li>

</ul>

Additional information on this process can be found in <a href = "https://forum.peak-system.com/viewtopic.php?t=3381"> 
this thread.</a>
