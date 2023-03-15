import sys

import bitstruct
import can
import cantools
import PyQt5
import encode_message
import load_dbc
import send_message
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtWidgets import QMainWindow, QApplication, QListWidget, QLineEdit, QFileDialog, QGridLayout, QWidget, \
    QListWidgetItem, QPushButton, QDialog, QTableWidget, QTableWidgetItem, QLabel, QComboBox, QDoubleSpinBox, QSpinBox, \
    QHBoxLayout


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window title. 
        self.setWindowTitle("OBD2 Request Sender")

        # Fixed unalterable window size.
        self.setFixedSize(QSize(400, 200))

        # Label and dropbox for displaying virtual or physical bus to use. 
        self.bus_label = QLabel("Bus")
        self.bus_selection = QComboBox()
        self.bus_selection.addItems(["Virtual", "Physical"])
        self.bus_selection.currentIndexChanged.connect(self.update_bus)

        # Set default bus on appliation launch to virtual.
        self.current_bus = "Virtual"

        # Filepath label for reading DBC and constructing service and parameter 
        # options.
        self.dbc_filepath = "/home/kyle/PycharmProjects/CAN-Python-GUI/files/dbc/CSS-Electronics-OBD2-v1.4.dbc"
        self.dbc_file = load_dbc.load_dbc(self.dbc_filepath)

        # Select service parameters as choices to populate drop box.
        self.services = self.dbc_file.get_message_by_name("OBD2").signals[2].choices
        self.signal_index = 3
        self.service_parameter = "ParameterID_Service01"
        self.signals = self.dbc_file.get_message_by_name("OBD2").signals[self.signal_index].choices

        # Set default font to Couriter for monospace.
        self.mono_font = QFont("courier")
        self.setFont(self.mono_font)

        # Set length label to 255 (unknown effect if lower).
        self.length_label = QLabel("Length")
        self.length_line = QLineEdit("255")
        self.length_line.setReadOnly(True)

        # Set default length of bytes to 15 (unknown effect if lower).
        self.response_label = QLabel("Response")
        self.response_line = QLineEdit("15")
        self.response_line.setReadOnly(True)

        # Create service label widget for selectig service type.
        self.service_label = QLabel("Service")
        self.service_dropbox = QComboBox()

        # Add service modes to service selection dropbox.
        for index in range(1, len(self.services) + 1):
            self.service_dropbox.addItems([self.services[index].__str__()])

        # Create signal selection dropbox widget.
        self.signal_label = QLabel("Signal")
        self.signal_dropbox = QComboBox()

        # Add signals to signal selection dropbox.
        for index in range(0, len(self.signals) - 1):
            try:
                self.signal_dropbox.addItem(self.signals[index].__str__(), 
                userData=index)
            except KeyError:
                pass

        # If index of Service selection has changed, update parameters in 
        # parameter dropbox.
        self.service_dropbox.currentIndexChanged.connect(self.update_signals)

        # Create number widget for entering parameter value.
        self.value_label = QLabel("Value")
        self.value_line = QSpinBox()

        # TODO: Create min/max value based on parameter min/max field.
        self.value_line.setMinimum(-99999)
        self.value_line.setMaximum(99999)

        # Create and activate message send button.
        self.send_button = QPushButton('Send Request')
        self.send_button.clicked.connect(self.send_message)
        self.is_active = True

        # Create grid layout and add widgets to layout.
        self.grid_layout = QGridLayout()
        self.grid_layout.addWidget(self.length_label, 0, 0)
        self.grid_layout.addWidget(self.length_line, 0, 1, 1, 2)
        self.grid_layout.addWidget(self.response_label, 1, 0, 1, 1)
        self.grid_layout.addWidget(self.response_line, 1, 1, 1, 2)
        self.grid_layout.addWidget(self.service_label, 2, 0, 1, 1)
        self.grid_layout.addWidget(self.service_dropbox, 2, 1, 1, 2)
        self.grid_layout.addWidget(self.signal_label, 3, 0, 1, 1)
        self.grid_layout.addWidget(self.signal_dropbox, 3, 1, 1, 2)
        self.grid_layout.addWidget(self.value_label, 4, 0, 1, 1)
        self.grid_layout.addWidget(self.value_line, 4, 1, 1, 2)
        self.grid_layout.addWidget(self.send_button, 5, 0, 1, 3)
        self.grid_layout.addWidget(self.bus_label, 6, 0, 1, 1)
        self.grid_layout.addWidget(self.bus_selection, 6, 1, 1, 3)

        # Create central widget to hold applicationv iew. 
        self.widget = QWidget()
        self.widget.setLayout(self.grid_layout)
        self.setCentralWidget(self.widget)

    def update_signals(self):
        """
        This method activates whenever the service is changed in the 
        service selection dropbox, and causes the available parameters 
        to change to match the parameters of the current service. 
        """
        # Get current index of the service mode.
        service_index = self.service_dropbox.currentIndex()
        print(service_index)
        # Clear service dropbox for repopulation.
        self.signal_dropbox.clear()

        # Populate parameter dropbox with ParameterID_Service01 parameters.
        if service_index == 0:
            self.is_active = True
            print("Changing signals.")
            self.service_parameter = "ParameterID_Service01"
            self.signal_index = 3
            self.signals = self.dbc_file.get_message_by_name("OBD2").signals[self.signal_index].choices
            for index in range(0, len(self.signals) - 1):
                try:
                    self.signal_dropbox.addItem(self.signals[index].__str__(), userData=index)
                except KeyError:
                    pass

        # Populate parameter dropbox with ParameterID_Service02 parameters.
        elif service_index == 1:
            self.is_active = True
            print("Changing signals.")
            self.service_parameter = "ParameterID_Service02"
            self.signal_index = 4
            self.signals = self.dbc_file.get_message_by_name("OBD2").signals[self.signal_index].choices
            for signal in self.signals:
                try:
                    self.signal_dropbox.addItem(self.signals[signal].__str__(), userData=signal)
                except KeyError:
                    pass
        else:
            self.is_active = False

        self.signal_dropbox.setDisabled(not self.is_active)
        self.value_line.setReadOnly(not self.is_active)
        self.send_button.setDisabled(not self.is_active)

    def send_message(self):
        """"
        This method is activated when the send button is clicked. It 
        contructs a message from the message value field, attaches it 
        to a message using the service and parameter of the currently 
        selected service and parameter dropbox field, and sends it through 
        the virtual or physical can bus.
        """

        # Construct message from current application field values.
        message_length = self.length_line.text()
        message_response = self.response_line.text()
        message_service = self.service_dropbox.currentIndex() + 1
        message_parameter_service = self.service_parameter
        message_signal_key = self.signal_dropbox.itemData(self.signal_dropbox.currentIndex())
        message_signal_value = self.signal_dropbox.itemText(self.signal_dropbox.currentIndex())
        message_value = self.value_line.text()

        # Create dictionary containt message fields and parameters.
        message_plaintext_data = {"length": int(message_length),
                                  "response": int(message_response),
                                  "service": message_service,
                                  f"{message_parameter_service}": message_signal_key,
                                  f"{message_signal_value}": int(message_value)
                                  }
        print(message_plaintext_data)

        # Attempt to encode and send message into CAN channel.
        try:
            message_fields = encode_message.encode_message(message_plaintext_data, self.dbc_file, "OBD2")
            message_id = message_fields[0]
            message_encoded_data = message_fields[1]
            send_message.send_encoded_message(message_id, message_encoded_data, self.current_bus)
        except bitstruct.Error as error:
            # If message fails (invalid value) display error dialog and return.
            dlg = QDialog(self)
            dlg.setWindowTitle("Error Window")
            dlg_layout = QHBoxLayout()
            dlg_layout.addWidget(QLabel("Error: Invalid Signal Value"))
            dlg.setLayout(dlg_layout)
            dlg.exec()

    def update_bus(self):
        """
        This method launches whenever the bus is changed from a virtual 
        to a physical bus, or vice versa. It allows the user to send OBD2 
        response messages into either a virtual channel or a physical channel.
        """
        self.current_bus = self.bus_selection.itemText(self.bus_selection.currentIndex())
        print(self.current_bus)

# Create application.
app = QApplication(sys.argv)
# Instantiate MainWindow.
window = MainWindow()
# Display Main Window.
window.show()
# Execute application.
app.exec()
