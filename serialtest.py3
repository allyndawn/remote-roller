import os
import random
import serial

ser = serial.Serial()

ser.port = '/dev/serial0'
ser.baudrate = 9600
ser.open()

msg = "Hello World"

print(msg.encode())

ser.write(b'\x7c\x2d')
ser.write(msg.encode())
ser.close()

