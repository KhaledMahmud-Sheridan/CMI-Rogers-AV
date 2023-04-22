import can
import cantools
import PyQt5

import encode_message
import load_dbc

buses = {}

try:
    buses["Virtual"] = can.interface.Bus(bustype="socketcan", channel="vcan0", bitrate=250000)
except:
    print("Not using virtual interface.")

try:
    buses["Physical"] = can.interface.Bus(bustype="socketcan", channel="can0", bitrate=500000)
except:
    print("Not using physical interface.")

def send_encoded_message(message_id, message_data, bus_type):
    """
    This function receives an encoded set of message data and a corresponding message ID to match, then sends that data
    out in the configured bus.

    :param bus_type:
    :param message_id:
    :param message_data:
    :return:
    """
    print(message_id)
    print(f"Message data is: {message_data}")
    bus = buses[bus_type]
    msg = can.Message(arbitration_id=message_id, data=message_data, is_extended_id=True)
    print(msg)
    try:
        bus.send(msg, 1)
        print(f"Message sent on {bus.channel_info}")
    except can.CanError as error:
        print(f"Error: {error}\nMessage not sent.")

def send_encoded_message_loop(message_id, message_data, bus_type):
    """
    This function receives an encoded set of message data and a corresponding message ID to match, then sends that data
    out in the configured bus.

    :param bus_type:
    :param message_id:
    :param message_data:
    :return:
    """
    print(message_id)
    print(message_data)
    bus = buses[bus_type]
    msg = can.Message(arbitration_id=message_id, data=message_data, is_extended_id=True)
    print(msg)
    try:
        bus.send_periodic(msg, 1)
        print(f"Message sent on {bus.channel_info}")
    except can.CanError as error:
        print(f"Error: {error}\nMessage not sent.")


if __name__ == "__main__":
    dbc = load_dbc.load_dbc("files/dbc/motohawk.dbc")
    message_parameters = encode_message.encode_message(dbc)
    parameter_id = message_parameters[0]
    parameter_data = message_parameters[1]
    send_encoded_message(parameter_id, parameter_data)

