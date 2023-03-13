import pandas
import pymongo
import json
import datetime

from utils import (
    setup_fs,
    load_dbc_files,
    list_log_files,
    ProcessData,
    MultiFrameDecoder,
    restructure_data,
    add_signal_prefix
)
from utils_db import SetupInflux
import inputs as inp

# initialize connection to InfluxDB + get latest data entries per device
influx = SetupInflux(inp.influx_url, inp.token, inp.org_id, inp.influx_bucket, inp.res)
start_times = influx.get_start_times(inp.devices, inp.default_start, inp.dynamic)

# setup filesystem (local/S3), load DBC files and list log files for processing
fs = setup_fs(inp.s3, inp.key, inp.secret, inp.endpoint, inp.region, passwords=inp.pw)
db_list = load_dbc_files(inp.dbc_paths)
log_files = list_log_files(fs, inp.devices, start_times, inp.pw)

# process log files and write extracted signals to InfluxDB
proc = ProcessData(fs, db_list, inp.signals, inp.days_offset)

for log_file in log_files:
    df_raw, device_id = proc.get_raw_data(log_file, inp.pw)

    if inp.tp_type != "":
        tp = MultiFrameDecoder(inp.tp_type)
        df_raw = tp.combine_tp_frames(df_raw)

    df_phys = proc.extract_phys(df_raw)

    # Save signal dataframe as .csv file.
    df_phys.to_csv("files/signals.csv", index=False)

    # Save signal dataframe as .txt file.
    with open("files/signals.txt", "w") as file:
        for index, row in df_phys.iterrows():
            file.write(f"{row}\n\n")

    # Save message dataframe as .csv file.
    df_raw.to_csv("files/messages.csv", index=False)

    df_phys = add_signal_prefix(df_phys, can_id_prefix=inp.can_id_prefix, pgn_prefix=inp.pgn_prefix,
                                bus_prefix=inp.bus_prefix)

    df_phys = restructure_data(df_phys, inp.res)

    # Save restructured dataframe as .csv file.
    df_phys.to_csv("files/influxdb_signals.csv", index=False)

    # Save restructure signal data from as .txt file.
    with open("files/influxdb_signals.txt", "w") as file:
        for index, row in df_phys.iterrows():
            file.write(f"{row}\n\n")

    # Convert Python datetime to BSON date format.
    list_times = []
    for index, row in df_phys.iterrows():
        date_thing = row.name.to_pydatetime()
        print(type(date_thing))
        list_times.append(date_thing)
    df_phys = df_phys.assign(timestamp=list_times)
    print(df_phys)

    # Convert dataframe to Python dictionary for MongoDV insertion.
    data = df_phys.to_dict(orient="record")

    # Push Data to MongoDB database.
    client = pymongo.MongoClient(
        "mongodb+srv://kyligalway:a1HtNaHBgwMaT5HD@rogersavcluster.nzrhiel.mongodb.net/?retryWrites=true&w=majority")

    # Specify collection to insert data into
    database = client["OBD2_DATA"]

    # Into data into measurements collection.
    database.measurements.insert_many(data)

