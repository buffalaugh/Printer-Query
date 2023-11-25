from pysnmp.hlapi import *
from influxdb import InfluxDBClient
import json
import os

def snmp_get(ip, oid):
    error_indication, error_status, error_index, var_binds = next(
        getCmd(SnmpEngine(),
               CommunityData('public', mpModel=0),
               UdpTransportTarget((ip, 161)),
               ContextData(),
               ObjectType(ObjectIdentity(oid)))
    )

    if error_indication:
        print(f"Error: {error_indication}")
        return None
    elif error_status:
        print(f"Error: {error_status.prettyPrint()}")
        return None
    else:
        for var_bind in var_binds:
            value = var_bind[1]

            if isinstance(value, Integer32):
                return int(value)
            elif isinstance(value, OctetString):
                return value.prettyPrint()


    return None

def send_to_influxdb(client, printer_ip, oid, measurement_type, color):
    value = snmp_get(printer_ip, oid)

    if value is not None:
        measurement_name = f"{measurement_type}_pages_left_{color}"
        data = [
            {
                "measurement": measurement_name,
                "tags": {"printer_ip": printer_ip, "color": color},
                "fields": {"value": int(value)}
            }
        ]

        client.write_points(data)
    else:
        print(f"Error: No SNMP response received for printer {printer_ip}, color {color}")


influxdb_host = ''
influxdb_port = 8086
influxdb_database = ''
influxdb_username = ''
influxdb_password = ''

script_directory = os.path.dirname(os.path.realpath(__file__))

json_file_path = os.path.join(script_directory, 'printers.json')
try:
    with open(json_file_path, 'r') as file:
        printers_info = json.load(file)
except FileNotFoundError:
    print(f"Error: File not found - {json_file_path}")
    exit(1)
except json.JSONDecodeError as e:
    print(f"Error decoding JSON: {e}")
    exit(1)


client = InfluxDBClient(host=influxdb_host, port=influxdb_port, username=influxdb_username, password=influxdb_password, database=influxdb_database)

# Loop through printers and send data to InfluxDB
for printer_info in printers_info['printers']:
    printer_ip = printer_info['ip']

    # Toner values
    send_to_influxdb(client, printer_ip, printer_info['cyan_toner_oid'], 'toner', 'cyan')
    send_to_influxdb(client, printer_ip, printer_info['yellow_toner_oid'], 'toner', 'yellow')
    send_to_influxdb(client, printer_ip, printer_info['magenta_toner_oid'], 'toner', 'magenta')
    send_to_influxdb(client, printer_ip, printer_info['black_toner_oid'], 'toner', 'black')

    # Drum values
    send_to_influxdb(client, printer_ip, printer_info['cyan_drum_oid'], 'drum', 'cyan')
    send_to_influxdb(client, printer_ip, printer_info['yellow_drum_oid'], 'drum', 'yellow')
    send_to_influxdb(client, printer_ip, printer_info['magenta_drum_oid'], 'drum', 'magenta')
    send_to_influxdb(client, printer_ip, printer_info['black_drum_oid'], 'drum', 'black')

# Close the InfluxDB client connection
client.close()
