import os
# -----------------------------------------------
# specify your InfluxDB details
influx_bucket = "defaultBucket"
# Use environment variable stored token to access InfluxDB bucket.
token = f"{os.getenv('Influx_OBD2')}"
influx_url = "https://us-east-1-1.aws.cloud2.influxdata.com"
org_id = "f86c8bfa5d323475"

# -----------------------------------------------
# specify devices to process from local disk via ["folder/device_id"] or S3 via ["bucket/device_id"]
devices = ["obd2-data-rogers-av/69703802"]

# -----------------------------------------------
# specify DBC paths and a list of signals to process ([]: include all signals)
# optionally include signal prefixes to make CAN ID, PGN and/or BusChannel explicit
dbc_paths = ["dbc_files/CSS-Electronics-OBD2-v1.4.dbc"]
signals = []
can_id_prefix = False
pgn_prefix = False
bus_prefix = False

# specify resampling frequency. Setting this to "" means no resampling (much slower)
res = "5S"

# -----------------------------------------------
# specify whether to load data from S3 (and add server details if relevant)
s3 = True
key = "AKIAVSSCGPRTTYXZLKX6"
secret = "isBBtBMXOO3EVONUftR0Y0JD1uIayAI2FAD6lxvY"
endpoint = "http://s3.us-east-1.amazonaws.com"  # e.g. http://s3.us-east-1.amazonaws.com or http://192.168.0.1:9000
region = "us-east-1" # only relevant if you are using more recent builds of MinIO S3 as the backend
# cert = "path/to/cert.crt"  # if MinIO + TLS, add path to cert and update utils.py/setup_fs to verify

# -----------------------------------------------
# if dynamic = True, data is loaded dynamically based on most recent data in InfluxDB - else default_start is used
dynamic = True
default_start = "2022-01-01 00:00:00"
days_offset = None  # offsets data to start at 'today - days_offset'. Set to None to use original timestamps

# if you're using data encryption, you can add the password below
pw = {"default": "password"}

# if you need to process multi-frame data, set tp_type to "uds", "j1939" or "nmea"
tp_type = ""
