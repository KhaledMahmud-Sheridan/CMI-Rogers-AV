import can

buses = {}
try:
    buses["Virtual"] = can.interface.Bus(bustype="socketcan", channel="vcan0", bitrate=250000)
except:
    print("Not using virtual interface.")

try:
    buses["Physical"] = can.interface.Bus(bustype="socketcan", channel="can0", bitrate=500000)
except:
    print("Not using physical interface.")

def send_request_message(message_id, message_data, bus_type):
    """
    This function receives an encoded set of message data and a corresponding message ID to match, then sends that data
    out in the configured bus.

    :param bus_type:
    :param message_id:
    :param message_data:dwad2
    :return:
    """
    print(message_id)
    print(message_data)
    bus = buses[bus_type]
    msg = can.Message(arbitration_id=message_id, data=message_data, is_extended_id=True)
    print(msg)
    try:
        bus.send(msg, 1)
        print(f"Message sent on {bus.channel_info}")
    except can.CanError as error:
        print(f"Error: {error}\nMessage not sent.")


if __name__ == "__main__":
    while True:
        # message_id = 0x7DF
        message_id = 0x18DB33F1
        message_data = {"EngineRPM": [0x2, 0x1, 12, 55, 55, 55, 55, 55],
                        "EngineLoad": [0x2, 0x1, 0x4, 55, 55, 55, 55, 55],
                        "EngineCoolantTemp": [0x2, 0x1, 0x5, 55, 55, 55, 55, 55],
                        "FuelPressure": [0x2, 0x1, 10, 55, 55, 55, 55, 55],
                        "VehicleSpeed": [0x2, 0x1, 13, 55, 55, 55, 55, 55]
                        }
        for index, key in enumerate(message_data.keys()):
            print(f"{index + 1}. {key}")

        data_name = input("Please enter the key of the data you would like to request: ")
        try:
            data_list = message_data[data_name]
            print(data_list)
            send_request_message(message_id, data_list, "Physical")
        except KeyError:
            print("Invalid value.")
            break


