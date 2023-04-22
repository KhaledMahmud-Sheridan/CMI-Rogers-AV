import CAN_Encoder_Decoder
import configuration
import CAN_Receiver_Sender
import DBC_Loader
import time
import datetime
import json
import threading
import read_supported_PIDs
import repository
import gps_reader


class DiagnosticRecorder:
    """
    The diagnostic recorder class is the central class of the application. It contains all the objects needed for
    logging OBD2 data from a CAN bus using the SocketCAN driver through a PCAN-USB CAN adapter and a DBC file.
    """

    def __init__(self, vin, device_id, auth):
        try:
            # Receive identification values from constructor arguments and add them to object.
            self.vin = vin
            self.device_id = device_id
            self.auth = auth

            # Initialize the signal collection class and signal index. signal_collection is the central list that
            # collects all logged data. Every index contains a single MongoDB document as per the obd2ts schema.
            # The signal_index variable tracks which indexes have been uploaded and saved. It is automatically
            # incremented whenever data is successfully saved and uploaded. At any time, the value of signal_index
            # will correspond to the index that the next inserted document will take. The first document is inserted
            # into index 0, which is the starting value of signal_index.
            self.signal_collection = []
            self.signal_index = 0

            # Create database access object for access to database through pymongo or API calls.
            self.database_access = repository.DatabaseAccess()

            # Create GPS reader object for reading GPS data.
            self.gps_reader = gps_reader.GPSReader(configuration.gps_port)

            # Instantiate receiverSender, dbc_loader, dbc, and messageDecoder objects. For more information, see
            # the respective modules for each class.
            self.receiverSender = CAN_Receiver_Sender.CanReceiverSender(configuration.current_channel)
            self.dbc_loader = DBC_Loader.DBCLoader(configuration.obd2_dbc_filepath)
            self.dbc = self.dbc_loader.dbc
            self.messageDecoder = CAN_Encoder_Decoder.EncoderDecoder(self.dbc)

            # Obtain initial vehicle settings from database (logParamSet, isActive, etc).
            self.vehicle = self.update_vehicle()

            # Instantiate supported param reader for reading supported OBD2 parameters on inital boot.
            self.supported_param_reader = read_supported_PIDs.SupportedParameterReader(self.dbc, self.receiverSender)

        except Exception as error:
            # Exception block if issue occurs during boot. Error is likely caused by not configuring SocketCAN
            # Error may also occur if OBD2 DBC file is not present in ./dbc/OBD2_standard.dbc location.
            print("Something went wrong when booting up the device.\nIt is possible that communication to your "
                  "vehicle's controller area network cannot be established.\nPlease power off the device, check your "
                  "installation, and try again.\nExiting...")
            # Exiting application if improperly configured. Logger must be configured correctly to function.
            exit()

    def update_vehicle(self):
        """
        This function is used to creation the vehicle dictionary that is used as the base model for the application.
        The vehicle dictionary contains all the information on the vehicle as specified in the authconfig.json file.
        This includes the vehicleInfo, logInfo, and userInfo objects from the MongoDB database. The vehicle dict is
        updated every upload cycle in order to ensure that the configuration settings are up-to-date.
        :return:
        """

        def create_dict_params(list_params):
            """
            This static function is used to create the restructure a list of logParamSet data and restructure it into a
            dictionary of logParamSet data with the name of the parameter as the key to the logParamSet dictionary.
            :param list_params:
            :return:
            """
            dict_params = {}
            for param in list_params:
                dict_params[param["name"]] = param
            return dict_params

        # Read vehicle data from database using vehicle identification number.
        vehicle = self.database_access.read_vehicle_by_vin_request(self.vin)
        print("Vehicle retrieved from database...")

        # Convert list logParamSet from database into dict logParamSet for easier processing further in application.
        vehicle["logInfo"]["logParamSet"] = create_dict_params(vehicle["logInfo"]["logParamSet"])

        # Return fully updated vehicle dictionary.
        return vehicle

    def log_diagnostic_data(self):
        """
        This is the central method in the application which is used to start the data logging process. It checks if
        the configured vehicle in the authconfig.json file has a availableParamSet with at least one element present.
        If no elements are present, this signifies that the vehicle has not been fully configured and must be scanned.
        This prompts the logger to scan the vehicle for a list of supported parameters, which it will be able to read
        when next the vehicle dictionary is updated with self.update_vehicle. If the vehicle has a list of available
        parameters and has the logActive field set to true, the logger will begin logging for OBD2 data. In between
        each cycle, the logger will wait for an amount of time as configured in the cloud.
        :return:
        """

        # Log continuously once application is started.
        while True:

            # If vehicle has no listed available parameters, scan for supported parameters.
            if len(self.vehicle["vehicleInfo"]["availableParamSet"]) == 0:
                print("No supported params detected, querying for supported params...")

                # Run obtain_supported_params method for supported parameters.
                list_available_params = self.supported_param_reader.obtain_supported_params()
                print("Supported Params:", list_available_params)

                # Update vehicle in database with scanned availableParamSet.
                self.database_access.update_vehicle_parameter_request(self.vin, list_available_params)

                print(f'Waiting {self.vehicle["logInfo"]["uploadInterval"]} seconds.')

                # Once scanned data is uploaded, wait the specified interval before updating the vehicle dict.
                time.sleep(self.vehicle["logInfo"]["uploadInterval"])

            # If vehicle has availableParamSet data and logActiev is true, scan for OBD2 parameters.
            elif self.vehicle["logInfo"]["logActive"] and self.vehicle["vehicleInfo"]["availableParamSet"]:
                print(f"Beginning {self.vehicle['logInfo']['uploadInterval']} second data logging cycle.")

                # Update self.signal_collection through self.begin_collection_interval call. Data is recorded for the
                # configured recording interval, and any received parameters are used to update the signal collection.
                self.begin_collection_interval()

                # Filler function to processing data before data is uploaded.
                self.process_data()

                # Save any recorded data in JSON format locally and upload to cloud for database storage.
                self.persist_data()

            # If logger is inactive, wait for the logger cycle time to expire and update vehicle configured settings.
            else:
                print(f"Logger inactive, going idle for {self.vehicle['logInfo']['uploadInterval']} seconds")
                time.sleep(self.vehicle["logInfo"]["uploadInterval"])

            # After each cycle, update self.vehicle() to ensure configuration settings are up-to-date.
            self.vehicle = self.update_vehicle()

    def begin_collection_interval(self):
        """
        This method is used to scan for any OBD2 parameters which have been broadcast on the CAN bus. It is called once
        for each logging cycle. It retrieves the signal dictionary for all logged parameters from the logging method,
        which contains all the parameters for one logging cycle and effectively makes up one parameterSet for each
        entry in an obd2ts collection. This dictionary is then added to the data dictionary, which is comprised of
        the timestamp and other meta data, and makes up one BSON document to be uploaded to the database.
        :return:
        """
        # Determine start time, then use start time to remain active until logging interval expires.
        upload_data_timer = time.time()
        while time.time() - upload_data_timer < self.vehicle["logInfo"]["uploadInterval"] \
                and self.vehicle["logInfo"]["logActive"]:

            # Record timestamp for timeseries document.
            timestamp = datetime.datetime.now()

            # Retrieve signal dictionary from logging method (this functions takes the logging interval to complete)
            signal_dictionary = self.begin_logging_interval()

            # Obtain GPS coordinates using GPS reader.
            gps_coordinates_dictionary = self.obtain_gps_coordinates()

            # If there are any logged OBD2 params from logging method, create structure for BSON document.
            if len(signal_dictionary.items()):
                data_dictionary = {
                    "vin": self.vin,
                    "scannerID": self.device_id,
                    "timestamp": timestamp,
                    "parameterSet": signal_dictionary,
                    "miscSet":
                        {
                            "gpsData": gps_coordinates_dictionary
                        }
                }
                # Append dictionary to signal collection if logged data is present.
                self.signal_collection.append(data_dictionary)

    def begin_logging_interval(self):
        """
        This function reads through the CAN channel on a loop for an amount of time equal to the
        CAN reading interval. Afterward, it constructs a dictionary of all the signals it has received,
        then returns that dictionary.
        :return:
        """
        print(f"Beginning {self.vehicle['logInfo']['logInterval']} second data read cycle.")

        # Use separate thread for sending OBD2 requests. OBD2 requests are sent from the logParamSet of the vehicle
        # dictionary to prompt the response of matching OBD2 responses. A separate thread is required such that the OBD2
        # responses on the CANbus can be read at the same time as the requests are send, as the CAN bus responses
        # quickly enough that the responses may be lost by the time the requests have been sent.
        send_thread = threading.Thread(target=self.send_obd2_requests)
        send_thread.start()

        # Record current time to ensure that channel reads CAN bus for the logging interval.
        read_data_timer = time.time()

        # Create the dictionary for holding logged OBD2 data.
        signal_dictionary = {}

        # Read bus until the passed time surpasses the logging interval.
        while time.time() - read_data_timer < self.vehicle["logInfo"]["logInterval"] and \
                self.vehicle["logInfo"]["logActive"]:

            # Each loop, read the CAN bus once.
            received_message = self.receiverSender.read_message()
            try:
                # Attempt to decode message using message decoder (returns dictionary of signal: value pairs).
                decoded_message = self.messageDecoder.decode_message(received_message)

                # Iterate through the returned signals from the decoded message dictionary.
                for key, value in decoded_message.items():

                    # If the signal is not in the vehicle's logParamSet, do not recorded received parameter.
                    if not self.vehicle["logInfo"]["logParamSet"].__contains__(key):
                        continue

                    # The data type of the OBD2 param value is NamedParameterValue, which cannot be uploaded to a BSON
                    # MongoDB database. Recorded parameters must be saved as numbers or strings instead.

                    # Attempt to save data first as integer (most OBD2 params are numerical).
                    try:
                        signal_dictionary[str(key)] = int(value)
                    # If parameter value is not numerical, save as a string.
                    except Exception as error:
                        signal_dictionary[str(key)] = str(value)

                    # Check signals against min and max values.
                    self.check_signal_range(key, value)
                    print(f"Found Signal: {{{key}: {value}}}")
            except Exception as error:
                # If an exception occurs, it indicates that the message is not OBD2, and should be ignored.
                pass
        # Return signal dictionary back to collection method.
        return signal_dictionary

    def send_obd2_requests(self):
        """
        This method sends the OBD2 requests needed to receive OBD2 responses.
        :return:
        """
        print("Sending parameter request codes...")
        # For each logParam, send correct OBD2 request.
        for parameter_data in self.vehicle["logInfo"]["logParamSet"].values():

            # Retrieve shallow copy of request data template.
            request = configuration.param_request_template.copy()

            # Add OBD2 parameter ID to 3rd byte of data tempate.
            request[2] = int(parameter_data["parameterID"], 16)
            print("Sending Request", request)

            # Send OBD2 request on bus (send numerous times to ensure transmission success).
            for i in range(0, 5):
                self.receiverSender.send_message(configuration.obd2_request_id, request)

                # Must wait 0.05 seconds before sending on CAN bus again.
                time.sleep(configuration.request_send_interval)

    def persist_data(self):
        """
        This method is used to save the logged data both locally and in the database.
        :return:
        """
        def write_data_to_json(collection):
            str_collection = str(collection)
            json_filename = f"readings_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
            print(f"Writing collected data to local JSON file: {json_filename}...")
            with open(f"{configuration.json_directory}{json_filename}", "w") as file:
                json.dump(str_collection, file, default=str)
            print("Data successfully saved!")

        # Declare None variable to attempt to assign collection to persist into.
        collection_to_persist = None
        try:
            # Add newly logged data to collection variable.
            collection_to_persist = self.signal_collection[self.signal_index:]
        except Exception as error:
            # If exception occurs, no new data has been added.
            pass

        # If there is data to be persisted, save it locally in JSON format and upload to database.
        if collection_to_persist:
            # Save data locally.
            write_data_to_json(collection_to_persist)
            # Save data in cloud.
            self.upload_to_database(collection_to_persist)

            # Update index of signal collection for next cycle of data logging.
            self.signal_index = len(self.signal_collection)
        else:
            print("No data to upload or save.")

    def upload_to_database(self, collection):
        """
        This small method uploads a collection of documents to the MongoDB database through platform API call.
        :return:
        """
        print("Uploading data to database...")
        # Use database access method to upload documents.
        self.database_access.create_documents_request(collection, self.auth)
        print("Data Upload successful!")

    def check_signal_range(self, signal_name, signal_value):
        """
        This method checks that a signal's value is within a certain range of that value's
        minimum and maximum values. Note that this method is a demo for a method which
        will perform more realistic data checking for predictive maintenance.
        :param signal_name:
        :param signal_value:
        :return:
        """
        # Obtain parameter from logParamSet.
        signal_range = self.vehicle["logInfo"]["logParamSet"][signal_name]
        # Obtain parameter ma and min from logParamSet.
        signal_range_length = signal_range["max"] - signal_range["min"]

        # Check if value is above safe threshold.
        if signal_value >= signal_range["max"] - (signal_range_length / 10):
            print(f"Alert: {signal_name}'s value of {signal_value} is above the safe threshold!")

        # Check if value is below safe threshold.
        elif signal_value <= signal_range["min"] + (signal_range_length / 10):
            print(f"Alert: {signal_name}'s value of {signal_value} is below the safe threshold!")

    def obtain_gps_coordinates(self):
        """
        This method is used to obtain a dictionary containing GPS coordinates through a gps reading object.
        This object will return a filler value set if GPS data cannot be obtained, or the lat and long values.
        :return:
        """
        dict_gps = {}
        # If GPS reader has been instantiated, attempt to retrieve GPS data.
        if self.gps_reader:
            # Retrieve GPS data from gps reader object.
            dict_gps = self.gps_reader.read_long_lat()
        # Return GPS data.
        return dict_gps

    def process_data(self):
        """
        This is a filler method for performing more in depth analysis of logged OBD2 data, which is unimplemented.
        :return:
        """
        pass


