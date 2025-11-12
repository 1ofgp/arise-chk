#!/bin/bash

if [ "$EUID" -ne 0 ]; then
  echo "Error: This script must be run with sudo."
  echo "Example: sudo ./arise_logger_Status.sh"
  exit 1
fi

systemctl status arise_logger.service
