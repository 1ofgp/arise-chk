#!/usr/bin/env python3

import time
import board
import busio
import adafruit_ina260
import adafruit_ds3231
import struct
import datetime
import logging  


logging.basicConfig(
    filename='ariseCHK_log.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)



i2c = None
ina260 = None
rtc = None  

try:
    i2c = busio.I2C(board.SCL, board.SDA)
    logging.info("I2C bus initialized successfully.")
except Exception as e:
    logging.error(f"Failed to initialize I2C bus: {e}")
    exit()

try:
    ina260 = adafruit_ina260.INA260(i2c)
    logging.info("INA260 initialized successfully.")
except Exception as e:
    logging.error(f"Failed to initialize INA260: {e}")
    exit() 

try:
    rtc = adafruit_ds3231.DS3231(i2c)
    logging.info("DS3231 RTC initialized successfully.")
    t = rtc.datetime
    logging.info(f"Current RTC time: {t.tm_year}-{t.tm_mon}-{t.tm_mday} {t.tm_hour}:{t.tm_min}:{t.tm_sec}")
except Exception as e:
    logging.warning(f"Failed to initialize DS3231 RTC: {e}. Will use system time as fallback.")




# --- File Handling Logic ---

# 'd' = double (8 bytes) for epoch timestamp
# 'f' = float (4 bytes) for current
# 'f' = float (4 bytes) for voltage
data_struct = struct.Struct('dff')




def get_hourly_filename():
    """
    Generates a filename based on the current date and hour.
    It will try to use the reliable RTC time first.
    """
    # Try to use the reliable RTC time first
    if rtc:
        try:
            t = rtc.datetime  # Get time.struct_time from RTC

            # FIX: Create a datetime object from the valid parts of the struct_time
            # This avoids the tm_yday=0 error.
            dt_now = datetime.datetime(
                t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour
            )
            
            # Format the datetime object
            return dt_now.strftime("logdata/sensors_data_UTC_%Y-%m-%d_%H.bin")
            
        except Exception as e:
            logging.warning(f"Failed to read RTC for filename: {e}. Falling back to system time.")
    
    # Fallback to system time if RTC is None or if reading it failed
    now = datetime.datetime.now()
    return now.strftime("logdata/sensors_data_UTC_%Y-%m-%d_%H.bin")


# Get the initial filename and open the file
current_file_name = get_hourly_filename()
logging.info(f"Logging data to: {current_file_name}")

try:
    # Open in 'ab' mode: 'a' = append, 'b' = binary
    file_handle = open(current_file_name, 'ab')
except Exception as e:
    logging.error(f"Failed to open initial file {current_file_name}: {e}")
    exit() # Can't continue if we can't open the file

try:
    while True:
        # --- Check if the hour has changed ---
        new_file_name = get_hourly_filename()
        if new_file_name != current_file_name:
            # The hour has rolled over. Close the old file.
            logging.info(f"Hour changed. Closing file: {current_file_name}")
            file_handle.close()
            
            # Update the filename and open the new file
            current_file_name = new_file_name
            logging.info(f"Opening new file: {current_file_name}")
            try:
                file_handle = open(current_file_name, 'ab')
            except Exception as e:
                logging.error(f"Failed to open new file {current_file_name}: {e}")
                break # Exit the loop if we can't open the new file

        # --- Read INA260 Data ---

        try:
            current = ina260.current
            voltage = ina260.voltage
        except Exception as e:
            logging.warning(f"Failed to read from INA260: {e}")
            current, voltage = 0.0, 0.0  # Log 0.0 on failure
            # Skip this reading and try again after sleeping
            time.sleep(1)
            continue
        # --- Get Timestamp ---
        timestamp = 0.0
        if rtc:  # Check if the RTC object was successfully initialized
            try:
                # 1. Get the 'struct_time' object from the RTC
                t = rtc.datetime
                # 2. Convert it into a floating-point epoch timestamp
                timestamp = time.mktime(t)
            except Exception as e:
                logging.warning(f"Failed to read from RTC: {e}. Falling back to system time.")
                timestamp = time.time() # Use system time as a fallback
        else:
            # If RTC was never initialized, just use system time
            timestamp = time.time()
        # --- Write Data to Binary File ---
        try:
            packed_data = data_struct.pack(timestamp, current, voltage)
            file_handle.write(packed_data)
        except Exception as e:
            logging.error(f"Failed to write to file {current_file_name}: {e}")
            # Try to sleep and continue, maybe the disk issue is temporary
            
        # Wait for 1 second before the next reading
        time.sleep(1)

except KeyboardInterrupt:
    # This block runs if you press Ctrl+C to stop the script
    logging.info("Stopping data logging (KeyboardInterrupt).")
finally:
    # This block *always* runs, even if an error occurs.
    if file_handle and not file_handle.closed:
        logging.info(f"Ensuring file is closed: {current_file_name}")
        file_handle.close()