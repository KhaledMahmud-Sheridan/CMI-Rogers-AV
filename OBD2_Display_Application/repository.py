import pymongo
import requests
import configuration


def get_data_by_start_time_end_time_direct(str_vin, date_time_start, date_time_end):
    client = pymongo.MongoClient(configuration.connection_string)
    database = client["OBD2_DATA"]
    result = database.test_datas.find(
        {
            "vin": str_vin,
            "timestamp":
            {
                "$gte": date_time_start, "$lte": date_time_end
            }
        })
    return list(result)


def get_data_by_start_time_end_time_request(str_vin, date_time_start, date_time_end):
    str_request = f"{configuration.backend_url}/logdata/obd2ts/vin/{str_vin}/starttime/{date_time_start.__str__()}/endtime/{date_time_end.__str__()}/num/300"
    result = requests.get(str_request).json()["data"]
    print(result)
    return result

