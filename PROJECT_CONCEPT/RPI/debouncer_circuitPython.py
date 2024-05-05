"""
From Adafruit youtube video:
https://www.youtube.com/watch?v=ktlRv83UvjY
"""
import board
from digitalio import DigitalInOut, Direction, Pull
from adafruit_debouncer import Debouncer
import neopixel

count_blue = 0
count_yellow = 0

RED = 0xAA0000
BLUE = 0x0000AA
YELLOW = 0x888800
BLACK = 0x000000

led = DigitalInOut(board.D13)
led.direction = Direction.OUTPUT

pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.2)
pixel[0] = BLACK

strip_blue = neopixel.NeoPixel(board.D8, 8, brightness=0.2, auto_write=False)
strip_yellow = neopixel.NeoPixel(board.D9, 8, brightness=0.2, auto_write=False)

strip_blue.fill(BLACK)
strip_blue[0] = YELLOW
strip_blue.show()

strip_yellow.fill(BLACK)
strip_yellow[0] = YELLOW
strip_yellow.show()

button_blue = DigitalInOut(board.D5)
button_blue.pull = Pull.UP

button_yellow_input = DigitalInOut(board.D6)
button_yellow_input.pull = Pull.UP
button_yellow = Debouncer(button_yellow_input)

while True:
    # Blue button
    led.value = not button_blue.value
    if not button_blue.value:
        count_blue += 1
        print(f'Blue count: {count_blue % 8}\n')
        strip_blue.fill(BLACK)
        strip_blue[count % 8] = BLUE
        strip_blue.show()

    # Yellow button
    button_yellow.update()
    if button_yellow.fell:
        count_yellow += 1
        print(f'yellow count: {count_yellow % 8}\n')
        pixel[0] = RED
        strip_yellow.fill(BLACK)
        strip_yellow[count_yellow % 8] = YELLOW
        strip_yellow.show()

    if button_yellow.rose:
        print('Yellow Button released!\n')
        pixel[0] = BLACK
