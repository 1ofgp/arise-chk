#!/usr/bin/env python3

# version 1.0 March 2026

import os
import time
import board
import busio
import adafruit_ina260
import struct
import datetime
import logging  
import subprocess
import digitalio
import adafruit_bme680
import dust
import Adafruit_BBIO.ADC as ADC

logging.basicConfig(
    filename='ariseCHK_v1p0_log.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logging.info("Import Done") 

period = 1 # read ~ data every second
temperatureAverage = 50 # temperature averaging 
dodust = True

spi_setup = """
sudo config-pin P9_17 gpio
sudo config-pin P9_18 spi
sudo config-pin P9_21 spi
sudo config-pin P9_22 spi_sclk
"""


# os.environ["BLINKA_FORCEBOARD"] = "BEAGLEBONE_BLACK" # set up in service config file /etc/systemd/system/arise_logger.service



try:
    subprocess.run(['bash', 'c', spi_setup])
    spi = busio.SPI(board.SCLK, MOSI=board.MOSI, MISO=board.MISO)
    cs = digitalio.DigitalInOut(board.P9_17)  
    logging.info("SPI Init Done") 
except Exception as e:
    logging.error(f"Failed initialize SPI bus: {e}")
    exit()


i2c = None
ina260 = None


if dodust:
    logging.info("Dust is Controlled")
else:
    logging.info("Dust is NOT Controlled")

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
    bme680sensor = adafruit_bme680.Adafruit_BME680_SPI(spi, cs, baudrate=100000)
    bme680sensor.set_gas_heater(320, 150)
    logging.info("BME680 initialized successfully.")
except Exception as e:
    logging.error(f"Failed to initialize BME680: {e}")
    exit()

try:
    ADC.setup()
    dust.dust_led_off_hi_z()
    T0_pin =  "P9_39" 
    T1_pin =  "P9_40"
    T2_pin =  "P9_37" 
    T3_pin =  "P9_38"
    logging.info("Temperature and Dust Sensors initialized successfully.")
except Exception as e:
    logging.error(f"Failed to initialize Temperature and/or Dust Sensors: {e}")
    exit()


# 'd' = double (8 bytes) -- timestamp
# 'f' = float (4 bytes) -- current -- should be 2??
# 'f' = float (4 bytes) -- voltage -- should be 2????
# 'f' = float (4 bytes) -- bme680 temperature 
# 'f' = float (4 bytes) -- bme680 humidity
# 'f' = float (4 bytes) -- bme680 pressure 
# 'i' = int (4 bytes) -- bme680 gas -- resistance on Ohms (higher VOC concentration lower resistance)
# 'f' = float (4 bytes) -- temperature 0
# 'f' = float (4 bytes) -- temperature 1
# 'f' = float (4 bytes) -- temperature 2
# 'f' = float (4 bytes) -- temperature 3 (inside)
# 'f' = float (4 bytes) -- dust LED Off
# 'f' = float (4 bytes) -- dust LED On

# package size = 56 bytes

data_struct = struct.Struct('dfffffiffffff')




def get_hourly_filename():
    now = datetime.datetime.now()
    return now.strftime("logdata/sensors_data_UTC_%Y-%m-%d_%H.bin")

def get_temperature(pin):
    avg_raw = sum([ADC.read(pin) for _ in range(temperatureAverage)]) / temperatureAverage
    voltage = avg_raw * 1.8
    return (voltage - 0.5) * 100

# Get the initial filename and open the file
current_file_name = get_hourly_filename()
logging.info(f"Logging data to: {current_file_name}")

try:
    file_handle = open(current_file_name, 'ab') # 'a' = append, 'b' = binary
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

        # --- Read INA260 ---
        try:
            current = ina260.current
            voltage = ina260.voltage
        except Exception as e:
            logging.warning(f"Failed to read from INA260: {e}")
            current, voltage = 0.0, 0.0
            time.sleep(1)
            continue
        # --- Read BME680 ---
        try:
            bme680Temperature = bme680sensor.temperature
            bme680Humidity = bme680sensor.relative_humidity 
            bme680Pressure = bme680sensor.pressure 
            bme680Gas = bme680sensor.gas
        except Exception as e:
            logging.warning(f"Failed to read from BME680: {e}")
            bme680Temperature, bme680Humidity, bme680Pressure, bme680Gas = 0.0, 0.0, 0.0, 0.0 
            time.sleep(1)
            continue
        # --- Read Temperature ---
        try:
            T0 = get_temperature(T0_pin)
            T1 = get_temperature(T1_pin)
            T2 = get_temperature(T2_pin)
            T3 = get_temperature(T3_pin)
        except Exception as e:
            logging.warning(f"Failed to read temperature: {e}")
            T0, T1, T2, T3 = 0.0, 0.0, 0.0, 0.0 
            time.sleep(1)
            continue
      
        if dodust:
            # --- Read Dust ---
            try:
                dustLedOff, dustLedOn = dust.get_dust()
            except Exception as e:
                logging.warning(f"Failed to read dust: {e}")
                dustLedOff, dustLedOn = 0.0, 0.0
                time.sleep(1)
                continue
        else:
            dustLedOff, dustLedOn = 0.0, 0.0
        
        # ------------------------------------------
        timestamp = time.time() #system time,  no RTC 
      
        try:
            packed_data = data_struct.pack(timestamp, current, voltage, bme680Temperature, bme680Humidity, bme680Pressure, bme680Gas, T0, T1, T2, T3, dustLedOff, dustLedOn)
            file_handle.write(packed_data)
        except Exception as e:
            logging.error(f"Failed to write to file {current_file_name}: {e}")
     
        time.sleep(period)

except KeyboardInterrupt:
    logging.info("Stopping data logging (KeyboardInterrupt).")
finally:
    if file_handle and not file_handle.closed:
        logging.info(f"Ensuring file is closed: {current_file_name}")
        file_handle.close()