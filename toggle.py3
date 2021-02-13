# toggle.py3
# Toggles an LED on J8:5 on and off as a button
# on J8:7 is pressed
#
# Allen Snook
# February 13, 2021

from gpiozero import LED, Button
from signal import pause

led = LED("J8:5")
button = Button("J8:7")

button.when_pressed = led.toggle

pause()
