import load_dbc
import send_message

dbc = load_dbc.load_dbc("../files/dbc/honda.dbc")

message = dbc.get_message_by_name("HIGHBEAM_CONTROL")
print(message)

for signal in message.signals:
    print(signal)

message_data = {
    "ZEROS_BOH": 15,
    "ZEROS_BOH_2": 15,
    "AUTO_HIGHBEAMS_ACTIVE": 1,
    "HIGHBEAMS_ON": 1,
    "COUNTER": 1,
    "CHECKSUM": 1
}

encoded = message.encode(message_data)
send_message.send_encoded_message(message_id=message.frame_id, message_data=message_data, bus_type="Virtual")


