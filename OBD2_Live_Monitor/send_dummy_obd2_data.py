import time
import configuration
import CAN_Receiver_Sender
import DBC_Loader
import CAN_Encoder_Decoder

# This module is used to send a series of OBD2 response messages. It is intended primarily for testing purposes.

if __name__ == "__main__":
    # Create CAN bus interacting objects.
    receiverSender = CAN_Receiver_Sender.CanReceiverSender(configuration.current_channel)
    dbc_loader = DBC_Loader.DBCLoader(configuration.obd2_dbc_filepath)
    database = dbc_loader.dbc
    messageDecoder = CAN_Encoder_Decoder.EncoderDecoder(database)
    message = database.get_message_by_name("OBD2")

    # Create initial list of signals to send.
    signal_name_list = []
    for signal in message.signals:
        if signal.name in configuration.parameter_request_dictionary.keys():
            signal_name_list.append(signal.name)

    # Create dict collecting signal data for sending (ID, index).
    signals_dict = {}
    for signal_name in signal_name_list:
        choice_index = 0
        while choice_index < len(message.signals[3].choices):
            try:
                if signal_name == message.signals[3].choices[choice_index]:
                    signals_dict[choice_index] = signal_name
                    break
                else:
                    choice_index = choice_index + 1
            except Exception:
                choice_index = choice_index + 1
    # Continuously use signal dictionary to endlessly send OBD2 responses according to configured upload interval.
    while True:
        print("Sending")
        # Create CAN signals for message sending.
        for index, signal in signals_dict.items():
            signal_dict = {
                'length': 255,
                'response': 15,
                'service': 1,
                'ParameterID_Service01': int(f"{index}"),
                f'{signal}': configuration.make_random_value()
            }
            # Encode signals using DBC file.
            encoded_obd2_message = messageDecoder.encode_message(signal_dict, "OBD2")
            try:
                # Send OBD2 response through CAN bus.
                receiverSender.send_message(encoded_obd2_message["Message_ID"], encoded_obd2_message["Message_Data"])
                print(f"Sent message: {signal}.")
            except Exception:
                pass
            # Wait 0.05 seconds before sending next response.
            time.sleep(configuration.request_send_interval)
        # Wait until upload interval expires before continuing to send OBD2 responses.
        time.sleep(configuration.read_data_interval)
