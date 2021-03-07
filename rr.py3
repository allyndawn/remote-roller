# Remote Roller
# Allen Snook
# February 13, 2021

import asyncio
import json
import os
import random
import serial
import time

from awscrt import io, mqtt
from awsiot import mqtt_connection_builder
from gpiozero import LED, Button

def lcdOut(line1, line2):
    ser.write(b'\x7c\x2d')
    ser.write(line1.encode())
    print(line1)
    if line2:
        ser.write(line2.encode())
        print(line2)

def onButtonPressed():
    global myRoll
    # Ingore button presses after they've already rolled for this round
    if myRoll != -1:
        return

    global mqttConnection
    global pubTopic
    myRoll = random.randint(1,20)
    message = {"value" : myRoll}
    mqttConnection.publish(
        topic=pubTopic,
        payload=json.dumps(message),
        qos=mqtt.QoS.AT_LEAST_ONCE)

def onConnectionInterrupted(connection, error, **kwargs):
    print("Connection interrupted. error: {}".format(error))

def onConnectionResumed(connection, return_code, session_present, **kwargs):
    print("Connection resumed. return_code: {} session_present: {}".format(return_code, session_present))

def onMessageReceived(topic, payload, **kwargs):
    print("Received message from topic '{}': {}".format(topic, payload))
    global theirRoll
    theirRoll = 11 #TODO get from message

# Set up our GPIO devices
led = LED("J8:5")
button = Button("J8:7")

# Set up the LCD
ser = serial.Serial()
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

opponentThingName = ""
if awsIoTThingName == "player_one":
    opponentThingName = "player_two"
else:
    opponentThingName = "player_one"

pubTopic = awsIoTThingName + "/roll"
subTopic = opponentThingName + "/roll"

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

# Subscribe
subTopic = opponentThingName + "/roll"
print("Subscribing to " + subTopic)
subscribeFuture, packet_id = mqttConnection.subscribe(
    topic=subTopic,
    qos=mqtt.QoS.AT_LEAST_ONCE,
    callback=onMessageReceived)

subscribeResult = subscribeFuture.result()
print("Subscribed!")

# The main game loop. Exits on Ctrl-C. Runs forever.
try:
    while True:
        # Reset the game, Turn on LED solid
        myRoll = -1
        theirRoll = -1
        led.on()
        lcdOut("Ready! Press", "button to roll")

        # Wait for either player to roll
        while myRoll == -1 or theirRoll == -1:
            time.sleep(0.1)

        # If we rolled first, blink LED slow
        # If other player rolled first, blink LED fast
        if myRoll != -1:
            led.blink()
            lcdOut("Waiting for", "opponent")

        if theirRoll != -1:
            led.blink()
            lcdOut("Opponent rolled", "Waiting for you")

        # Wait for remaining player to roll
        while myRoll == -1 or theirRoll == -1:
            time.sleep(0.1)

        # Display result
        led.off()
        if myRoll > theirRoll:
            lcdOut("You won!", str(myRoll) + " > " + str(theirRoll))

        if myRoll < theirRoll:
            lcdOut("They won!", str(myRoll) + " < " + str(theirRoll))

        if myRoll > theirRoll:
            lcdOut("It's a tie!", str(myRoll) + " = " + str(theirRoll))

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
