"""
From YouTube channel 'Gary Explains': https://www.youtube.com/watch?v=_fdwE4EznYo

The model of the servo is Micro Servo SG90
"""
import math
from gpiozero import Servo
from time import sleep

from gpiozero.pins.pigpio import PiGPIOFactory


def simple_servo_demo(servo):
    print('Start in the middle position')
    servo.mid()
    sleep(5)
    print('Go to the minimum position')
    servo.min()
    sleep(5)
    print('Go to the maximum position')
    servo.max()
    sleep(5)
    print('Back to the middle')
    servo.mid()
    sleep(5)
    servo.value = None


def radar_servo_sweep(servo):
    """ This will make the servo sweep from min to max continuously
     """
    while True:
        for i in range(0, 360):
            servo.value = math.sin(math.radians(i))
            sleep(0.01)


if __name__ == '__main__':
    """
    Servo PWM pin connects to GPIO 12 (PWM 0), which is pin 32 (see IMG_0207 for detail)
    If simply use servo = Servo(12), PWM value is SW generated and it will not stay the same. 
    This makes the servo jittery. PiGPIOFactory introduces HW based PWM timing to eliminate 
    the servo jitter. Check the pigpio library for detail. One pre-requisite is to run the 
    pigpio daemon before running the script: sudo gpiod
    
    Actually, if using servo = Servo(12), the script will throw warning on the screen:
       PWMSoftwareFallback: To reduce servo jitter, use the pigpio pin factory. See 
       https://gpiozero.readthedocs.io/en/stable/api_output.html#servo
       
    SG-90 servo spec:
       Position 90 (servo.mid()): 2 ms pulse
       Position  0 (servo.mid()): 1.5 ms pulse
       Position -90 (servo.min()): 1 ms pulse
       
    Sometimes the servo might not be following the spec exactly. Minor tweak to the timing
    can help fine tune the servo position with min_pulse_width and max_pulse_width keyword argument.
    """
    # servo = Servo(12)
    factory = PiGPIOFactory()
    servo = Servo(12, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000, pin_factory=factory)

    simple_servo_demo(servo)
    radar_servo_sweep(servo)
