# remote-roller

## Hardware

- Raspberry Pi Zero W
- Raspberry Pi Camera V2.1
- [SparkFun 16x2 Serial LCD (16397)](https://www.sparkfun.com/products/16397)
- [Lighted Pushbutton, Green, Momentary (1440)](https://www.adafruit.com/product/1440)

## Software

- Install the Amazon IoT SDK


## Configuration

- Add the following to ~/.bashrc replacing the xxx with your Thing's details
- One thing should be named player_one and the other player_two
- The monitoring system should be named player_monitor

```
export AWS_ROOT_CA="/home/pi/.awskeys/AmazonRootCA1.pem"
export AWS_IOT_ENDPOINT="xxxxxxxxxxxxxx-ats.iot.us-west-2.amazonaws.com"
export AWS_IOT_CERTIFICATE="/home/pi/.awskeys/xxxxxxxxxx-certificate.pem.crt"
export AWS_IOT_PRIVATE_KEY="/home/pi/.awskeys/xxxxxxxxxx-private.pem.key"
export AWS_IOT_THING_NAME="player_one"

```
