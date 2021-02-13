# blink.py3
# Blinks an LED attached to J8:5
#
# Allen Snook
# February 13, 2021

from gpiozero import LED
from signal import pause

led = LED("J8:5")
led.blink()

pause()
