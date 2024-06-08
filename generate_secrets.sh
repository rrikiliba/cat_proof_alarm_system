#!/bin/bash
echo -e "WIFI_SSID=''\n
        WIFI_PASSWORD=''\n
        DEVICE_ID=b''\n
        MQTT_BROKER=b''\n
        MQTT_PORT=1883" > esp_32/lib/secrets.py
echo -e "WIFI_SSID=''\n
        WIFI_PASSWORD=''\n
        RFID_AUTHORIZED=[\n
        ]\n
        DEVICE_ID=b''\n
        CAM_ID=b''\n
        MQTT_BROKER=b''\n
        MQTT_PORT=1883" > esp_32/lib/secrets.py
echo -e "MQTT_HOST=mosquitto  #uses docker network for automatic dns resolution, you don't need to change this\n
        MQTT_PORT=\n
        MQTT_KEEPALIVE=\n

        HTTP_HOST=alarm_server  #uses docker network for automatic dns resolution, you don't need to change this\n
        HTTP_PORT=" > orange_pi_zero_2w/.env