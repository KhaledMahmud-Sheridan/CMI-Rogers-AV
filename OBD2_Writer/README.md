# What is this directory? 

This directory contains the Python scripts used to load CAN log files from an S3 Bucket using an S3 access key. The script, started by running the main.py script, first loads log files from the S3 bucket, then decodes this data using the CSS Electronic's CAN_decoder Python library. After the files have been decoded into dataframe format, this dataframe is transformed into a format more readable to a time series database. The data in this format is that entered into a Python dictionary, and then pushed to a MongoDB time series collection for later use. 

This script is predominantly based on the [CSS Electronic's InfluxDB Writer script](https://github.com/CSS-Electronics/canedge-influxdb-writer), which can be used as a reference to the setup and configuration of this script. 

In order for this script to be valid, a S3 Bucket must be configured, and an access key string with the relevant permissions must be used to read logged .mf4 files. In addition, an InfluxDB organization endpoint must be configured with a valid access key in order to write data to the selected table. 