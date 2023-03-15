from PyQt5.QtWidgets import QDialog, QGridLayout, QLabel, QComboBox, QPushButton, QSpinBox

import send_message


class PlaybackMessageDialog(QDialog):
    def __init__(self, messages):
        super().__init__()

        self.setWindowTitle("Message Playback")

        self.grid_layout = QGridLayout()

        self.messages = messages
        self.message_label = QLabel("Message: ")
        self.message_list = QComboBox()

        self.number_label = QLabel("# of Messages: ")
        self.number_spinbox = QSpinBox()
        self.number_spinbox.setValue(1)
        self.number_spinbox.setMinimum(1)
        self.number_spinbox.setMaximum(10)

        self.bus_label = QLabel("Bus: ")
        self.bus_list = QComboBox()
        self.bus_list.addItems(["Physical", "Virtual"])

        for message in messages:
            message_data = message.data.__str__().strip('bytearray(').strip(")")
            self.message_list.addItem(f"CAN ID: {message.arbitration_id} Message Data: {message_data}")

        self.send_button = QPushButton("Playback Message")
        self.send_button.clicked.connect(self.playback)

        self.send_loop_button = QPushButton("Playback Message On Loop")
        self.send_loop_button.clicked.connect(self.playback_loop)

        self.grid_layout.addWidget(self.message_label, 0, 0)
        self.grid_layout.addWidget(self.message_list, 0, 1, 1, 2)
        self.grid_layout.addWidget(self.bus_label, 1, 0)
        self.grid_layout.addWidget(self.bus_list, 1, 1, 1, 2)
        self.grid_layout.addWidget(self.number_label, 2, 0, 1, 1)
        self.grid_layout.addWidget(self.number_spinbox, 2, 1, 1, 2)
        self.grid_layout.addWidget(self.send_button, 3, 0, 1, 3)
        self.grid_layout.addWidget(self.send_loop_button, 4, 0, 1, 3)

        self.setLayout(self.grid_layout)

    def playback(self):
        message = self.messages[self.message_list.currentIndex()]
        bus = self.bus_list.currentText()
        for i in range(int(self.number_spinbox.text())):
            send_message.send_encoded_message(message.arbitration_id, message.data, bus)

    def playback_loop(self):
        message = self.messages[self.message_list.currentIndex()]
        bus = self.bus_list.currentText()
        send_message.send_encoded_message_loop(message.arbitration_id, message.data, bus)
