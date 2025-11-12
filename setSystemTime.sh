#!/bin/bash

# This script allows you to manually set the system time.
# It must be run as root (using sudo) to work.

# Check if the script is being run as root
if [ "$EUID" -ne 0 ]; then
  echo "Error: This script must be run with sudo."
  echo "Example: sudo ./setSystemTime.sh"
  exit 1
fi

echo "NOTE: Remember to stop the 'arise_logger.service' first!"
echo "sudo systemctl stop arise_logger.service or sudo ./arise_logger_service_Stop.sh"
echo
echo "--- Manual Time Update ---"
echo
echo "Please enter the new date and time in the following format:"
echo "The time msut be in UTC"
echo "YYYY-MM-DD HH:MM:SS"
echo
echo "For example, to set the time to Oct 31, 2025 at 4:55:30 PM UTC, you would enter:"
echo "2025-10-31 16:55:30"
echo

# Prompt the user to enter the time string
read -p "Enter new date/time: " datetime_string

echo
echo "Attempting to set time to: '$datetime_string'"

# Use the 'date -s' command to set the system time
date -s "$datetime_string"

# Check the exit code of the last command
if [ $? -eq 0 ]; then
  echo
  echo "Time updated successfully."
  echo "The new system time is:"
  date
  echo" You can now restart the logger: sudo systemctl start arise_logger.service or sudo ./arise_logger_service_Restart.sh"
else
  echo
  echo "Error: Failed to set time."
  echo "Please check your format and try again."
fi

