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
        MQTT_PORT=1883" > esp_32/lib/secrets.py
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
        MQTT_PORT=1883" > esp_32/lib/secrets.py
echo -e "# Uses the docker network feature for automatic dns resolution, you don't need to change this\n
        MQTT_HOST=mosquitto\n
        # Port on which the MQTT broker is listening on (default: 1883)\n
        MQTT_PORT=1883\n
        # Keep alive value for the MQTT connection (default: 60)
        MQTT_KEEPALIVE=60\n
        #uses docker network for automatic dns resolution, you don't need to change this\n
        HTTP_HOST=cat_proof_alarm\n
        HTTP_PORT=" > orange_pi_zero_2w/.env
touch orange_pi_zero_2w/.authfile