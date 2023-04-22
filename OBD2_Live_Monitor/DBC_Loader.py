import cantools


class DBCLoader:
    """
    This small class provides the DBC file needed to decode and encode CAN messages. A DBC file must be provided.
    """
    def __init__(self, dbc_filepath):
        self.dbc = cantools.db.load_file(dbc_filepath)
