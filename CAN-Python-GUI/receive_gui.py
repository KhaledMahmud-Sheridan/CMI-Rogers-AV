import bitstruct
import sys
import threading
import decode_message
import load_dbc
import receive_message
import playback_message_dialog
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtWidgets import QMainWindow, QApplication, QListWidget, QLineEdit, QFileDialog, QGridLayout, \
    QWidget, QPushButton, QDialog, QTableWidget, QTableWidgetItem, QComboBox, QLabel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Declare window title.
        self.setWindowTitle("CAN Message Recorder")

        # Initialize monospace font for clearer display
        self.mono_font = QFont("courier")
        self.setFont(self.mono_font)

        # Create initial filename and path for storing recorded messages and signals.
        self.message_filename = "files/messages.csv"
        self.signal_filename = "files/signals.csv"

        # Define initial empty filepath for DBC file
        self.dbc_filepath = ""

        # Define initial signal and message lists for storing recorded data.
        self.message_list = []
        self.signal_list = []

        # Define initial insertion point for the signal and message tables.
        self.signal_row_position = 0
        self.message_row_position = 0

        # Create structure for filter dictionaries to include or exclude messages.
        self.message_filters_dict = {"CAN_ID": [], "Timestamp": []}
        self.signal_filters_dict = {"CAN_ID": [], "Timestamp": [], "Signal_Name": []}
        self.message_include_dict = {"CAN_ID": [], "Timestamp": []}
        self.signal_include_dict = {"CAN_ID": [], "Timestamp": [], "Signal_Name": []}

        # Initialize channel as closed (not actively reading frames).
        self.is_open = False

        # Channel for opening connection and enabling reading of frames from CAN bus. Default is closed.
        self.open_button = QPushButton("Open Channel")
        self.open_button.clicked.connect(self.open_channel)
        self.open_button.setEnabled(True)

        # Button for closing connection and disabling reading of frames from CAN bus. Default is open.
        self.close_button = QPushButton("Close  Channel")
        self.close_button.clicked.connect(self.close_channel)
        self.close_button.setDisabled(True)

        # Button for outputting recorded signals and frames into .csv files.
        # TODO: Add file export dialog to customize output format and data.
        self.export_button = QPushButton("Export Messages")
        self.export_button.clicked.connect(self.export_messages)
        self.clear_button = QPushButton("Clear Messages")
        self.clear_button.clicked.connect(self.clear_messages)

        # Define label and button for selecting DBC file pathname.
        self.dbc_button_file = QPushButton("DBC File")
        self.dbc_button_file.clicked.connect(self.select_dbc_file)
        self.dbc_pathname_label = QLineEdit("")
        self.dbc_pathname_label.setReadOnly(True)

        # Button for displaying message playback dialog (used to repeat messages).
        self.playback_message_button = QPushButton("Playback Messages")
        self.playback_message_button.clicked.connect(self.playback_message)

        # Button for clearing filter dictionaries (removes all filters).
        self.reset_filters_button = QPushButton("Reset Filters")
        self.reset_filters_button.clicked.connect(self.reset_filters)

        # Button for displaying dialog to enter new exclusion signal filters.
        self.signal_filter_button = QPushButton("Exclude Signals")
        self.signal_filter_button.clicked.connect(self.filter_signals)

        # Button for displaying dialog to enter new exclusion message filters.
        self.message_filter_button = QPushButton("Exclude Messages")
        self.message_filter_button.clicked.connect(self.filter_messages)

        # Labels for displaying signal and message exclusion filters.
        self.message_filter_line = QLineEdit()
        self.message_filter_line.setReadOnly(True)
        self.signal_filter_line = QLineEdit()
        self.signal_filter_line.setReadOnly(True)

        # Button for displaying dialog to enter new inclusion message filters.
        self.message_include_button = QPushButton("Include Messages")
        self.message_include_button.clicked.connect(self.include_messages)

        # Button for displaying dialog to enter new inclusion signal filters.
        self.signal_include_button = QPushButton("Include Signals")
        self.signal_include_button.clicked.connect(self.include_signals)

        # Labels for displaying signal and message inclusion filters.
        self.message_include_line = QLineEdit()
        self.message_include_line.setReadOnly(True)
        self.signal_include_line = QLineEdit()
        self.signal_include_line.setReadOnly(True)

        # Define message display table and message display table size and appearance.
        self.table_messages = QTableWidget()
        self.table_messages.verticalHeader().setVisible(False)
        self.table_messages.setMinimumSize(QSize(int(self.size().width() * 1.3), int(self.size().height() / 2)))
        self.table_messages.setMaximumSize(QSize(int(self.size().width() * 1.3), int(self.size().height())))

        # Define number of columns in message display table.
        self.table_messages.setColumnCount(3)

        # Define size of message display table columns to 10%, 44.%, and 44.5% window size.
        self.table_messages.setColumnWidth(0, int(self.size().width() * 1.3 * .1))
        self.table_messages.setColumnWidth(1, int(self.size().width() * 1.3 * .445))
        self.table_messages.setColumnWidth(2, int(self.size().width() * 1.3 * .445))

        # Define headers for message display table.
        self.message_headers = ["CAN_ID", "Timestamp", "Data_Bytes"]
        self.table_messages.setHorizontalHeaderLabels(self.message_headers)
        self.table_messages.horizontalHeader().setVisible(True)

        # Define list widget for displaying contents of message list.
        self.message_list_widget = QListWidget()
        self.message_list_widget.setMinimumSize(QSize(int(self.size().width() * 1.3), int(self.size().height() / 2)))
        self.message_list_widget.setMaximumSize(QSize(int(self.size().width() * 1.3), int(self.size().height())))

        # Define signal display table and table size and appearance.
        self.table_signals = QTableWidget()
        self.table_signals.verticalHeader().setVisible(False)
        self.table_signals.setMinimumSize(QSize(int(self.size().width() * 1.3), int(self.size().height() / 2)))
        self.table_signals.setMaximumSize(QSize(int(self.size().width() * 1.3), int(self.size().height())))

        self.table_signals.setColumnCount(4)

        # Set signal column size to 10%, 30%, 30%, and 29% of window size.
        self.table_signals.setColumnWidth(0, int(self.size().width() * 1.3 * .1))
        self.table_signals.setColumnWidth(1, int(self.size().width() * 1.3 * .3))
        self.table_signals.setColumnWidth(2, int(self.size().width() * 1.3 * .3))
        self.table_signals.setColumnWidth(3, int(self.size().width() * 1.3 * .29))

        # Define name of signal display table headers.
        self.signal_headers = ["CAN_ID", "Timestamp", "Signal_Name", "Signal_Data"]
        self.table_signals.setHorizontalHeaderLabels(self.signal_headers)
        self.table_signals.horizontalHeader().setVisible(True)

        # Create and setup virtual or physical bus selection dropbox.
        self.bus_label = QLabel("Bus")
        self.bus_selection = QComboBox()
        self.bus_selection.addItems(["Virtual", "Physical"])
        self.bus_selection.currentIndexChanged.connect(self.update_bus)

        # Default bus set to virtual.
        self.current_bus = "Virtual"

        # Define grid layout.
        self.grid_layout = QGridLayout()

        # Assign widgets to layout.
        self.grid_layout.addWidget(self.dbc_button_file, 0, 0)
        self.grid_layout.addWidget(self.dbc_pathname_label, 0, 1, 1, 5)

        self.grid_layout.addWidget(self.open_button, 1, 0, 1, 3)
        self.grid_layout.addWidget(self.close_button, 1, 3, 1, 3)
        self.grid_layout.addWidget(self.clear_button, 2, 0, 1, 3)
        self.grid_layout.addWidget(self.export_button, 2, 3, 1, 3)

        self.grid_layout.addWidget(self.playback_message_button, 3, 0, 1, 3)
        self.grid_layout.addWidget(self.reset_filters_button, 3, 3, 1, 3)

        self.grid_layout.addWidget(self.message_filter_button, 4, 0, 1, 3)
        self.grid_layout.addWidget(self.signal_filter_button, 4, 3, 1, 3)
        self.grid_layout.addWidget(self.message_filter_line, 5, 0, 1, 3)
        self.grid_layout.addWidget(self.signal_filter_line, 5, 3, 1, 3)

        self.grid_layout.addWidget(self.message_include_button, 6, 0, 1, 3)
        self.grid_layout.addWidget(self.signal_include_button, 6, 3, 1, 3)
        self.grid_layout.addWidget(self.message_include_line, 7, 0, 1, 3)
        self.grid_layout.addWidget(self.signal_include_line, 7, 3, 1, 3)

        self.grid_layout.addWidget(self.table_messages, 8, 0, 3, 6)
        self.grid_layout.addWidget(self.table_signals, 12, 0, 5, 6)
        self.grid_layout.addWidget(self.bus_label, 17, 0, 1, 1)
        self.grid_layout.addWidget(self.bus_selection, 17, 1, 1, 6)

        # Set layout as window layout.
        self.widget = QWidget()
        self.widget.setLayout(self.grid_layout)
        self.setCentralWidget(self.widget)

        # Create thread to periodically check CAN bus channel and update view.
        update_thread = threading.Thread(target=self.update_timer)
        update_thread.start()

    def update_timer(self):
        """
        This method is called by a threading daemon, allowing it to check the selected channel periodically
        without causing lagging or holdups in the application.
        :return:
        """
        while True:
            if self.is_open:
                self.read_channel()

    def close_channel(self):
        """
        This method closes the channel if it was open, disables the close channel button,
        and enables the open channel button.
        :return:
        """
        self.is_open = False
        self.close_button.setDisabled(True)
        self.open_button.setDisabled(False)

    def open_channel(self):
        """
        This method opens the channel if it was closed, disables the open channel button,
        and enables the close channel button.
        :return:
        """
        self.is_open = True
        self.close_button.setDisabled(False)
        self.open_button.setDisabled(True)

    def read_channel(self):
        """
        This method reads the currently selected channel and then sends the recorded data to
        be displayed on the message display tables and signal display tables. If the data cannot
        be decoded using the selected DBC file, no data is appended to the signal table.
        :return:
        """
        message = receive_message.read_message(self.current_bus)
        if self.is_open:
            # Read selected bus and receieved message waiting in the buffer
            if message is not None:
                # If message exists, add message to the message list and display on table.
                self.message_list.append(message)
                self.update_message_table(message)

                # If a DBC file is selected, attempt to decode the message.
                if self.dbc_filepath:
                    database = load_dbc.load_dbc(self.dbc_filepath)
                    signal_dict = None

                    # Attempt to decode message using DBC file.
                    try:
                        signal_dict = decode_message.decode_message(message, database)
                    except KeyError as error:
                        pass
                        print(f"Cannot decode: {error}")
                    except bitstruct.Error as error:
                        print(f"Cannot decode: {error}")

                    # If signal is successfully decoded, append to signal display table.
                    if signal_dict is not None:
                        print(signal_dict)
                        self.update_signal_table(signal_dict, message)

    def select_dbc_file(self):
        """
        This method prompts the user with a file selection dialog for selecting a
        single DBC file. It does not allow the user to select multiple files, or
        select a file that does not end with the DBC file extension.
        :return:
        """
        dbc_filepath = QFileDialog.getOpenFileName()[0].__str__()
        if dbc_filepath.endswith(".dbc"):
            self.dbc_pathname_label.setText(dbc_filepath)
            self.dbc_filepath = self.dbc_pathname_label.text()
            print(f"You have selected: {self.dbc_filepath}")

    def export_messages(self):
        """
        This method exports the recorded messages and signals into a .csv file format.
        If there are no messages to export, it returns nothing and has no effect. It
        will override completely the contents of any preexisting .csv files.
        TODO: Add additional export dialog and improve and expand functionality.
        TODO: Allow for the importation of messages and the sending of message over http.
        :return:
        """
        if len(self.message_list) == 0:
            return None

        # Save messages to message file.
        with open(self.message_filename, "w") as file:
            for header in self.message_headers:
                file.write(f"{header},")
            file.write("\n")
            for message in self.message_list:
                message_data = message.data.__str__().strip('bytearray(').strip(")")
                message_timestamp = message.timestamp
                message_id = message.arbitration_id
                file.write(f"{message_id},{message_timestamp},{message_data}\n")

        # save signals to signal file.
        with open(self.signal_filename, "w") as file:
            for header in self.signal_headers:
                print(header)
                file.write(f"{header},")
            file.write("\n")
            for signal in self.signal_list:
                file.write(f"{signal[0]},{signal[1]},{signal[2]},{signal[3]}\n")

        return None

    def clear_messages(self):
        """
        This method clears all messages and signals from the display tables
        and storage lists.
        :return:
        """
        self.table_signals.setRowCount(0)
        self.table_messages.setRowCount(0)
        self.signal_row_position = 0
        self.message_row_position = 0
        self.signal_list.clear()
        self.message_list.clear()
        return None

    def update_bus(self):
        """
        This method allows for the changing of BUS from virtual to physical or vice versa.
        :return:
        """
        self.current_bus = self.bus_selection.itemText(self.bus_selection.currentIndex())
        print(self.current_bus)

    def playback_message(self):
        """
        This method displays the playback message dialog for the selective repeating of messages.
        :return:
        """
        if len(self.message_list) > 0:
            dlg = playback_message_dialog.PlaybackMessageDialog(self.message_list)
            dlg.exec()

    def filter_messages(self):
        """
        This method launches the message filter dialog for showing messages
        only if they exclude all the fields in the message exclusion filter.
        :return:
        """
        # Run the message filter dialog to gather filter dictionary.
        dlg = self.MessageFilterDialog()
        dlg.exec()

        # After dialog has closed, add new filters to main message filter dictionary.
        filters = dlg.get_filters()
        self.message_filters_dict["CAN_ID"].extend(filters["CAN_ID"])
        self.message_filters_dict["Timestamp"].extend(filters["Timestamp"])
        self.message_filter_line.setText(self.message_filters_dict.__str__())
        # Repopulate message table with new filters applied.
        self.populate_message_table()

    def filter_signals(self):
        """
        This method launches the signal filter dialog for showing signals
        only if they exclude all the fields in the signal exclusion filter.
        :return:
        """
        # Run the signal filter dialog to gather filter dictionary.
        dlg = self.SignalFilterDialog()
        dlg.exec()

        # After the dialog has closed, add new filters to main signal filter dictionary.
        filters = dlg.get_filters()
        self.signal_filters_dict["CAN_ID"].extend(filters["CAN_ID"])
        self.signal_filters_dict["Timestamp"].extend(filters["Timestamp"])
        self.signal_filters_dict["Signal_Name"].extend(filters["Signal_Name"])
        self.signal_filter_line.setText(self.signal_filters_dict.__str__())

        # Repopulate signal table with new filters applied.
        self.populate_signal_table()

    def include_signals(self):
        """
        This method launches the message filter dialog for showing signals
        only if they include all the fields in the signal inclusion filter.
        :return:
        """
        # Run the signal filter dialog to gather filter dictionary.
        dlg = self.SignalFilterDialog()
        dlg.exec()

        # After dialog has closed, add new filters to main signal filter dictionary.
        filters = dlg.get_filters()
        self.signal_include_dict["CAN_ID"].extend(filters["CAN_ID"])
        self.signal_include_dict["Timestamp"].extend(filters["Timestamp"])
        self.signal_include_dict["Signal_Name"].extend(filters["Signal_Name"])
        self.signal_include_line.setText(self.signal_include_dict.__str__())

        # Repopulate the signal table with new filters applied.
        self.populate_signal_table()

    def include_messages(self):
        """
        This method launches the signal filter dialog for showing messages
        only if they include all of the fields in the message inclusion filter.
        :return:
        """
        # Run the message filter dialog to gather filter dictionary.
        dlg = self.MessageFilterDialog()
        dlg.exec()

        # After dialog has closed, add new filters to main message filter dictionary.
        filters = dlg.get_filters()
        self.message_include_dict["CAN_ID"].extend(filters["CAN_ID"])
        self.message_include_dict["Timestamp"].extend(filters["Timestamp"])
        self.message_include_line.setText(self.message_include_dict.__str__())

        # Repopulate the message table  with new filters applied.
        self.populate_message_table()

    def reset_filters(self):
        """
        This method resets all inclusion and exclusion filters, thereby displaying all
        recorded messages regardless of content.
        :return:
        """
        self.message_filters_dict["CAN_ID"].clear()
        self.message_filters_dict["Timestamp"].clear()
        self.signal_filters_dict["CAN_ID"].clear()
        self.signal_filters_dict["Timestamp"].clear()
        self.signal_filters_dict["Signal_Name"].clear()
        self.message_include_dict["CAN_ID"].clear()
        self.message_include_dict["Timestamp"].clear()
        self.signal_include_dict["CAN_ID"].clear()
        self.signal_include_dict["Timestamp"].clear()
        self.signal_include_dict["Signal_Name"].clear()
        self.message_filter_line.clear()
        self.signal_filter_line.clear()
        self.message_include_line.clear()
        self.signal_include_line.clear()
        self.populate_message_table()
        self.populate_signal_table()

    def populate_message_table(self):
        """
        This method clears the current message table and repopulates it with the contents of the
        message list after checking it through the inclusion and exclusion filters.
        :return:
        """
        # Reset message table to empty.
        self.table_messages.setRowCount(0)
        self.message_row_position = 0

        # Iterate through message list to gether each message.
        for message in self.message_list:
            # Split each message into id, data, and time.
            message_data = message.data.__str__().strip('bytearray(').strip(")")
            message_id = message.arbitration_id
            message_time = message.timestamp

            # Skip adding message to table if message is in message exclusion filter.
            if message_id.__str__() in self.message_filters_dict["CAN_ID"] \
                    or message_time in self.message_filters_dict["Timestamp"]:
                continue

            # Skip adding message if message not in message inclusion filter and filter is not empty.
            if len(self.message_include_dict["CAN_ID"]) > 0 and message_id.__str__() not in self.message_include_dict[
                "CAN_ID"]:
                print("Excluding message: CAN ID")
                continue
            if len(self.message_include_dict["Timestamp"]) > 0 and \
                    message_time.__str__() not in self.message_include_dict["Timestamp"]:
                print("Excluding message: Timestamp")
                continue

            # Create table widgets for message id, data, and time.
            message_table_id = QTableWidgetItem(f"{message_id}")
            message_table_time = QTableWidgetItem(f"{message_time}")
            message_table_data = QTableWidgetItem(f"{message_data}")

            # Disable message table widget to prevent altering of values.
            message_table_id.setFlags(Qt.ItemIsEnabled)
            message_table_time.setFlags(Qt.ItemIsEnabled)
            message_table_data.setFlags(Qt.ItemIsEnabled)

            # Create new row on table and insert message widgets.
            self.table_messages.insertRow(self.message_row_position)
            self.table_messages.setItem(self.message_row_position, 0, message_table_id)
            self.table_messages.setItem(self.message_row_position, 1, message_table_time)
            self.table_messages.setItem(self.message_row_position, 2, message_table_data)

            # Increment row position for future insertions.
            self.message_row_position = self.message_row_position + 1

    def populate_signal_table(self):
        """
        This method clears the current signal table and repopulates it with the contents of the signal list
        after checking it through the inclusion and exclusion filters.
        :return:
        """
        # Reset signal table to empty.
        self.table_signals.setRowCount(0)
        self.signal_row_position = 0

        # Skip adding signal if signal in exclusion filter.
        for signal in self.signal_list:
            if signal[1].__str__() in self.signal_filters_dict["CAN_ID"] \
                    or signal[0].__str__() in self.signal_filters_dict["Timestamp"] \
                    or signal[2].__str__() in self.signal_filters_dict["Signal_Name"]:
                continue

            # Skip adding signal if signal data not in inclusion filter and filter is not empty.
            if len(self.signal_include_dict["CAN_ID"]) > 0 and signal[1] not in self.signal_include_dict["CAN_ID"]:
                continue
            if len(self.signal_include_dict["Timestamp"]) > 0 and signal[0] not in self.signal_include_dict[
                "Timestamp"]:
                continue
            if len(self.signal_include_dict["Signal_Name"]) > 0 and signal[2] not in self.signal_include_dict[
                "Signal_Name"]:
                continue

            # Insert new row
            self.table_signals.insertRow(self.signal_row_position)

            # Create table widgets populated by signal data.
            signal_id = QTableWidgetItem(f"{signal[1]}")
            signal_time = QTableWidgetItem(f"{signal[0]}")
            signal_key = QTableWidgetItem(f"{signal[2]}")
            signal_value = QTableWidgetItem(f"{signal[3]}")

            # Disable table widgets to prevent altering entries.
            signal_id.setFlags(Qt.ItemIsEnabled)
            signal_time.setFlags(Qt.ItemIsEnabled)
            signal_key.setFlags(Qt.ItemIsEnabled)
            signal_value.setFlags(Qt.ItemIsEnabled)

            # Insert signals into table.
            self.table_signals.setItem(self.signal_row_position, 0, signal_id)
            self.table_signals.setItem(self.signal_row_position, 1, signal_time)
            self.table_signals.setItem(self.signal_row_position, 2, signal_key)
            self.table_signals.setItem(self.signal_row_position, 3, signal_value)

            # Increment row count for future insertions.
            self.signal_row_position = self.signal_row_position + 1

    def update_message_table(self, message):
        """
        This method appends an additional message to the message table after checking it against the
        message inclusion and exclusion filters.
        :return:
        """
        # Split message into data, id, and time.
        message_data = message.data.__str__().strip('bytearray(').strip(")")
        message_id = message.arbitration_id
        message_time = message.timestamp

        # Skip adding message if present in exclusion filters.
        if message_id.__str__() in self.message_filters_dict["CAN_ID"] \
                or message_time in self.message_filters_dict["Timestamp"]:
            return None

        # Skip adding message if not present in inclusion filters and filters are not empty.
        if len(self.message_include_dict["CAN_ID"]) > 0 and message_id.__str__() \
                not in self.message_include_dict["CAN_ID"]:
            print("Excluding message: CAN ID")
            return None
        if len(self.message_include_dict["Timestamp"]) > 0 and \
                message_time.__str__() not in self.message_include_dict["Timestamp"]:
            print("Excluding message: Timestamp")
            return None

        # Create table widgets for message fields.
        message_table_id = QTableWidgetItem(f"{message_id}")
        message_table_time = QTableWidgetItem(f"{message_time}")
        message_table_data = QTableWidgetItem(f"{message_data}")

        # Disable message fields to prevent altering values.
        message_table_id.setFlags(Qt.ItemIsEnabled)
        message_table_time.setFlags(Qt.ItemIsEnabled)
        message_table_data.setFlags(Qt.ItemIsEnabled)

        # Insert message fields into new table row.
        self.table_messages.insertRow(self.message_row_position)
        self.table_messages.setItem(self.message_row_position, 0, message_table_id)
        self.table_messages.setItem(self.message_row_position, 1, message_table_time)
        self.table_messages.setItem(self.message_row_position, 2, message_table_data)

        # Increment message row count for future insertions.
        self.message_row_position = self.message_row_position + 1

    def update_signal_table(self, signal_dict, message):
        """
        This message appends an additional signal to the signal table after checking it
        against the signal inclusion and exclusion filters.
        :return:
        """
        # Split message into message id and time.
        message_id = message.arbitration_id.__str__()
        message_time = message.timestamp

        # Iterate through all signals decoded from message.
        for key, value in signal_dict.items():
            # Skip adding signal if present in exclusion filters.
            if message_id.__str__() in self.signal_filters_dict["CAN_ID"] \
                    or message_time.__str__() in self.signal_filters_dict["Timestamp"] \
                    or key.__str__() in self.signal_filters_dict["Signal_Name"]:
                continue
            # Skip adding signal if not present in inclusion filter and filter is not empty.
            if len(self.signal_include_dict["CAN_ID"]) > 0 and message_id not in self.signal_include_dict["CAN_ID"]:
                continue
            if len(self.signal_include_dict["Timestamp"]) > 0 and message_time not in self.signal_include_dict[
                "Timestamp"]:
                continue
            if len(self.signal_include_dict["Signal_Name"]) > 0 and key not in self.signal_include_dict["Signal_Name"]:
                continue

            # Append signal to signal list.
            self.signal_list.append([message_time, message_id, key, value])

            # Create new row in signal able for insertion.
            self.table_signals.insertRow(self.signal_row_position)

            # Create table widgets to insert signal values.
            signal_id = QTableWidgetItem(f"{message_id}")
            signal_time = QTableWidgetItem(f"{message_time}")
            signal_key = QTableWidgetItem(f"{key}")
            signal_value = QTableWidgetItem(f"{value}")

            # Disable signal values to prevent value alteration.
            signal_id.setFlags(Qt.ItemIsEnabled)
            signal_time.setFlags(Qt.ItemIsEnabled)
            signal_key.setFlags(Qt.ItemIsEnabled)
            signal_value.setFlags(Qt.ItemIsEnabled)

            # Insert signal widgets into table.
            self.table_signals.setItem(self.signal_row_position, 0, signal_id)
            self.table_signals.setItem(self.signal_row_position, 1, signal_time)
            self.table_signals.setItem(self.signal_row_position, 2, signal_key)
            self.table_signals.setItem(self.signal_row_position, 3, signal_value)

            # Increment row count for future insertion.
            self.signal_row_position = self.signal_row_position + 1

    class MessageFilterDialog(QDialog):
        """
        This class launches a dialog or adding additional filters to the message
        inclusion or exclusion filter dictionaries. This dialog is used for both
        inclusion and exclusion filters.
        """

        def __init__(self):
            super().__init__()
            # Create dictionary for holder filter values.
            self.filter_dict = {"CAN_ID": [], "Timestamp": []}

            # Set window title.
            self.setWindowTitle("Message ID Filters")

            # Create dropbox widget for selecting field.
            self.filter_dropbox = QComboBox()
            self.filter_dropbox.addItems(["CAN_ID", "Timestamp"])
            # Create line for entering filtered value.
            self.filter_line = QLineEdit("")

            # Create submit button to add field.
            self.filter_button = QPushButton("Add Filter")
            self.filter_button.clicked.connect(self.add_filter)

            # Use grid to orient layout.
            self.grid_layout = QGridLayout()

            # Add widgets to layout.
            self.grid_layout.addWidget(self.filter_dropbox, 0, 0)
            self.grid_layout.addWidget(self.filter_line, 0, 1, 1, 2)
            self.grid_layout.addWidget(self.filter_button, 1, 0, 1, 3)

            #  Set grid layout to default.
            self.setLayout(self.grid_layout)

        def add_filter(self):
            """
            This method takes the value added by the user and uses them to add an entry to the filter dictionary.
            :return:
            """
            key = self.filter_dropbox.currentText()
            self.filter_dict[key].append(self.filter_line.text())
            self.filter_line.clear()

        def get_filters(self):
            """
            This method returns the filter dictionary after the dialog has been closed.
            :return:
            """
            return self.filter_dict

    class SignalFilterDialog(QDialog):
        """
        This class launches a dialog for adding additional filters to the message
        inclusion or exclusion filter dictionaries.
        """

        def __init__(self):
            super().__init__()
            # Create dictionary for holding filter values.
            self.filter_dict = {"CAN_ID": [], "Timestamp": [], "Signal_Name": []}

            self.setWindowTitle("Signal Filters")

            # Create dropbox for selecting filtered field.
            self.filter_dropbox = QComboBox()
            self.filter_dropbox.addItems(["CAN_ID", "Timestamp", "Signal_Name"])

            # Create line for entering filter value.
            self.filter_line = QLineEdit("")

            # Create submit button for adding filter to dictionary.
            self.filter_button = QPushButton("Add Filter")
            self.filter_button.clicked.connect(self.add_filter)

            # Create grid layout for dialog.
            self.grid_layout = QGridLayout()

            # Add widgets to layout.
            self.grid_layout.addWidget(self.filter_dropbox, 0, 0)
            self.grid_layout.addWidget(self.filter_line, 0, 1, 1, 2)
            self.grid_layout.addWidget(self.filter_button, 1, 0, 1, 3)

            # Set grid layout as default.
            self.setLayout(self.grid_layout)

        def add_filter(self):
            """
            This method takes the user entered filtered field and value
            and adds them as an entry to the filter dictionary.
            :return:
            """
            key = self.filter_dropbox.currentText()
            self.filter_dict[key].append(self.filter_line.text())
            self.filter_line.clear()

        def get_filters(self):
            """
            This method returns the filter dictionary after the dialog has closed.
            :return:
            """
            return self.filter_dict


# Declare application.
app = QApplication(sys.argv)
# Declare main window.
window = MainWindow()
# Display window.
window.show()
# Execute application.
app.exec()
