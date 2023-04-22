import configuration
import serial
import pynmea2


class GPSReader:
    """
    This class provides the funcionality for receiving GPS data from a separate USB GPS module. It requires the GPS
    USB receiver to be connected to the serial number, which the user of the script must have access to. It reads the
    input from the receiver for a set amount of time until it times out or receives the correct NMEA sentence for GPS
    coordinates. If the coordinates are invalid, it indicates that the receiver cannot connect, and returns error
    values.
    """
    def __init__(self, serial_number):
        """Constructor for class."""
        try:
            # Attempt to create serial object. If fails, indicates that the receiver is not connected, or that
            # the user does not have the privileges to use the device, in which case the sudo user must add them.
            self.serial = serial.Serial(serial_number, 9600, timeout=1)
        except Exception as error:
            pass

    def read_long_lat(self):
        """
        This function use the GPS serial object to scan for GPS coordinates. If the GPS can connect to the satellite,
        it returns the current long and lat coordinates. Otherwise, it returns an error dictionary.
        :return:
        """
        dict_gps = {"long": "N/A", "lat": "N/A"}
        try:
            # Read 100 lines to search for correct NMEA sentence for long and lat.
            for i in range(0, 100):
                # Read raw GPS data to search for correct NMEA sentence for long and lat.
                gps_data_raw = self.serial.readline().decode("ascii", errors="replace")

                # Test if sentence begins with $GPGGA (sentence containing long and lat).
                if gps_data_raw.startswith("$GPGGA"):

                    # If sentence correct, obtain current long and lat coordinates.
                    gps_data_parsed = pynmea2.parse(gps_data_raw)
                    lat = gps_data_parsed.latitude
                    long = gps_data_parsed.longitude
                    print(f"Lat: {lat}")
                    print(f"Long: {long}")

                    # If long and lat are both 0.0, indicates satellite cannot connect.
                    if lat and long:
                        # Assign long and lat if connection successfully.
                        dict_gps["long"] = long
                        dict_gps["lat"] = lat
                        break
                    else:
                        # Assign error message is satellite cannot connect.
                        dict_gps["long"] = "Cannot connect."
                        dict_gps["lat"] = "Cannot connect."
                        break
        except Exception as error:
            print(error)

        # Return GPS data
        return dict_gps


if __name__ == "__main__":
    gps_reader = GPSReader(configuration.gps_port)
    # gps_reader.test_read_long_lat()
    "num_sv_in_view"
    dict_gps = gps_reader.read_long_lat()
    print(dict_gps)
