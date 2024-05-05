# SPDX-FileCopyrightText: Copyright (c) 2020 Bryan Siepert for Adafruit Industries
#
# SPDX-License-Identifier: MIT
import time
import board
from adafruit_lsm6ds.ism330dhcx import ISM330DHCX
from math import atan2, pi, sqrt

alpha = 0.98
beta = 1 - alpha
roll = 0
pitch = 0
yaw = 0

i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
sensor = ISM330DHCX(i2c)

while True:
    # print("Acceleration: X:%.2f, Y: %.2f, Z: %.2f m/s^2" % (sensor.acceleration))
    # print("Gyro X:%.2f, Y: %.2f, Z: %.2f radians/s" % (sensor.gyro))
    # print("")
    ax, ay, az = sensor.acceleration
    gx, gy, gz = sensor.gyro

    acc_roll = atan2(ay, az) * (180 / pi)
    acc_pitch = atan2(-ax, sqrt(ay**2 + az**2)) * (180 / pi)

    roll = alpha * (roll + gx) + beta * acc_roll
    pitch = alpha * (pitch + gy) + beta * acc_pitch
    yaw += gz

    # Ensure yaw stays within range (-180 to 180 degrees)
    yaw = yaw % 360
    if yaw > 180:
        yaw -= 360
    elif yaw < -180:
        yaw += 360

    print((roll, pitch, yaw,))
    # print((ax, ay, az,))
    # print((gx, gy, gz, ))
    time.sleep(0.1)
    # test end
