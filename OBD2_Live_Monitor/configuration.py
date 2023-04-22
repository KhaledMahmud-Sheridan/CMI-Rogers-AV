import random
import pymongo
import getmac

gps_port = "/dev/ttyACM0"
query_database = True
bus_type = "socket_can"
bitrate = 500000
database_name = "OBD2_DATA"
database_username = "obd2_test"
database_access_key = "nzEr7INXXiLuluiC"
connection_string = f"mongodb+srv://{database_username}:{database_access_key}@rogersavcluster.nzrhiel.mongodb.net/?retryWrites=true&w=majority"
truck_vehicle_identification_number = "ABCDEDG9876543210"
car_vehicle_identification_number = "test1234"
device_identification_number = getmac.get_mac_address()
key = "test_obd2@fakemail.ca"
is_vehicle_logging = True
json_filepath = "./files/collected_data.json"
json_directory = "./files/"
obd2_dbc_filepath = "./dbc/OBD2_standard.dbc"
virtual_channel = "vcan0"
physical_channel = "can0"
current_channel = virtual_channel
request_send_interval = 0.05
upload_data_interval = 120
read_data_interval = 60
obd2_request_id = 0x7DF
obd2_response_id = 0x7E8
dict_supported_pids = {
    "S1_PID_00_PIDsSupported_01_20": 0x00,
    "S1_PID_20_PIDsSupported_21_40": 0x20,
    "S1_PID_40_PIDsSupported_41_60": 0x40,
}
parameter_request_dictionary = {
    "S1_PID_2F_FuelTankLevel": [0x02, 0x01, 0x2F, 0x55, 0x55, 0x55, 0x55, 0x55],
    "S1_PID_05_EngineCoolantTemp": [0x02, 0x01, 0x05, 0x55, 0x55, 0x55, 0x55, 0x55],
    "S1_PID_0A_FuelPressure": [0x02, 0x01, 0x0A, 0x55, 0x55, 0x55, 0x55, 0x55],
    "S1_PID_0B_IntakeManiAbsPress": [0x02, 0x01, 0x0B, 0x55, 0x55, 0x55, 0x55, 0x55],
    "S1_PID_0C_EngineRPM": [0x02, 0x01, 0x0C, 0x55, 0x55, 0x55, 0x55, 0x55],
    "S1_PID_0D_VehicleSpeed": [0x02, 0x01, 0x0D, 0x55, 0x55, 0x55, 0x55, 0x55],
    "S1_PID_10_MAFAirFlowRate": [0x02, 0x01, 0x10, 0x55, 0x55, 0x55, 0x55, 0x55],
    "S1_PID_11_ThrottlePosition": [0x02, 0x01, 0x11, 0x55, 0x55, 0x55, 0x55, 0x55],
    "S1_PID_5E_EngineFuelRate": [0x02, 0x01, 0x5E, 0x55, 0x55, 0x55, 0x55, 0x55],
    "S1_PID_5C_EngineOilTemp": [0x02, 0x01, 0x5C, 0x55, 0x55, 0x55, 0x55, 0x55],
    "S1_PID_62_ActualEngTorqPct": [0x02, 0x01, 0x62, 0x55, 0x55, 0x55, 0x55, 0x55],
    "S1_PID_42_ControlModuleVolt": [0x02, 0x01, 0x42, 0x55, 0x55, 0x55, 0x55, 0x55],
    "S1_PID_33_AbsBaroPres": [0x02, 0x01, 0x33, 0x55, 0x55, 0x55, 0x55, 0x55],
    "S1_PID_04_CalcEngineLoad": [0x02, 0x01, 0x04, 0x55, 0x55, 0x55, 0x55, 0x55],
    "S1_PID_0F_IntakeAirTemperature": [0x02, 0x01, 0x0F, 0x55, 0x55, 0x55, 0x55, 0x55]
}
param_request_template = [0x02, 0x01, "REPLACE", 0x55, 0x55, 0x55, 0x55, 0x55]


def make_random_value():
    return random.randint(55, 65)

def make_connection():
    mongo_client = pymongo.MongoClient(connection_string)
    return mongo_client["OBD2_DATA"]


# {
#     "vin": "ABCDEDG9876543210",
#     "scannerID": "Scanner01",
#     "email": "client1@client1.com",
#     "userID":"user01ID",
#     "userKey":"user01key"
# }