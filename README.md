# remote-roller

## Hardware

- Raspberry Pi Zero W
- Raspberry Pi Camera V2.1
- [SparkFun 16x2 Serial LCD (16397)](https://www.sparkfun.com/products/16397)
- [Lighted Pushbutton, Green, Momentary (1440)](https://www.adafruit.com/product/1440)

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
- Be sure to add the Policy created above to the the Things certificates

## Raspberry Pi Configuration

- Use `raspi-config` to disable the linux terminal and enable the serial port
- Add the following to `~/.bashrc` (or `~/.zshenv`) replacing the xxx with your Thing's details
- One thing should be named player_one and the other player_two
- The monitoring system should be named player_monitor

```
export AWS_ROOT_CA="/home/pi/.awskeys/AmazonRootCA1.pem"
export AWS_IOT_ENDPOINT="xxxxxxxxxxxxxx-ats.iot.us-west-2.amazonaws.com"
export AWS_IOT_CERTIFICATE="/home/pi/.awskeys/xxxxxxxxxx-certificate.pem.crt"
export AWS_IOT_PRIVATE_KEY="/home/pi/.awskeys/xxxxxxxxxx-private.pem.key"
export AWS_IOT_THING_NAME="player_one"

```
- Run the following commands to set up dependencies
- `python3 -m pip install awsiotsdk`
- 