# Run script is main.py is the named module that is run.
if __name__ == "__main__":
    print("Welcome to the Diagnostic Logger!\nScanning for configuration settings...")

    # Open authconfig.json file for boot configuration settings.
    with open("misc/authconfig.json") as file:
        config = json.load(file)

    # If config settings are obtained, boot and run the logger.
    if config:
        print("Configuration settings detected")

        # Create variables for vin, scanner id and auth (used for validating upload permissions).
        vin = config["vin"]
        scanner_id = config["scannerID"]
        auth = {"userID": config["userID"],
                "userKey": config["userKey"],
                "email": config["email"]}

        print(f"Vin: {vin}\nScanner ID: {scanner_id}\nUser ID: {auth['userID']}\nUser Key: {config['userKey']}")

        # Instantiate logger object for running application.
        application = DiagnosticRecorder(vin, scanner_id, auth)
        print("Application initialized. Beginning logger...")

        # Begin logging diagnostic data.
        application.log_diagnostic_data()

    # If config settings are not present, exist out of the application without logging.
    else:
        print("Configuration settings not found. Please see the product manufacturer.")
    print("Exiting...")
    exit()

# def log_once(self):
# print(f"Beginning {configuration.upload_data_interval} second data logging cycle.")
#
# self.begin_collection_interval()
# self.write_data_to_json()
# self.upload_to_database()

