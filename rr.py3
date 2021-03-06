# Remote Roller
# Allen Snook
# February 13, 2021

import asyncio
import os
import random
import serial
import time

from awscrt import io
from awsiot import mqtt_connection_builder
from gpiozero import LED, Button

my_roll = -1
their_roll = -1
ser = serial.Serial()

def lcdOut(line1, line2):
    ser.write(b'\x7c\x2d')
    ser.write(line1.encode())
    print(line1)
    if line2:
        ser.write(line2.encode())
        print(line2)

def onButtonPressed():
    global my_roll
    my_roll = random.randint(1,20)

def onMessageReceive():
    global their_roll
    their_roll = 11 #TODO get from message

def onConnectionInterrupted(connection, error, **kwargs):
    print("Connection interrupted. error: {}".format(error))

def onConnectionResumed(connection, return_code, session_present, **kwargs):
    print("Connection resumed. return_code: {} session_present: {}".format(return_code, session_present))

# Set up our GPIO devices
led = LED("J8:5")
button = Button("J8:7")

# Set up the LCD
ser.port = '/dev/serial0'
ser.baudrate = 9600
ser.open()

lcdOut("Starting up","")
time.sleep(1)

# Set up the client.
awsRootCAPath = os.getenv("AWS_ROOT_CA")
awsIoTEndpoint = os.getenv("AWS_IOT_ENDPOINT")
awsIoTCertificate = os.getenv("AWS_IOT_CERTIFICATE")
awsIoTPrivateKey = os.getenv("AWS_IOT_PRIVATE_KEY")
awsIoTThingName = os.getenv("AWS_IOT_THING_NAME")

eventLoopGroup = io.EventLoopGroup(1)
hostResolver = io.DefaultHostResolver(eventLoopGroup)
clientBootstrap = io.ClientBootstrap(eventLoopGroup, hostResolver)

mqttConnection = mqtt_connection_builder.mtls_from_path(
    endpoint=awsIoTEndpoint,
    cert_filepath=awsIoTCertificate,
    pri_key_filepath=awsIoTPrivateKey,
    client_bootstrap=clientBootstrap,
    ca_filepath=awsRootCAPath,
    on_connection_interrupted=onConnectionInterrupted,
    on_connection_resumed=onConnectionResumed,
    client_id=awsIoTThingName,
    clean_session=False,
    keep_alive_secs=60)

# Connect the client.
connectFuture = mqttConnection.connect()
connectFuture.result()
lcdOut("Connected!","")
time.sleep(1)

# Listen for button events
button.when_pressed = onButtonPressed

# Listen for messages from the IoT Hub
# TODO

# The main game loop. Exits on Ctrl-C. Runs forever.
try:
    while True:
        # Turn on LED solid
        led.on()
        lcdOut("Ready! Press", "button to roll")

        # Wait for either player to roll
        while my_roll == -1 or their_roll == -1:
            time.sleep(0.1)

        # If we rolled first, blink LED slow
        # If other player rolled first, blink LED fast
        if my_roll != -1:
            led.blink()
            lcdOut("Waiting for", "opponent")

        if their_roll != -1:
            led.blink()
            lcdOut("Opponent rolled", "Waiting for you")

        # Wait for remaining player to roll
        while my_roll == -1 or their_roll == -1:
            time.sleep(0.1)

        # Display result
        led.off()
        if my_roll > their_roll:
            lcdOut("You won!", str(my_roll) + " > " + str(their_roll))

        if my_roll < their_roll:
            lcdOut("They won!", str(my_roll) + " < " + str(their_roll))

        if my_roll > their_roll:
            lcdOut("It's a tie!", str(my_roll) + " = " + str(their_roll))

        time.sleep(3)

except KeyboardInterrupt:
    pass

# Shut down the MQTT client
disconnectFuture = mqttConnection.disconnect()
disconnectFuture.result()
lcdOut("Disconnected!","")
time.sleep(1)

# Close serial I/O
ser.close()
