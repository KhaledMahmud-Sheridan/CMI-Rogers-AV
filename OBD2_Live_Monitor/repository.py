import time
import pymongo
import configuration
import requests
import json


class DatabaseAccess:
    def __init__(self):
        self.connection = configuration.database_name
        self.database = self.setup_database_connection(configuration.connection_string)
        self.api_route = "http://192.168.56.1:3000"

    def setup_database_connection(self, connection_str):
        mongo_client = pymongo.MongoClient(connection_str)
        return mongo_client[self.connection]

    def read_vehicle_by_vin_direct(self, vin):
        return self.database.vehicles.find_one({"vehicleInfo.vin": vin})

    def read_parameter_by_name_direct(self, parameter_name):
        return self.database.parameters.find_one({"name": parameter_name})

    def create_documents_direct(self, documents):
        return self.database.measurements.insert_many(documents)

    def update_vehicle_parameter_direct(self, vin, list_avail_params):
        return self.database.vehicles.update_one({"vehicleInfo.vin": vin}, {"$set": {"vehicleInfo.availableParamSet": list_avail_params}})

    def read_vehicle_by_vin_request(self, vin):
        # result = self.read_vehicle_by_vin_direct(vin)
        result = requests.get(f"{self.api_route}/logdata/vehicle/vin/{vin}").json()["data"]
        return result

    def read_parameter_by_name_request(self, parameter_name):
        pass

    def create_documents_request(self, documents, auth):
        # self.create_documents_direct(documents)
        for document in documents:
            dict_document = {
                "auth": auth,
                "data": document
            }
            json_obj = json.dumps(dict_document, indent=4)
            result = requests.post(f"{self.api_route}/logdata/obd2ts/create", json=dict_document)
            time.sleep(configuration.request_send_interval)

    def update_vehicle_parameter_request(self, vin, list_avail_params):
        # result = self.update_vehicle_parameter_direct(vin, list_avail_params)
        str_request = f"{self.api_route}/logdata/vehicle/availparams/{vin}"
        result = requests.post(str_request, json=list_avail_params)
        return result


if __name__ == "__main__":
    database = DatabaseAccess()
    database.read_vehicle_by_vin_request(configuration.car_vehicle_identification_number)

