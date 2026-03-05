import struct
import datetime 
import sys


# 'd' = double (8 bytes) -- timestamp
# 'f' = float (4 bytes) -- current -- should be 2??
# 'f' = float (4 bytes) -- voltage -- should be 2????
# 'f' = float (4 bytes) -- bme680 temperature 
# 'f' = float (4 bytes) -- bme680 humidity
# 'f' = float (4 bytes) -- bme680 pressure 
# 'i' = int (4 bytes) -- bme680 gas -- resistance on Ohms (higher VOC concentration lower resistance)

data_struct = struct.Struct('dfffffiffffff')

record_size = data_struct.size  
filename_to_read = file_name = sys.argv[1]


all_readings = []

try:
    with open(filename_to_read, 'rb') as f:  # 'rb' = read binary
        while True:
            # Read one chunk of data (16 bytes)
            chunk = f.read(record_size)
            
            # If the chunk is empty, we've reached the end of the file
            if not chunk:
                break
                
            # Make sure we got a full chunk (in case of a partial write)
            if len(chunk) == record_size:
                # Unpack the binary data back into Python values
                unpacked_data = data_struct.unpack(chunk)
                all_readings.append(unpacked_data)

    print(f"Read {len(all_readings)} total records from {filename_to_read}")

    for i, (timestamp, current, voltage, bme680Temperature, bme680Humidity, bme680Pressure, bme680Gas, T0, T1, T2, T3, dustLedOff, dustLedOn) in enumerate(all_readings):


        # Convert epoch timestamp to a readable datetime object
        dt_object = datetime.datetime.fromtimestamp(timestamp)
        print(f"Record {i}: Time={dt_object} Current={current:.2f} mA, Voltage={voltage:.2f} V, bme680T = {bme680Temperature:.2f} C, bme680H = {bme680Humidity:.2f} %, bme680P = {bme680Pressure:.2f} hPa, bme680Gas = {bme680Gas} Ohm, T0 = {T1:.2f}, T0 = {T1:.2f}, T2 = {T2:.2f}, T3 = {T3:.2f}, dustLedOff = {dustLedOff:.2f}, dustLedOn = {dustLedOn:.2f}")

except FileNotFoundError:
    print(f"Error: File not found at {filename_to_read}")
except Exception as e:
    print(f"An error occurred: {e}")