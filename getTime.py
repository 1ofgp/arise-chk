#!/usr/bin/env python3

import board
import busio
import adafruit_ds3231
import datetime

i2c = busio.I2C(board.SCL, board.SDA)
rtc = adafruit_ds3231.DS3231(i2c)
t_rtc = rtc.datetime
print("RTC Time: ", t_rtc)
print("System Time: ", datetime.datetime.now())