#!/bin/bash

if [ "$EUID" -ne 0 ]; then
  echo "Error: This script must be run with sudo."
  echo "Example: sudo ./taxiOFF.sh"
  exit 1
fi

echo "--- setting pin P9_42 as GPIO  ---"
echo

config-pin P9_42 gpio

if [ $? -eq 0 ]; then
  echo "config-pin: SUCCESS"
else
  echo "config-pin: FAIL"
fi

echo
echo "--- turning TAXI OFF  ---"
echo

gpioset --mode=signal --background gpiochip0 7=0


if [ $? -eq 0 ]; then
  echo "TAXI OFF: SUCCESS"
else
  echo "TAXI OFF: FAIL"
fi