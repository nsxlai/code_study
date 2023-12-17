import serial.tools.list_ports as list_ports
import serial
from time import sleep
import logging

import pandas as pd
import numpy as np

from icm42605 import icm42605

 
if __name__ == "__main__":
    ports = list(list_ports.comports())
    for p in ports: print(p)
 
    ser = serial.Serial(port="COM10", baudrate=500000, timeout=0.5)
    ser.close(); sleep(0.1); ser.open(); sleep(2) # allow enough time for connection to stabilize
 
    sensor = icm42605(ser, reset_sensor=True)
 
    sensor.gyro_setup(odr=200,fsr=250)
    sensor.accel_setup(odr=200,fsr=2)

    print (ser.read_all())

    df_selftest = pd.DataFrame(data=None, index=["Gx","Gy","Gz","Ax","Ay","Az"], columns=["ST_meas_on","ST_meas_off"])

    # GYRO SELF TEST
    # Step 1: configure part ODR, FSR, lowpass filtering per AN-000150 recommendation
    # Appnote has different recommendations for ICM-42686 vs all other ICM-426xx
    GYRO_FS_SEL = 0b011 # needed later.. 0b011: ±250dps
    sensor.i2c_write(0, 0x4F, [0x66]) # GYRO_FS_SEL: ±250dps; GYRO_ODR: 1kHz
    sensor.i2c_write(0, 0x51, [0x08]) # GYRO_UI_FILT_ORD: 3 rd Order
    sensor.i2c_write(0, 0x52, [0x04]) # GYRO_UI_FILT_BW: ODR/10
    sensor.i2c_write(0, 0x4E, [0x0C]) # GYRO_MODE: Low Noise Mode
    sensor.fifo_config()

    # Step 2: power on, wait t=100ms, grab 200 samples
    sensor.power()
    sleep(0.5) # appnote says 0.1ms is ok
 
    gyro_st_off = sensor.fifo_read_stream(N_samples=200)
    df_selftest["ST_meas_off"].loc[["Gx","Gy","Gz"]] = gyro_st_off[["Gx","Gy","Gz"]].mean()
   
    # Step 3: enable self test mode and capture 200 more samples
    sensor.i2c_write(0, 0x70, [0x07]) # EN_GX_ST = EN_GY_ST = EN_GZ_ST = 1
    sleep(0.5) # appnote says 0.2s is ok
 
    gyro_st_on = sensor.fifo_read_stream(N_samples=200)
    df_selftest["ST_meas_on"].loc[["Gx","Gy","Gz"]] = gyro_st_on[["Gx","Gy","Gz"]].mean()
 
    sensor.power(power=False)
    sensor.reset() # this isn't explicitly specified in the appnote, but doing it anyway to be safe
 
    # ACCEL SELF TEST - similar as above
    # STEP 4 - setup per AN-000150
    ACCEL_FS_SEL = 0b011 # needed later 0b011: ±2g
    sensor.i2c_write(0, 0x50, [0x66]) # ACCEL_FS_SEL: ±2g; ACCEL_ODR: 1kHz
    sensor.i2c_write(0, 0x52, [0x40]) # ACCEL_UI_FILT_BW: ODR/10
    sensor.i2c_write(0, 0x53, [0x10]) # ACCEL_UI_FILT_ORD: 3 rd Order
    sensor.i2c_write(0, 0x4E, [0x03]) # ACCEL_MODE: Low Noise Mode
    sensor.fifo_config()
 
    # Step 5: power on, wait, grab 200 samples
    sensor.power()
    sleep(0.5) # appnote says 0.1ms is ok
 
    accel_st_off = sensor.fifo_read_stream(N_samples=200)
    df_selftest["ST_meas_off"].loc[["Ax","Ay","Az"]] = accel_st_off[["Ax","Ay","Az"]].mean()
 
    # Step 6: enable self test mode and capture 200 more samples
    sensor.i2c_write(0, 0x70, [0x78]) # SELF_TEST_ACCEL_REGULATOR = 1; EN_AX_ST = EN_AY_ST = EN_AZ_ST = 1
    sleep(0.5) # appnote says 0.2s is ok
 
    accel_st_on = sensor.fifo_read_stream(N_samples=200)
    df_selftest["ST_meas_on"].loc[["Ax","Ay","Az"]] = accel_st_on[["Ax","Ay","Az"]].mean()
 

    df_selftest["ST_diff"] = df_selftest["ST_meas_on"] - df_selftest["ST_meas_off"]

    # STEP 7 - read factory self-test data
    gyro_st_code = [sensor.i2c_read(1,0x5F, 1)[0], sensor.i2c_read(1, 0x60, 1)[0], sensor.i2c_read(1, 0x61, 1)[0]]
    accel_st_code = [sensor.i2c_read(2, 0x3B, 1)[0], sensor.i2c_read(2, 0x3C, 1)[0], sensor.i2c_read(2, 0x3D, 1)[0] ]
 
    df_selftest["ST_DATA"] = gyro_st_code + accel_st_code
 
    def st_otp_calc(ST_code, FS_sel):
        ST_OTP = (2620/(2**(3-FS_sel))) * (1.01**(ST_code-1))
        return ST_OTP
   
    gyro_st_otp = [st_otp_calc(ST_code, GYRO_FS_SEL) for ST_code in gyro_st_code]
    accel_st_otp = [st_otp_calc(ST_code, ACCEL_FS_SEL) for ST_code in accel_st_code]
 
    df_selftest["ST_OTP"] = gyro_st_otp + accel_st_otp
 
    # STEP 8 - compare read data vs OTP data
    df_selftest["ST_ratio"] = df_selftest["ST_diff"]/df_selftest["ST_OTP"]
    df_selftest["ST_pass"] = (df_selftest["ST_ratio"] < 1.5) & (df_selftest["ST_ratio"] > 0.5)
   
    pd.set_option("display.precision", 1)
    print( df_selftest.astype(np.float64) )
   
    df_selftest.to_csv("measure self-test.csv")
 
    """
    Example of successful test:
              ST_meas_on  ST_meas_off   ST_diff    ST_DATA  ST_OTP         ST_ratio      ST_pass
        Gx    14512.89    7.805         14505.085  173      14506.99903    0.999868062   TRUE
        Gy    15162.325   -67.595       15229.92   178      15247.00177    0.998879663   TRUE
        Gz    14733.65    34.48         14699.17   174      14652.06902    1.00321463    TRUE
        Ax    4813.22     93.77         4719.45    61       4759.74535     0.991534137   TRUE
        Ay    5925.98     92.48         5833.5     81       5807.793869    1.004426144   TRUE
        Az    25615.84    16512.34      9103.5     127      9178.979247    0.991776945   TRUE
    """
 
    # Done!  Shutdown.
    sensor.power(power=False)
    sensor.reset()
    sensor.close()
