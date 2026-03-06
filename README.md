ARISE CHK v 1.0 March 2026

# Debian Image
By default the OS imaged is flashed on eMMC, no SD-card needed.
To copy the image form SD to eMMC:
Insert SD and hold S2 (next to SD) for ~10 seconds. After a few minutes the image will be copied to eMMC and BBB will turn off, the SD-card then can be removed.
To get the image as me.
# Structure
All the scripts are in `/home/debian/arise/`
- `taxiON.sh` -- turn TAXI On. Must be run as sudo. By default TAXI is On. 
- `taxiOFF.sh` -- turn TAXI Off. Must be run as sudo.
- `ariseCHK.py` -- main logger script, runs as service (`/etc/systemd/system/arise_logger.service`), no manual launch required by default. The script saves timestamped data from various sensors.
- `arise_logger.service` -- ARISE CHK logger service config file. Do not change it unless something does not work.
- `arise_logger_service_Status.sh` -- check the status of the logger service. Must be run as sudo.  
- `arise_logger_service_Stop.sh` -- stop the logger service (e.g. before changing system or RTC time). Must be run as sudo.  
- `arise_logger_service_Restart.sh` -- restart the logger service. Must be run as sudo.  
- `logdata\` -- directory with sensors data files (bin), a new file is created every hour. Sampling rate (can be tuned) is ~1.3 seconds without dust (the slowest sensor) and ~2 seconds with dust (minimum averaging).  
- `readData.py` -- script to read sensors data.
- `ariseCHK_v1p0_log.log` -- logger service log file (text).
- `setSystemTime.sh` -- set system time, normally the time is set using NTP server, no RTC required compared to old version. All the times must be in UTC!

# Sensors:
- Current
- Voltage
- BME680: temperature, humidity, pressure, VOCs
- Temperature x4: 1 inside, 3 outside;
- Dust