# self.param_list = self.create_parameter_request_list()
# self.signal_ranges = self.create_signal_ranges()
# self.request_list = self.create_request_list()

#
# print("param_list")
# for param in self.param_list:
#     print(param)
# print("\n")

# print("signal ranges")
# for key, value in self.signal_ranges.items():vehicle["logActive"] =
# self.database_access.read_vehicle_by_vin_request(self.vin)["logActive"]
# print(key, ":", value)
# print("\n")

# print("request_list")
# for request in self.request_list:
# print(request)
# print("\n")

# print("\n")
# print("vehicle")
# for key, value in self.vehicle.items():
#     print(f"{key}: {value}")
# print("\n")
#
# print("parameter data")
# for key, value in self.vehicle["parameter_data_dict"].items():
#     print(f"{key}: {value}")
# print("\n")

#     def update_vehicle(self):
#         """Take data from parameter request and create parameter_data field in vehicle object"""
#
#         # def create_param_dict(param_list):
#         #     def create_param_id(param_full_name):
#         #         print(f"{param_full_name}: {type(int(param_full_name[7:9], 16))}")
#         #         return int(param_full_name[7:9], 16)
#         #
#         #     parameter_data_dict = {}
#         #     for param in param_list:
#         #         create_param_id(param["parameterName"])
#         #         parameter_data_dict[param["parameterName"]] = {"min": param["min"], "max": param["max"],
#         #                                                        "request_data": param["request_data"],
#         #                                                        "id": create_param_id(param["parameterName"])}
#         #     return parameter_data_dict
#
#         def create_parameter_list(vehicle):
#             parameter_request_list = []
#             for parameter in vehicle["logInfo"]["logParamSet"]:
#             # for parameter in vehicle["vehicleInfo"]["availableParamSet"]:
#                 parameter_returned = self.database_access.read_parameter_by_name_direct(parameter)
#                 if parameter_returned:
#                     parameter_request_list.append(parameter_returned)
#             return parameter_request_list
#
#         vehicle = self.database_access.read_vehicle_by_vin_request(self.vin)
#
#         param_list = create_parameter_list(vehicle)
#
#         # vehicle["parameter_data_dict"] = create_param_dict(param_list)
#         # self.database_access.update_vehicle_log_params(vehicle["parameter_data_dict"])
#         return vehicle
