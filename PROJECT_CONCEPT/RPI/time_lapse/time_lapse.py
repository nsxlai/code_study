"""
source: https://www.youtube.com/watch?v=Fer4SssH4FE&t=853s

The time lapse code will have the following specification:
1. Capture interval: every 2 seconds
2. Total frame capture: 750 frames
3. Frame rate: 25 fps

The capture will be completed in 25 minutes (2 seconds X 750 frames = 1500 seconds)
Total render will be around 30 seconds (750 frames / 25 fps = 30 seconds)

Also need to make this file executable by doing the "sudo chmod +x time_lapse.py"
"""
from picamera import PiCamera
import time
import os

# Set up variables
interval = 2
frame = 0
max_frame = 750

# Wait 20 seconds in case the user is trying to stop this!
time.sleep(20)

# Set up & start camera
camera = PiCamera()
camera.resolution = (2592, 1944)
camera.start_preview()
time.sleep(2)

while frame < max_frame:
    camera.capture(f'home/pi/Videos/Frames/clouds_{frame}.jpg')
    frame += 1
    time.sleep(interval)

# Shut down gracefully
os.system('sudo shutdown now')
