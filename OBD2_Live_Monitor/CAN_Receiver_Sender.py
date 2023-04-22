import can
import configuration
import DBC_Loader
import CAN_Encoder_Decoder
import time


class CanReceiverSender:
    """
    This class provides the sending and receiving functionality for CAN bus.
    """
    def __init__(self, channel):
        """
        This constructor instantiates the bus object with the argument channel (physical or virtual).
        :param channel:
        """
        # Create bus value
        self.bus = can.interface.Bus(bustype="socketcan", channel=channel, bitrate=500000)

    def read_message(self):
        """
        This method uses the bus read one CAN frame, and then returns that frame. This message must be decoded by the
        encoderDecoder.
        :return:
        """

        message_frame = self.bus.recv(timeout=1)
        return message_frame

    def send_message(self, message_id, message_data):
        """
        This method receives a message ID and message data, and transmits that message through the CAN bus.
        :param message_id:
        :param message_data:
        :return:
        """
        # Create message object with message ID and message data.
        message = can.Message(arbitration_id=message_id, data=message_data, is_extended_id=False)

        # Attempt to send message through CAN bus.
        try:
            self.bus.send(message, timeout=1)
        except can.CanError as error:
            print(f"Error: {error}\nMessage not sent.")
        except Exception as error:
            print(f"An error has occurred: {error}.\nMessage not sent.")


if __name__ == "__main__":
    # Create objects
    can_object = CanReceiverSender(configuration.virtual_channel)
    dbc_loader = DBC_Loader.DBCLoader(configuration.obd2_dbc_filepath)
    database = dbc_loader.dbc
    obd2_decoder = CAN_Encoder_Decoder.EncoderDecoder(database)

    # Send OBD2 request data
    for request_data in configuration.parameter_request_dictionary.values():
        can_object.send_message(configuration.obd2_request_id,
                                request_data)

    # Receive OBD2 response data
    start_time = time.time()
    while True:
        if (time.time() - start_time) >= 5:
            break

        message_received = can_object.read_message()
        if message_received is None:
            continue
        else:
            decoded_message = obd2_decoder.decode_message(message_received)
            print(decoded_message)

    print("Done.")
