# Remote Roller
# Allen Snook
# February 13, 2021

import asyncio
import cv2
import json
import numpy as np
import os
import random
import serial
import subprocess
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
    print("Button pressed")
    # Ingore button presses after they've already rolled for this round
    if myRoll != -1:
        return

    # Capture the image
    imagePath = "./image.jpg"
    lcdOut("Capturing image ", "Please wait...")
    subprocess.run(["/usr/bin/raspistill", "-o", imagePath])

    # Analyze the image
    lcdOut("Analyzing image ", "Please wait...")
    myRoll = countPipsInImage(imagePath)
    print("I count ", myRoll)

    # Publish the count
    lcdOut("Sending to the  ", "server...")
    global mqttConnection
    global pubTopic
    # myRoll = random.randint(1,20)
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
    message = json.loads(payload)
    theirRoll = message["value"]

def firstRollCast():
    global myRoll
    global theirRoll
    if myRoll > 0:
        return True
    if theirRoll > 0:
        return True
    return False

def bothRollsCast():
    global myRoll
    global theirRoll
    if myRoll < 0:
        return False
    if theirRoll < 0:
        return False
    return True

def getBlobs(frame):
    frameBlurred = cv2.medianBlur(frame, 7)
    frameGray = cv2.cvtColor(frameBlurred, cv2.COLOR_BGR2GRAY)
    blobs = detector.detect(frameGray)
    print("found # of blobs:", len(blobs))
    return blobs

def overlay_info(frame, blobs):
    # Overlay blobs
    for b in blobs:
        pos = b.pt
        r = b.size / 2

        cv2.circle(frame, (int(pos[0]), int(pos[1])),
                   int(r), (255, 0, 0), 2)

def countPipsInImage(imagePath):
    # Open the image
    image = cv2.imread(imagePath)
    imageHeight, imageWidth, imageColorPlanes = image.shape

    cropX1 = int(0.35 * imageWidth)
    cropX2 = int(0.67 * imageWidth)
    cropY1 = int(0.3 * imageHeight)
    cropY2 = int(0.7 * imageHeight)

    # Crop the image
    croppedImage = image[cropY1:cropY2, cropX1:cropX2]

    # Count the pips
    blobs = getBlobs(croppedImage)

    # Out the overlay
    overlay_info(croppedImage, blobs)

    # Save the result for later reference
    cv2.imwrite('./processed.png', croppedImage)

    # Debugging: Show the result
    # cv2.imshow('img', croppedImage)
    # cv2.waitKey()
    # cv2.destroyAllWindows()

    return len(blobs)

# Set up the blob detector
params = cv2.SimpleBlobDetector_Params()
params.filterByInertia
params.minInertiaRatio = 0.6
detector = cv2.SimpleBlobDetector_create(params)

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
        lcdOut("Roll dice then  ", "press button...")

        # Wait for either player to roll
        while not firstRollCast():
            time.sleep(0.1)

        # If we rolled first, blink LED slow
        # If other player rolled first, blink LED fast
        if myRoll != -1:
            led.blink()
            lcdOut("Waiting for     ", "opponent")

        if theirRoll != -1:
            led.blink()
            lcdOut("Opponent rolled.", "Waiting for you")

        # Wait for remaining player to roll
        while not bothRollsCast():
            time.sleep(0.1)

        # Display result
        led.off()
        if myRoll > theirRoll:
            lcdOut("You won!        ", str(myRoll) + " > " + str(theirRoll))

        if myRoll < theirRoll:
            lcdOut("They won!       ", str(myRoll) + " < " + str(theirRoll))

        if myRoll == theirRoll:
            lcdOut("It's a tie!     ", str(myRoll) + " = " + str(theirRoll))

        time.sleep(10)

except KeyboardInterrupt:
    pass

# Shut down the MQTT client
disconnectFuture = mqttConnection.disconnect()
disconnectFuture.result()
lcdOut("Disconnected!","")
time.sleep(1)

# Close serial I/O
ser.close()
