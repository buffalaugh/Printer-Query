# Printer-Query
A simple Python Script to push printer consumable counters to an influx 1.X database using SNMP.

Currently Supporting:
Drum (CYMK) pages left
Toner (CYMK) pages left

Values for printers and SNMP OIDs will be taken from the printers.json file. Remember to place this file in the same directory as the script is located.
You will have to find the appropriate OID values for your printer. I recommend snmpwalk and grepping for known values to figure out which one is which.
If you happen to have a Xerox Versalink C600 you are in luck as the supplied printers.json file includes all the necessary OIDs

Enter your credentials in this section of the script:
influxdb_host = ''
influxdb_port = 8086
influxdb_database = ''
influxdb_username = ''
influxdb_password = ''
