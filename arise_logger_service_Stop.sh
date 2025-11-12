#!/bin/bash

if [ "$EUID" -ne 0 ]; then
  echo "Error: This script must be run with sudo."
  echo "Example: sudo ./arise_logger_Stop.sh"
  exit 1
fi

systemctl stop arise_logger.service

