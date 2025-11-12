#!/usr/bin/env python3

import sys
import time
import datetime
import board
import busio
import adafruit_ds3231

def print_usage():
    """Prints the correct way to use the script."""
    print("Error: Invalid arguments.")
    print("Usage: python3 set_rtc_from_args.py \"YYYY-MM-DD HH:MM:SS\"")
    print("Time should be in UTC")
    print("\nExample:")
    print("python3 set_rtc_from_args.py \"2025-11-12 16:50:00\"")
    print("\nNOTE: Remember to stop the 'arise_logger.service' first!")
    print("sudo systemctl stop arise_logger.service or sudo ./arise_logger_service_Stop.sh")

# --- Main script ---
if __name__ == "__main__":
    
    # Check if we have the correct number of arguments (script name + 1 string)
    if len(sys.argv) != 2:
        print_usage()
        sys.exit(1)

    time_string = sys.argv[1]
    time_format = "%Y-%m-%d %H:%M:%S"
    
    try:
        # 1. Parse the time string into a datetime object
        dt_obj = datetime.datetime.strptime(time_string, time_format)
        
        # 2. Convert the datetime object into a time.struct_time object
        #    The DS3231 library expects a struct_time.
        new_time_struct = dt_obj.timetuple()

        # 3. Initialize I2C and RTC
        i2c = busio.I2C(board.SCL, board.SDA)
        rtc = adafruit_ds3231.DS3231(i2c)

        # 4. Set the RTC time
        rtc.datetime = new_time_struct
        
        print(f"Successfully set RTC time to: {time_string}")

        # 5. Read back from RTC to confirm
        t = rtc.datetime
        print(f"Read back from RTC: {t.tm_year}-{t.tm_mon}-{t.tm_mday} {t.tm_hour}:{t.tm_min}:{t.tm_sec}")
        print("\nSync complete! You can now restart the logger.")
        print("sudo systemctl start arise_logger.service or sudo ./arise_logger_service_Restart.sh")

    except ValueError:
        print(f"\nError: The time string \"{time_string}\" does not match the format \"{time_format}\"")
        print_usage()
    except Exception as e:
        print(f"\nAn error occurred:")
        print(f"Details: {e}")
        print("Please ensure the logger service is stopped and the RTC is connected.")