"""
source: https://www.youtube.com/watch?v=Zy64kZEM_bg&list=PLWNDWPAClRVoo0Z-QtCkXuM15jdb2Q54N
at time stamp 31:50
"""

import machine
import utime


led_red = machine.Pin(10, machine.Pin.OUT)
led_green = machine.Pin(11, machine.Pin.OUT)

led_red.value(0)
led_green.value(0)

button_red = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_DOWN)


def int_handler(pin):
    button_red.irq(handler=None)
    print('Interrupt Detected!!')
    led_red.value(1)
    led_green.value(0)
    utime.sleep(4)
    led_red.value(0)
    button_red.irq(handler=int_handler)


button_red.irq(trigger=machine.Pin.IRQ_RISING, handler=int_handler)


while True:
    led_green.toggle()
    utime.sleep(2)
