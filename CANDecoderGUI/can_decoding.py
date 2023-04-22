import can_decoder
import mdf_iter
import fsspec
import glob
from pathlib import Path


def setup_fs():
    """
    Helper function to setup the file system for the examples.
    """
    from fsspec.implementations.local import LocalFileSystem

    fs = LocalFileSystem()

    return fs


def example_decode_using_iterator_obd2(dbc_path=None, log_file=None):
    """
    Example of loading a file and using the iterator to decode records as they are extracted.
    """
    fs = setup_fs()
    if dbc_path is None:
        # Specify path to the DBC file containing the decoding rules.
        dbc_list = glob.glob(f"{Path(__file__).parent.__str__()}/*dbc")
        dbc_path = Path(__file__).parent / "CSS-Electronics-OBD2-Extended-v1.4.dbc"

        for index, dbc_file in enumerate(dbc_list):
            print(f"{index + 1}. {dbc_file}")

        try:
            dbc_num = int(input("Which file would you like to use to decode: ")) - 1
            dbc_path = dbc_list[dbc_num]
        except IndexError:
            pass
        except ValueError:
            pass
        print("You have chosen {}".format(dbc_path))

        # Setup filesystem and which log file to decode.

    if log_file is None:
        device = "LOG/EEEE0005"
        log_file = "{}/00000001/obd2_data_from_van_extended_id.MF4".format(device)

        list_files = glob.glob(f"{device}/00000001/*.MF4")
        for index, file in enumerate(list_files):
            print(f"{index + 1}. {file}")

        try:
            log_num = int(input("Which file would you like to analyze: ")) - 1
            log_file = list_files[log_num]
        except IndexError:
            pass
        except ValueError:
            pass

    print("You have chosen {}".format(log_file))

    # Import the decoding rules.
    db = can_decoder.load_dbc(dbc_path, use_custom_attribute="S1_PID_0C_EngineRPM")

    with fs.open(log_file, "rb") as handle:
        # Open the file and extract an iterator for raw CAN records.
        mdf_file = mdf_iter.MdfFile(handle)

        raw_iterator = mdf_file.get_can_iterator()

        # Wrap the raw iterator with the decoder.
        wrapped_iterator = can_decoder.IteratorDecoder(raw_iterator, db)
        signal_list = [signal for signal in wrapped_iterator if signal.Signal in ["response", "length"]]
        ctr = 0
        # print(type(wrapped_iterator))
        for signal in wrapped_iterator:
            # The DBC file contains data for response type and length as well, which we skip.
            if signal.Signal in ["response", "length"]:
                continue
            print(signal)
            ctr += 1

        # print("Found a total of {} decoded messages".format(ctr))

        return signal_list

