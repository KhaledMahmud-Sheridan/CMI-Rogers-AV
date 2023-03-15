import can
import cantools

buses = {}

try:
    buses["Virtual"] = can.interface.Bus(bustype="socketcan", channel="vcan0", bitrate=250000)
except:
    print("Not using virtual interface.")

try:
    buses["Physical"] = can.interface.Bus(bustype="socketcan", channel="can0", bitrate=500000)
except:
    print("Not using physical interface.")

def read_message(bus_type):
    """
    This method reads the designated bus and returns all raw messages it receives.
    This method provides no decoding utility, which must be provided by another script.
    :return:
    """
    bus = buses[bus_type]
    message_func = bus.recv(timeout=1)
    return message_func

