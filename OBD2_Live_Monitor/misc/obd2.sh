echo "Running startup script." > /home/kyle/bootscripts/output.txt;
bash /home/kyle/PycharmProjects/OBD2_Live_Monitor/misc/setup_virtual_bus.sh >> /home/kyle/bootscripts/output.txt;
bash /home/kyle/PyCharmProjects/OBD2_Live_Monitor/misc/setup_gps_device.sh >> /home/kyle/bootscripts.output.txt;
echo "Successfully setup virtual bus!" >> output.txt;
cd /home/kyle/PycharmProjects/OBD2_Live_Monitor/
source env/bin/activate >> /home/kyle/bootscripts/output.txt;
echo "Successfully changed virtual environment." >> /home/kyle/bootscripts/output.txt;
# python3 /home/kyle/PycharmProjects/OBD2_Live_Monitor/dbc/OBD2_standard.dbc;
python3 main.py 

