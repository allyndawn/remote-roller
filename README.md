# remote-roller

An AWS IoT powered MQTT based two terminal dice rolling game using OpenCV and a pair of Raspberry Pi Zero W.

Work in progress.

## Hardware

Two of each of the following. One for each "player"

- [Raspberry Pi Zero W](https://www.raspberrypi.org/products/raspberry-pi-zero-w/)
- [Raspberry Pi Camera V2.1](https://www.raspberrypi.org/products/camera-module-v2/)
- [Raspbbery Pi Zero Camera Case](https://www.raspberrypi.org/products/raspberry-pi-zero-case/)
- [Raspberry Pi Camera Focus Adjustment Tool](https://www.adafruit.com/product/3518)
- [SparkFun 16x2 Serial LCD (16397)](https://www.sparkfun.com/products/16397)
- [Lighted Pushbutton, Green, Momentary (1440)](https://www.adafruit.com/product/1440)
- [Forged Gaming Dice Tray, White](https://forgedgaming.com/products/copy-of-dice-arena-dice-rolling-tray-and-storage?variant=11773653712932)
- Dice
- Chemistry Ring Stand
- Miscellaneous hook up wires

## Cloud Setup

- Login to your [AWS IoT Console](https://us-west-2.console.aws.amazon.com/iot/home?region=us-west-2#/thinghub)
- Under Secure > Policies, create the following policy, name it `remote_roller_player_policy`
- Note: The Resource ARN will be auto-filled for you as you add each Action. You will need to edit the end of the Resource to get the correct client, topic and topicfilters shown below. However, do not change the rest of the ARN.

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

- Next, under Manage > Things, create three Things: `player_one`, `player_two` and `player_monitor`
- Save their certificates into a `.awskeys` folder on each device as you create them
- Be sure to add the Policy created above to each Things certificates

## Wiring

- Connect the LCD RAW to 3.3V (e.g. J8:1)
- Connect the LCD GND to GND (e.g. J8:6)
- Connect the LCD RXD to GPIO 15 (TXD) (J8:8)
- Connect the Pushbutton GND to GND (e.g. J8:9)
- Connect the Pushbutton LED anode through a 330 ohm resistor to GPIO 9 (J8:5)
- Connect one side of the Pushbutton switch to GPIO7 (J8:7)
- Connect the Pushbutton LED cathode and other side of the Pushbutton switch to GND (e.g. J8:9)
- Connect the camera to the Raspberry Pi 22-pin connector

## Raspberry Pi Configuration

- Connect an HDMI cable and keyboard
- Wait for the GUI to boot.
- Complete setup.
- Open Preferences (under the Raspberry) and select Boot to CLI (not GUI)
- Use the GUI or `raspi-config` to disable the linux terminal and enable the serial port
- Use the GUI or `raspi-config` to enable the camera port
- After doing this, ` ls -la /dev/serial0` should show `/dev/serial0 -> ttyS0`
- Reboot (to CLI)
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
- Run the following command to check WiFi signal strength. Update wpa_supplicant.conf to use strong networks.
- `python3 iwlistparse.py`

- Run the following commands to set up dependencies
```
python3 -m pip install awsiotsdk
pip install gpiozero
pip install pyserial
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install libssl-dev
sudo apt-get install build-essential cmake pkg-config
sudo apt-get install libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev
sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
sudo apt-get install libxvidcore-dev libx264-dev
sudo apt-get install libgtk2.0-dev libgtk-3-dev
sudo apt-get install libatlas-base-dev gfortran
sudo apt-get install libqtgui4
sudo modprobe bcm2835-v4l2
sudo apt-get install libqt4-test
sudo apt-get install python3-dev
sudo apt-get install python3-pip
pip3 install opencv-python
sudo apt-get install python-opencv
pip install numpy
pip install sklearn
```

## Raspberry Pi Pre-check
- Use `raspistill -o ./image.jpg` to capture an image from the camera
- Use the focus tool to adjust the image focus (the factory default is out at infinity)
- Run `python3 serialtest.py3` and ensure "Hello World" is displayed on the LCD
- Run `python3 toggle.py3` and ensure pressing the pushbutton toggles the pushbutton LED
- (Press Ctrl-C to exit)
- Run `python3 dicereader.py3` and ensure it is able to count the pips on `image.jpg` captured above
- You can examine the `processed.png` output file to see what it saw

## Launch the Monitor
- Run `python3 monitor.py3` and ensure the device is able to connect to AWS

## Launch the "Remote Roller" Script on each Raspberry Pi
- Run `python3 rr.py3`, ensure each device is able to connect to AWS and enjoy the game!

## Sample Images
- Sample image before processing:

![Before](/sampledata/image.jpg)

- Sample image after processing:

![After](/sampledata/processed.png)

## Props

- Quentin Golsteyn https://golsteyn.com/projects/dice/ for a great example of using OpenCV to read dice
- Hugo Chargois for his WiFi strength parsing script (iwlistparse.py)
- Unlocked Lab for [OpenCV Raspberry Pi setup instructions](https://www.youtube.com/watch?v=cmPz6bfIOEU) that work!
