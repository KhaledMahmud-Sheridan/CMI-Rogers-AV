import sys
import can_decoding
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import (QMainWindow, QApplication, QLabel, QCheckBox, QComboBox, QListWidget, QLineEdit, QSpinBox,
                             QDoubleSpinBox, QSlider, QFontComboBox, QDial, QPushButton, QDialog, QDialogButtonBox,
                             QVBoxLayout, QFileDialog, QGridLayout, QWidget, QListWidgetItem)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Dialog Application")

        self.process_button = QPushButton("Process for Signals")
        self.process_button.clicked.connect(self.process_signals)

        self.dbc_button_file = QPushButton("DBC File")
        self.dbc_button_file.clicked.connect(self.select_dbc)
        self.dbc_label_file = QLineEdit("")
        self.dbc_label_file.setReadOnly(True)

        self.mf4_button_folder = QPushButton("MF4 File")
        self.mf4_button_folder.clicked.connect(self.select_mf4)
        self.mf4_label_folder = QLineEdit()
        self.mf4_label_folder.setReadOnly(True)

        self.list_signals = QListWidget()
        self.list_signals.setMinimumSize(QSize(self.size().width(), int(self.size().height() / 4)))
        self.list_signals.setMaximumSize(QSize(self.size().width(), int(self.size().height() / 2)))

        self.grid_layout = QGridLayout()
        self.grid_layout.addWidget(self.dbc_button_file, 0, 0)
        self.grid_layout.addWidget(self.dbc_label_file, 0, 1)
        self.grid_layout.addWidget(self.mf4_button_folder, 1, 0)
        self.grid_layout.addWidget(self.mf4_label_folder, 1, 1)
        self.grid_layout.addWidget(self.process_button, 2, 0, 1, 3)
        self.grid_layout.addWidget(self.list_signals, 3, 0, 3, 3)

        self.widget = QWidget()
        self.widget.setLayout(self.grid_layout)

        self.setCentralWidget(self.widget)

    def select_dbc(self):
        dbc_file = QFileDialog().getOpenFileName()
        self.dbc_label_file.setText(dbc_file[0].__str__())

    def select_mf4(self):
        # folderpath = QFileDialog.getExistingDirectory(self, 'Select Folder')
        mf4_file = QFileDialog.getOpenFileName()
        self.mf4_label_folder.setText(mf4_file[0].__str__())

    def process_signals(self):
        mf4_folder = self.mf4_label_folder.text()
        dbc_file = self.dbc_label_file.text()
        signal_list = can_decoding.example_decode_using_iterator_obd2(dbc_file, mf4_folder)
        counter = 0
        while counter < len(signal_list):
            self.list_signals.addItem(QListWidgetItem(signal_list[counter].__str__()))
            print(type(signal_list[counter]))
            counter = counter + 1


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
