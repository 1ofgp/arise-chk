#!/bin/bash

if [ "$EUID" -ne 0 ]; then
  echo "Error: This script must be run with sudo."
  echo "Example: sudo ./arise_logger_Restart.sh"
  exit 1
fi

systemctl daemon-reload
systemctl restart arise_logger.service

