#!/usr/bin/env python3
import time, statistics
import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.ADC as ADC

ADC_PIN = "P9_33"   # AIN4
LED_PIN = "P9_15"   # <-- set this to your actual LED control pin

R_TOP = 12000.0
R_BOTTOM = 10000.0
ADC_REF_V = 1.8

dustAverage = 10 # dust averaging

def dust_delay_us(us: int):
    target = time.perf_counter_ns() + us * 1000
    while time.perf_counter_ns() < target:
        pass

def dust_read_adc():
    ADC.read(ADC_PIN)      
    f = ADC.read(ADC_PIN)   
    return f

def undo_divider(v_adc):
    return v_adc * (R_TOP + R_BOTTOM) / R_BOTTOM

def dust_led_off_hi_z():
    GPIO.setup(LED_PIN, GPIO.IN)   # release (open-drain OFF)

def dust_led_on_sink():
    GPIO.setup(LED_PIN, GPIO.OUT)
    GPIO.output(LED_PIN, GPIO.LOW) # sink (open-drain ON)

def dust_sample_once():
    # OFF reading (baseline)
    dust_led_off_hi_z()
    dust_delay_us(50)
    v_off = dust_read_adc()

    # ON pulse + sample at ~280us
    dust_led_on_sink()
    dust_delay_us(280)
    v_on = dust_read_adc()
    dust_delay_us(40)
    dust_led_off_hi_z()

    # complete ~10ms frame (DFRobot uses 9680us after 280+40)
    dust_delay_us(9680)
    return v_off, v_on

def get_dust():
    offs, ons = [], []
    for _ in range(1):
        v_off, v_on = dust_sample_once()
        offs.append(undo_divider(v_off))
        ons.append(undo_divider(v_on))

    dustLedOff = statistics.mean(offs)
    dustLedOn  = statistics.mean(ons)
    return dustLedOff, dustLedOn

