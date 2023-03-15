import pandas

dataframe_messages = pandas.read_csv("files/messages.csv")
# print(dataframe_messages)

for index, row in dataframe_messages.iterrows():
    print(f"{row['CAN ID']} {row['Data Bytes']} {row['Timestamp']}")

print("\n\nPrinting Signals\\nn")

dataframe_signals = pandas.read_csv("files/signals.csv")
for index, row in dataframe_signals.iterrows():
    print(f"{row['CAN_ID']} {row['Timestamp']} {row['Signal_Name']} {row['Signal_Data']}")

