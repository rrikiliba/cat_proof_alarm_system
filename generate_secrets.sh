#!/bin/bash
echo -e "# Name of your wifi network\n
        WIFI_SSID=''\n
        # Password for your network\n
        WIFI_PASSWORD=''\n
        # ID of the cam device that will be used in the system\n
        DEVICE_ID=b''\n
        # IP address of the device hosting the MQTT broker\n
        MQTT_BROKER=b''\n
        # Port on which the MQTT broker is listening on (default: 1883)\n
        MQTT_PORT=1883\n
        # Credentials\n
        MQTT_USER=''\n
        MQTT_PASSWORD=''" > esp_32/lib/secrets.py
echo -e "# Name of your wifi network\n
        WIFI_SSID=''\n
        # Password for your network\n
        WIFI_PASSWORD=''\n
        # Array of authorized id's belonging to the RFID cards that can defuse the system\n
        RFID_AUTHORIZED=[\n
        ]\n
        # ID of the alarm device that will be used in the system\n
        DEVICE_ID=b''\n
        # ID of the cam device associated with this device\n
        CAM_ID=b''\n
        # IP address of the device hosting the MQTT broker\n
        MQTT_BROKER=b''\n
        # Port on which the MQTT broker is listening on (default: 1883)\n
        MQTT_PORT=1883\n
        # Credentials\n
        MQTT_USER=''\n
        MQTT_PASSWORD=''" > esp_32/lib/secrets.py
echo -e "# Uses the docker network feature for automatic dns resolution, you don't need to change this\n
        MQTT_HOST=mosquitto\n
        # Port on which the MQTT broker is listening on (default: 1883)\n
        MQTT_PORT=1883\n
        # Keep alive value for the MQTT connection (default: 60)
        MQTT_KEEPALIVE=60\n
        # Credentials for Mosquitto broker\n
        MQTT_USER=\n
        MQTT_PASSWORD=\n
        # Uses docker network for automatic dns resolution, you don't need to change this\n
        HTTP_HOST=cat_proof_alarm\n
        # The webserver will listen on this port
        HTTP_PORT=\n
        # The memory address of the I2C device (use i2cdetect to find it)\n
        I2C_ADDR=" > orange_pi_zero_2w/.env
touch orange_pi_zero_2w/controller/.authfile
echo "admin:$7$101$NBZcAb+v3xOjrRoR$lub+0XOCLjlgXK76KguA9SnfveJ1AoXcriMKrwEtYqFUIEGsyZMOB3xqw1mGZ0vLHOhBgjhUNJpdfbv0Um4DVg==" > orange_pi_zero_2w/mosquitto/passwd