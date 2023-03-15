import cantools
from can.message import Message


def decode_message(message_frame, database):
    """
    This method receives an encoded CAN message from and returns a dictionary containing its decoded contents.
    :param message_frame:
    :param database:
    :return:
    """
    decoded_message = database.decode_message(message_frame.arbitration_id, message_frame.data)
    return decoded_message


