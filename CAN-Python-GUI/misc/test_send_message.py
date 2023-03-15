import cantools
import can

import decode_message

"""
This module is intended to test the entirety of the transmission process using the python-can and can-tools 
libraries. It is functional and unorganized in nature and should not be used for any actual transmission purposes.
"""

def send_test_message(id, data):
    """
    This function sends out an arbitrary message without any meaning for use to test bus transmission capability.
    :return:
    """
    bus_send = can.interface.Bus(bustype='socketcan', channel='vcan0', bitrate=250000)
    msg = can.Message(arbitration_id=id, data=data, is_extended_id=False)
    try:
        bus_send.send_periodic(msg, 1)
        print(f"Message sent on {bus_send.channel_info}")
    except can.CanError:
        print("Message not sent.")


db = cantools.db.load_file("../files/dbc/CANExplorerDatabase.dbc")
print(db)

message_template = db.get_message_by_name("Message_A")
print(message_template.signals)

# signals = message_template.signals
# print(type(signals))
# print(signals[2].choices)
# print(signals[3].choices)

message_data = {
    "Signal_PWM": 100,
    "Signal_Step_Counter": 100
}

message_id = message_template.frame_id
message_encoded_data = message_template.encode(message_data)

# print(message_encoded_data)

send_test_message(message_id, message_encoded_data)

bus_receive = can.interface.Bus(bustype="socketcan", channel="vcan0", bitrate=250000)

received_message = bus_receive.recv(timeout=1)

decoded_message = decode_message.decode_message(received_message, database=db)
print(decoded_message)
