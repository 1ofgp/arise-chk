# Debian Image
By default the OS imaged is flashed on eMMC, no SD-card needed.
# Structure
All the scripts are in `/home/debian/arise/`
- `taxiON.sh` -- turn TAXI On. Must be run as sudo. By default TAXI is off. ToDo: turn ON at BBB start.
- `taxiON.sh` -- turn TAXI Off. Must be run as sudo.
- `ariseCHK.py` -- main logger script, runs as service (`/etc/systemd/system/arise_logger.service`), no manual launch required by default. The script saves timestamped (RTC by default) INA260 sensor data (voltage and current) every second.
- `arise_logger_service_Status.sh` -- check the status of the logger service. Must be run as sudo.  
- `arise_logger_service_Stop.sh` -- stop the logger service (e.g. before changing system or RTC time). Must be run as sudo.  
- `arise_logger_service_Restart.sh` -- restart the logger service. Must be run as sudo.  
- `logdata\` -- directory with sensors data files (bin), a new file is created every hour. Sampling rate is 1 second. The size of 1 hour file is ~56kB.
- `readData.py` -- script to read sensors data.
- `ariseCHK_log.log` -- logger service log file (text).
- `setRTC_time.py, setSystemTime.sh, getTime.sh` -- see `Timing` section. 

# Timing
There are 2 different clocks running:
- RTC -- default, should stay correct while the battery is alive (should be years);
- System -- resets every time BBB restarts, can be set manually using corresponding scripts.

All the times must be in UTC!

ToDo: add NTP synchronization.

Timing scripts:
- `getTime.sh` -- returns RTC and System time;
- `setRTC_time` -- set RTC time, not needed unless the RTC unit is disconnected or the battery is dead;
- `setSystemTime.sh` -- set System time. It is a good idea to set correct system time once the device is constantly running. 