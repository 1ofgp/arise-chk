#!/usr/bin/env python3

import sys
import os
import struct
import datetime

# Format of the binary data (Double timestamp, Float current, Float voltage)
# We need this only to count records in the summary.
RECORD_STRUCT = struct.Struct('dff')
RECORD_SIZE = RECORD_STRUCT.size

def print_usage():
    print("Usage: python3 combineDailySensorsLogs.py <YYYY-MM-DD> <FOLDER_PATH>")
    print("\nExample:")
    print("python3 combineDailySensorsLogs.py 2025-11-12 /home/debian/arise")

def combine_logs(target_date, folder_path):
    # Construct the full path for the output file
    # I updated the output name to match your "sensors" and "UTC" style
    output_filename = f"combined_sensors_data_UTC_{target_date}.bin"
    output_path = os.path.join(folder_path, output_filename)
    
    # Check if output file already exists to prevent accidental overwrites
    if os.path.exists(output_path):
        print(f"Warning: Output file '{output_path}' already exists.")
        response = input("Overwrite? (y/n): ")
        if response.lower() != 'y':
            print("Operation cancelled.")
            sys.exit(0)

    print(f"--- Combining logs for {target_date} in '{folder_path}' ---")
    
    files_found = 0
    total_bytes = 0
    
    # Open the output file in Write Binary mode
    with open(output_path, 'wb') as outfile:
        # Loop through all 24 hours of the day
        for hour in range(24):
            # Generate the expected filename based on your example: 
            # sensors_data_UTC_2025-11-19_15
            hour_str = f"{hour:02d}"
            
            # 1. Try the exact name you provided (no extension)
            base_name = f"sensors_data_UTC_{target_date}_{hour_str}"
            filename = base_name
            input_path = os.path.join(folder_path, filename)
            
            # 2. If that doesn't exist, try checking for a .bin extension just in case
            if not os.path.exists(input_path):
                if os.path.exists(input_path + ".bin"):
                    filename = base_name + ".bin"
                    input_path = input_path + ".bin"
            
            if os.path.exists(input_path):
                try:
                    # Open the hourly file in Read Binary mode
                    with open(input_path, 'rb') as infile:
                        # Read the entire content
                        data = infile.read()
                        # Write it to the master file
                        outfile.write(data)
                        
                        size = len(data)
                        total_bytes += size
                        files_found += 1
                        
                        # Calculate records in this chunk for display
                        records = size // RECORD_SIZE
                        print(f"Merged: {filename} ({records} records)")
                except Exception as e:
                    print(f"Error reading {filename}: {e}")
            else:
                # It's normal for some hours to be missing
                pass

    print("-" * 30)
    if files_found == 0:
        print("No files found for this date.")
        # Clean up the empty output file
        if os.path.exists(output_path):
            os.remove(output_path)
    else:
        total_records = total_bytes // RECORD_SIZE
        print(f"Success! Combined {files_found} files.")
        print(f"Total Data Size: {total_bytes} bytes")
        print(f"Total Records:   {total_records}")
        print(f"Saved to:        {output_path}")

if __name__ == "__main__":
    # Check for arguments (Script name + Date + Folder)
    if len(sys.argv) != 3:
        print_usage()
        sys.exit(1)
        
    date_arg = sys.argv[1]
    folder_arg = sys.argv[2]
    
    # Validate date format
    try:
        datetime.datetime.strptime(date_arg, '%Y-%m-%d')
    except ValueError:
        print("Error: Date must be in YYYY-MM-DD format.")
        sys.exit(1)
        
    # Validate folder path
    if not os.path.isdir(folder_arg):
        print(f"Error: The folder '{folder_arg}' does not exist or is not a directory.")
        sys.exit(1)
        
    combine_logs(date_arg, folder_arg)