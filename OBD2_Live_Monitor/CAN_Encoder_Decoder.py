class EncoderDecoder:
    """
    This class receives as argument a database object from the python-can library. Using this object, it provides
    CAN message decoding and encoding services for receiving and sending messages on the CAN bus.
    """
    def __init__(self, database):
        """
        This is the contructor for the EncoderDecoder. It receives only one argument, a DBC database object.
        :param database:
        """
        self.database = database

    def encode_message(self, signals, message_name):
        """
        This method is used to receives the signals and name of a given CAN message. It returns a dictionary containing
        the ID of the message and the correctly encoded data for the message located by the message name.
        :param signals:
        :param message_name:
        :return:
        """
        # Retrieve message from database using message name
        message_template = self.database.get_message_by_name(message_name)

        # Use message to obtain encoded data list and message id
        message_id = message_template.frame_id
        message_data = message_template.encode(signals, strict=False)

        # Return message ID and encoded message data.
        return {"Message_ID": message_id, "Message_Data": message_data}

    def decode_message(self, message_frame):
        """
        This method receives a message from which has been read from a CAN bus. It uses the database file to decode
        the message by using the message's frame ID to locate the decoding rules for the message data.
        :param message_frame:
        :return:
        """

        # Decode and return message data.
        decoded_message = self.database.decode_message(message_frame.arbitration_id, message_frame.data)
        return decoded_message

