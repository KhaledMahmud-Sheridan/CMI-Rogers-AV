import can
import cantools
import time
import threading
import configuration


class SupportedParameterReader:
    def __init__(self, database, receiver_sender):
        self.database = database
        self.receiver_sender = receiver_sender

    def send_queries(self, dict_ids):
        for key, value in dict_ids.items():
            request_data = configuration.param_request_template.copy()
            request_data[2] = value
            print(f"Sending {key}: {request_data}")
            for i in range(0, 2):
                self.receiver_sender.send_message(configuration.obd2_request_id, request_data)
                time.sleep(configuration.request_send_interval)
            time.sleep(1)

    def receive_responses(self):
        start_time = time.time()
        list_responses = []
        while time.time() - start_time < 8:
            response = self.receiver_sender.read_message()
            if response is not None and response.arbitration_id == 2024:
                decoded_data = self.database.decode_message(2024, response.data)
                list_responses.append(decoded_data)
        return list_responses

    def obtain_supported_params(self):

        def trim_dict_param(list_responses):
            dict_supported_PIDs = {}
            for response in list_responses:
                for key, value in response.items():
                    if key in ["length", "response", "service", "ParameterID_Service01"]:
                        continue
                    dict_supported_PIDs[key] = value
            return dict_supported_PIDs

        def obtain_list_params(dict_supported_PIDs, dict_choices):
            list_params = []
            num_index = 1
            for key, value in dict_supported_PIDs.items():
                response = {key: value}
                pid_bits = bin(response[key])[2:].zfill(32)

                for bit in pid_bits:
                    try:
                        print(f"{num_index}: {bit}: {dict_choices[num_index]}")
                    except KeyError as error:
                        print("Missing value detected!")

                    if bit == "1":
                        try:
                            list_params.append(dict_choices[num_index].__str__())
                        except Exception as error:
                            pass
                    num_index = num_index + 1
            print(list_params)
            return list_params

        db = cantools.db.load_file('./dbc/OBD2_standard.dbc')
        obd2_message = db.get_message_by_name("OBD2")

        dict_ids = configuration.dict_supported_pids

        send_thread = threading.Thread(target=self.send_queries, args=(dict_ids,))
        send_thread.start()

        list_responses = self.receive_responses()

        print(obd2_message.signals[3].choices)
        dict_choices = dict(obd2_message.signals[3].choices)
        print(dict_choices)

        dict_supported_PIDs = trim_dict_param(list_responses)

        list_params = obtain_list_params(dict_supported_PIDs, dict_choices)
        return list_params


if __name__ == "__main__":
    pass

