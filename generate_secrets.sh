#!/bin/bash
echo -e "# Name of your wifi network
WIFI_SSID=''
# Password for your network
WIFI_PASSWORD=''
# ID of the cam device that will be used in the system
DEVICE_ID=b''
# IP address of the device hosting the MQTT broker
MQTT_BROKER=b''
# Port on which the MQTT broker is listening on (default: 1883)
MQTT_PORT=1883
# Credentials
MQTT_USER=''
MQTT_PASSWORD=''" > esp_32/lib/secrets.py
echo -e "# Name of your wifi network
WIFI_SSID=''
# Password for your network
WIFI_PASSWORD=''
# Array of authorized id's belonging to the RFID cards that can defuse the system
RFID_AUTHORIZED=[
]
# ID of the alarm device that will be used in the system
DEVICE_ID=b''
# ID of the cam device associated with this device
CAM_ID=b''
# IP address of the device hosting the MQTT broker
MQTT_BROKER=b''
# Port on which the MQTT broker is listening on (default: 1883)
MQTT_PORT=1883
# Credentials
MQTT_USER=''
MQTT_PASSWORD=''" > esp_32/lib/secrets.py
echo -e "# Uses the docker network feature for automatic dns resolution, you don't need to change this
MQTT_HOST=mosquitto
# Port on which the MQTT broker is listening on (default: 1883)
MQTT_PORT=1883
# Keep alive value for the MQTT connection (default: 120)
MQTT_KEEPALIVE=120
# Credentials for Mosquitto broker
MQTT_USER=
MQTT_PASSWORD=
# Uses docker network for automatic dns resolution, you don't need to change this
HTTP_HOST=cat_proof_alarm
# The webserver will listen on this port (default: 5000)
HTTP_PORT=5000
# The memory address of the I2C device (use i2cdetect to find it, default: 0x3c)
I2C_ADDR=0x3c
# Accuracy threshold on pet detection to disable the alarm
YOLO_THRESHOLD=" > orange_pi_zero_2w/.env
touch orange_pi_zero_2w/controller/.authfile
echo "admin:$7$101$NBZcAb+v3xOjrRoR$lub+0XOCLjlgXK76KguA9SnfveJ1AoXcriMKrwEtYqFUIEGsyZMOB3xqw1mGZ0vLHOhBgjhUNJpdfbv0Um4DVg==" > orange_pi_zero_2w/mosquitto/passwd