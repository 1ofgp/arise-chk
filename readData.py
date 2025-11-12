import struct
import datetime 
import sys

# The same struct you used to write the data
# 'd' = double (timestamp), 'f' = float (current), 'f' = float (voltage)
data_struct = struct.Struct('dff')
record_size = data_struct.size  # This will be 16 bytes

# Make sure to change this to the file you want to read
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

    for i, (timestamp, current, voltage) in enumerate(all_readings):
        # Convert epoch timestamp to a readable datetime object
        dt_object = datetime.datetime.fromtimestamp(timestamp)
        print(f"Record {i}: Time={dt_object} Current={current:.2f} mA, Voltage={voltage:.2f} V")

except FileNotFoundError:
    print(f"Error: File not found at {filename_to_read}")
except Exception as e:
    print(f"An error occurred: {e}")