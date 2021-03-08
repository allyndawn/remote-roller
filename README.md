# remote-roller

## Hardware

- [Raspberry Pi Zero W](https://www.raspberrypi.org/products/raspberry-pi-zero-w/)
- [Raspberry Pi Camera V2.1](https://www.raspberrypi.org/products/camera-module-v2/)
- [Raspbbery Pi Zero Camera Case](https://www.raspberrypi.org/products/raspberry-pi-zero-case/)
- [SparkFun 16x2 Serial LCD (16397)](https://www.sparkfun.com/products/16397)
- [Lighted Pushbutton, Green, Momentary (1440)](https://www.adafruit.com/product/1440)
- [Forged Gaming Dice Tray, White](https://forgedgaming.com/products/copy-of-dice-arena-dice-rolling-tray-and-storage?variant=11773653712932)
- Dice
- Chemistry Ring Stand
- Miscellaneous hook up wires

## Cloud Setup

- Login to your [AWS IoT Console](https://us-west-2.console.aws.amazon.com/iot/home?region=us-west-2#/thinghub)
- Under Secure > Policies, create the following policy, name it `remote_roller_player_policy`
- Replace xxx with your Thing Hub's ARN id

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "iot:Connect",
      "Resource": "arn:aws:iot:us-west-2:xxxxxxxxxxxx:client/player*"
    },
    {
      "Effect": "Allow",
      "Action": "iot:Publish",
      "Resource": "arn:aws:iot:us-west-2:xxxxxxxxxxxx:topic/player*/roll"
    },
    {
      "Effect": "Allow",
      "Action": "iot:Subscribe",
      "Resource": "arn:aws:iot:us-west-2:xxxxxxxxxxxx:topicfilter/player*/roll"
    },
    {
      "Effect": "Allow",
      "Action": "iot:Receive",
      "Resource": "arn:aws:iot:us-west-2:xxxxxxxxxxxx:topic/player*/roll"
    }
  ]
}
```

- Login to your AWS console and create three Things: `player_one`, `player_two` and `player_monitor`
- Save their certificates into a `.awskeys` folder on each device as you create them
- Be sure to add the Policy created above to each Things certificates

## Raspberry Pi Configuration

- Use `raspi-config` to disable the linux terminal and enable the serial port
- After doing this, ` ls -la /dev/serial0` should show `/dev/serial0 -> ttyS0`
- Add the following to `~/.bashrc` (or `~/.zshenv`) replacing the xxx with your Thing's details
- One Thing should be named `player_one` and the other `player_two`
- The monitoring system should be named `player_monitor`

```
export AWS_ROOT_CA="/home/pi/.awskeys/AmazonRootCA1.pem"
export AWS_IOT_ENDPOINT="xxxxxxxxxxxxxx-ats.iot.us-west-2.amazonaws.com"
export AWS_IOT_CERTIFICATE="/home/pi/.awskeys/xxxxxxxxxx-certificate.pem.crt"
export AWS_IOT_PRIVATE_KEY="/home/pi/.awskeys/xxxxxxxxxx-private.pem.key"
export AWS_IOT_THING_NAME="player_one"

```
- Run the following commands to set up dependencies
- `python3 -m pip install awsiotsdk`
- `pip install gpiozero`
- `pip install pyserial`
- `sudo apt-get update`
- `sudo apt-get install cmake`
- `sudo apt-get install libssl-dev`
- `pip install opencv-python --no-cache-dir`

## Wiring

- Connect the LCD RAW to 3.3V (e.g. J8:1)
- Connect the LCD GND to GND (e.g. J8:6)
- Connect the LCD RXD to GPIO 15 (TXD) (J8:8)
- Connect the Pushbutton GND to GND (e.g. J8:9)
- Connect the Pushbutton LED anode through a 330 ohm resistor to GPIO 9 (J8:5)
- Connect one side of the Pushbutton switch to GPIO7 (J8:7)
- Connect the Pushbutton LED cathode and other side of the Pushbutton switch to GND (e.g. J8:9)
- Connect the camera to the Raspberry Pi 22-pin connector
