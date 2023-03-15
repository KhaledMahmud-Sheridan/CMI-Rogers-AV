import cantools
import send_message
from can.message import Message


def load_dbc(dbc_filepath):
    """
    This function receives a String filepath pointing to the location of a .dbc file, and then returns a dbc object
    created from that file. This object can then be used to encode or decode messages which have been sent or will
    be received.
    :param dbc_filepath:
    :return:
    """
    dbc = cantools.db.load_file(dbc_filepath)
    return dbc
