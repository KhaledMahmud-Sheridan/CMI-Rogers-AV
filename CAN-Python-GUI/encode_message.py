import cantools
from can.message import Message


def encode_message(signals, database, message_name):
    """
    This function receives a list containing the signals of a message to be encoded, as well as the message name and
    a corresponding database which has been previously loaded. It encodes the signals into the message's data bytes,
    and then returns a list containing the message's frame ID and the encoded data bytes.

    :param signals:
    :param database:
    :param message_name:
    :return:
    """
    message_template = database.get_message_by_name(message_name)
    message_id = message_template.frame_id
    message_data = message_template.encode(signals, strict=False)
    return [message_id, message_data]



