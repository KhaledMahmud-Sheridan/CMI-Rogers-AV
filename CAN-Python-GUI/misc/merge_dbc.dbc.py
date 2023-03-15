import canmatrix
import os
import sys


def merge_dbc_files(dbc_file_one, dbc_file_two):
    print(dbc_file_one)
    print(dbc_file_two)
    if dbc_file_one is None or dbc_file_two is None:
        print("Error: You must give two .dbc files as an argument.")
        return None
    elif not dbc_file_one.endswith(".dbc") or not dbc_file_two.endswith(".dbc"):
        print("Error: Both files must be .dbc files.")
        return None

    output_dbc = input("Please enter the merged filename to save: ")
    os.system(f"canconvert --merge={dbc_file_one} {dbc_file_two} {output_dbc}.dbc")
    return None


if __name__ == "__main__":
    merge_dbc_files(sys.argv[1], sys.argv[2])
