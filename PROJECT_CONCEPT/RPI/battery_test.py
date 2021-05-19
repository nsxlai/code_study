#!/usr/bin/env python

"""
To run this code headlessly, modify the following files:
bootup.sh
    #!/bin/bash
    /usr/bin/python /home/pi/[script_location]/Battery_Test.py

autostart
    @lxterminal -e /home/pi/[script_location]/bootup.sh
"""
# import libraries for time, GPIO, and OpenPiXL
import time
import RPi.GPIO as GPIO
from openpyxl import load_workbook

# Set up GPIO for LED
GPIO.setmode(GPIO.BOARD)
GPIO.setup(7, GPIO.OUT)

# Set start_time to now, in seconds
start_time = time.time()

# Load the spreadsheet and select the worksheet
wb = load_workbook('/home/pi/Documents/Battery_Test.xlsx')
sheet = wb['Sheet1']

while True:
    # Flash LED 5 times every 30 seconds update spreadsheet every 5 minutes
    count_AA = 0
    while count_AA < 10:
        count_BB = 0
        while count_BB < 5:
            GPIO.output(7, True)
            time.sleep(0.5)
            GPIO.output(7, False)
            time.sleep(0.5)
            count_BB += 1
        time.sleep(25)
        count_AA += 1

    # Calculate current uptime in hours
    uptime = (time.time() - start_time) / 3600

    # Add uptime to the spreadsheet
    row = ('Uptime in hours', uptime)
    sheet.append(row)

    # Save the spreadsheet to Documents & to Backup
    wb.save('/home/pi/Documents/Battery_Test.xlsx')
    wb.save('/home/pi/Documents/Backup/Battery_Test.xlsx')
