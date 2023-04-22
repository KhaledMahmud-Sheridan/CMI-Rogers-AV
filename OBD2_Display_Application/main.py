import flask
from flask import Flask
import plotly.express
import pandas
import repository
import datetime

application = Flask(__name__)


@application.route("/", methods=["GET"])
def getIndex():
    return flask.render_template("index.html")


@application.route("/getVehicleInfo", methods=["GET"])
def getData():
    str_vin = flask.request.values["vin"]
    date_time_start = datetime.datetime.strptime(flask.request.values["start_time"], "%Y-%m-%dT%H:%M")
    date_time_end = datetime.datetime.strptime(flask.request.values["end_time"], "%Y-%m-%dT%H:%M")
    data_timeseries = repository.get_data_by_start_time_end_time_request(str_vin, date_time_start, date_time_end)
    # data_timeseries = repository.get_data_by_start_time_end_time_direct(str_vin, date_time_start, date_time_end)
    dict_data = {}
    for data in data_timeseries:
        print(data["timestamp"])
        for parameter, value in data["parameterSet"].items():
            if parameter not in dict_data.keys():
                dict_data[parameter] = {}
            if value:
                dict_data[parameter][data["timestamp"]] = value

    dict_graphs = {}
    for key, data in dict_data.items():
        dict_graphs[key] = plotly \
            .express.line(x=data.keys(), y=data.values(), labels={"x": key, "y": "Time Recorded"}, title=f"{key[10:]}")\
            .update_layout(title_x=0.5).to_html(full_html=False)

    message = f"Data Logged Between {date_time_start} and {date_time_end}" if len(dict_data.keys()) else \
        f"No Data Found Between {date_time_start} and {date_time_end}"

    return flask.render_template("index.html", dict_data={"dict_graphs": dict_graphs, "message": message})


if __name__ == "__main__":
    with application.app_context():
        application.run(debug=True, port=5001)

"""
TODO: ADD MESSAGE FOR NO RESULTS FOUND DONE

TODO: DO NOT DISPLAY LINE ON GRAPH FOR PERIODS WITH NO DATA 

TODO: CREATE STYLESHEET TO IMPROVE APPEARANCE OF WEBPAGE 

TODO: REPLACE DIRECT DATABASE CALL WITH BACKEND API CALL DONE
"""