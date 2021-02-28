# Remote Roller
# Allen Snook
# February 13, 2021

import asyncio
import os
import random
import serial

from azure.iot.device.aio import IoTHubDeviceClient
from gpiozero import LED, Button

my_roll = -1
their_roll = -1
ser = serial.Serial()

def lcdOut(line1, line2):
    # TODO send clearing characters
    ser.write(line1)
    print(line1)
    if line2:
        ser.write(line2)
        print(line2)

def onButtonPressed():
    global my_roll
    my_roll = random.randint(1,20)

def onMessageReceive():
    global their_roll
    their_roll = 11 #TODO get from message

async def main():
    global ser
    global my_roll
    global their_roll

    # Set up our GPIO devices
    led = LED("J8:5")
    button = Button("J8:7")

    # Set up the LCD
    ser.port = '/dev/serial0'
    ser.baudrate = 9600
    ser.open()

    lcdOut("Starting up","")
    await asyncio.sleep(1)

    conn_str = os.getenv("IOTHUB_DEVICE_CONNECTION_STRING")
    device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)

    # Connect the client.
    await device_client.connect()
    lcdOut("Connected!","")
    await asyncio.sleep(1)

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
                await asyncio.sleep(0.1)

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
                await asyncio.sleep(0.1)

            # Display result
            led.off()
            if my_roll > their_roll:
                lcdOut("You won!", str(my_roll) + " > " + str(their_roll))

            if my_roll < their_roll:
                lcdOut("They won!", str(my_roll) + " < " + str(their_roll))

            if my_roll > their_roll:
                lcdOut("It's a tie!", str(my_roll) + " = " + str(their_roll))

            await asyncio.sleep(3)

    except KeyboardInterrupt:
        pass

    # Shut down the MQTT client
    await device_client.shutdown()
    lcdOut("Disonnected!","")
    await asyncio.sleep(1)

    # Close serial I/O
    ser.close()

if __name__ == "__main__":
    asyncio.run(main())

