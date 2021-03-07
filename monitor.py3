# Remote Roller Monitor
# Allen Snook
# March 3, 2021

import json
import os
import time

from awscrt import io, mqtt
from awsiot import mqtt_connection_builder

def onConnectionInterrupted(connection, error, **kwargs):
    print("Connection interrupted. error: {}".format(error))

def onConnectionResumed(connection, return_code, session_present, **kwargs):
    print("Connection resumed. return_code: {} session_present: {}".format(return_code, session_present))

def onMessageReceived(topic, payload, **kwargs):
    print("Received message from topic '{}': {}".format(topic, payload))

# Set up the client.
awsRootCAPath = os.getenv("AWS_ROOT_CA")
awsIoTEndpoint = os.getenv("AWS_IOT_ENDPOINT")
awsIoTCertificate = os.getenv("AWS_IOT_CERTIFICATE")
awsIoTPrivateKey = os.getenv("AWS_IOT_PRIVATE_KEY")
awsIoTThingName = os.getenv("AWS_IOT_THING_NAME") # Should really be Client ID which doesn't need to match the Thing Name

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
print("Connected!")

# Subscribe
subTopic1 = "player_one/roll"
print("Subscribing to " + subTopic1)
subscribeFuture1, packetId1 = mqttConnection.subscribe(
    topic=subTopic1,
    qos=mqtt.QoS.AT_LEAST_ONCE,
    callback=onMessageReceived)

subscribeResult1 = subscribeFuture1.result()
print("Subscribed to player_one/roll!")

subTopic2 = "player_two/roll"
print("Subscribing to " + subTopic2)
subscribeFuture2, packetId2 = mqttConnection.subscribe(
    topic=subTopic2,
    qos=mqtt.QoS.AT_LEAST_ONCE,
    callback=onMessageReceived)

subscribeResult2 = subscribeFuture2.result()
print("Subscribed to player_two/roll!")

# The main loop. Exits on Ctrl-C. Runs forever.
try:
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    pass

# Shut down the MQTT client
disconnectFuture = mqttConnection.disconnect()
disconnectFuture.result()
print("Disconnected!")
